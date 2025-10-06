"""
Spread-Aware Order Manager
Handles intelligent order placement to minimize spread costs
"""

import asyncio
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from enum import Enum

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    SMART_LIMIT = "smart_limit"  # Our intelligent limit order

class SpreadAwareOrderManager:
    """
    Order manager that minimizes spread costs through intelligent order placement
    """
    
    def __init__(self, config: Dict):
        self.config = config.get('order_management', {})
        self.logger = logging.getLogger(__name__)
        
        # Order parameters
        self.max_spread_pct = self.config.get('max_spread_pct', 0.001)  # 0.1%
        self.limit_offset_pct = self.config.get('limit_offset_pct', 0.0005)  # 0.05%
        self.order_timeout = self.config.get('order_timeout_seconds', 30)
        self.retry_attempts = self.config.get('retry_attempts', 3)
        
        # Spread analysis
        self.recent_spreads: List[float] = []
        self.avg_spread = 0.0
        
    async def execute_smart_order(self, signal: Dict, exchange_client) -> Dict:
        """
        Execute order with intelligent spread management
        
        Returns:
            Dict with execution results
        """
        try:
            # Analyze current market conditions
            market_info = await self._get_market_info(signal['symbol'], exchange_client)
            
            if not market_info['can_trade']:
                return {
                    'success': False,
                    'reason': market_info['reason'],
                    'order_id': None
                }
            
            # Determine best order strategy
            order_strategy = self._choose_order_strategy(market_info, signal)
            
            # Execute order based on strategy
            if order_strategy == OrderType.MARKET:
                return await self._execute_market_order(signal, exchange_client, market_info)
            elif order_strategy == OrderType.SMART_LIMIT:
                return await self._execute_smart_limit_order(signal, exchange_client, market_info)
            else:
                return await self._execute_limit_order(signal, exchange_client, market_info)
                
        except Exception as e:
            self.logger.error(f"Error executing smart order: {e}")
            return {
                'success': False,
                'reason': f'Execution error: {str(e)}',
                'order_id': None
            }
    
    async def _get_market_info(self, symbol: str, exchange_client) -> Dict:
        """Get current market information for smart order placement"""
        try:
            # Get order book
            orderbook = await exchange_client.fetch_order_book(symbol)
            
            if not orderbook['bids'] or not orderbook['asks']:
                return {
                    'can_trade': False,
                    'reason': 'Empty order book',
                    'bid': 0,
                    'ask': 0,
                    'spread_pct': 1.0
                }
            
            bid = orderbook['bids'][0][0]
            ask = orderbook['asks'][0][0]
            spread_pct = (ask - bid) / bid if bid > 0 else 1.0
            
            # Update spread tracking
            self._update_spread_stats(spread_pct)
            
            # Check if market is tradeable
            can_trade = spread_pct <= self.max_spread_pct
            reason = "Market conditions acceptable" if can_trade else f"Spread too wide: {spread_pct:.4f}"
            
            return {
                'can_trade': can_trade,
                'reason': reason,
                'bid': bid,
                'ask': ask,
                'spread_pct': spread_pct,
                'mid_price': (bid + ask) / 2,
                'orderbook': orderbook
            }
            
        except Exception as e:
            self.logger.error(f"Error getting market info: {e}")
            return {
                'can_trade': False,
                'reason': f'Market data error: {str(e)}',
                'bid': 0,
                'ask': 0,
                'spread_pct': 1.0
            }
    
    def _choose_order_strategy(self, market_info: Dict, signal: Dict) -> OrderType:
        """Choose the best order strategy based on market conditions"""
        
        spread_pct = market_info['spread_pct']
        confidence = signal.get('confidence', 0.5)
        
        # Use market orders for high confidence + tight spreads
        if confidence > 0.8 and spread_pct < self.avg_spread * 0.8:
            return OrderType.MARKET
        
        # Use smart limits for normal conditions
        elif spread_pct < self.max_spread_pct:
            return OrderType.SMART_LIMIT
        
        # Use regular limits for wide spreads
        else:
            return OrderType.LIMIT
    
    async def _execute_market_order(self, signal: Dict, exchange_client, market_info: Dict) -> Dict:
        """Execute market order for immediate execution"""
        try:
            symbol = signal['symbol']
            side = 'buy' if signal['action'] == 'BUY' else 'sell'
            quantity = signal['quantity']
            
            # Use market price
            price = market_info['ask'] if side == 'buy' else market_info['bid']
            
            order = await exchange_client.create_order(
                symbol=symbol,
                type='market',
                side=side,
                amount=quantity
            )
            
            return {
                'success': True,
                'order_id': order.get('id'),
                'price': price,
                'quantity': quantity,
                'strategy': 'MARKET',
                'spread_cost': market_info['spread_pct'] * price * quantity
            }
            
        except Exception as e:
            self.logger.error(f"Market order failed: {e}")
            return {'success': False, 'reason': str(e)}
    
    async def _execute_smart_limit_order(self, signal: Dict, exchange_client, market_info: Dict) -> Dict:
        """Execute smart limit order with adaptive pricing"""
        try:
            symbol = signal['symbol']
            side = 'buy' if signal['action'] == 'BUY' else 'sell'
            quantity = signal['quantity']
            
            # Calculate smart limit price
            if side == 'buy':
                # Place buy order slightly above bid to increase fill probability
                base_price = market_info['bid']
                limit_price = base_price * (1 + self.limit_offset_pct)
                # Don't pay more than mid-price
                limit_price = min(limit_price, market_info['mid_price'])
            else:
                # Place sell order slightly below ask
                base_price = market_info['ask']
                limit_price = base_price * (1 - self.limit_offset_pct)
                # Don't sell below mid-price
                limit_price = max(limit_price, market_info['mid_price'])
            
            # Place initial order
            order = await exchange_client.create_order(
                symbol=symbol,
                type='limit',
                side=side,
                amount=quantity,
                price=limit_price
            )
            
            # Monitor and adjust if needed
            final_result = await self._monitor_and_adjust_order(
                order, signal, exchange_client, market_info
            )
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"Smart limit order failed: {e}")
            return {'success': False, 'reason': str(e)}
    
    async def _execute_limit_order(self, signal: Dict, exchange_client, market_info: Dict) -> Dict:
        """Execute conservative limit order"""
        try:
            symbol = signal['symbol']
            side = 'buy' if signal['action'] == 'BUY' else 'sell'
            quantity = signal['quantity']
            
            # Use conservative limit pricing
            if side == 'buy':
                limit_price = market_info['bid']  # Buy at bid
            else:
                limit_price = market_info['ask']  # Sell at ask
            
            order = await exchange_client.create_order(
                symbol=symbol,
                type='limit',
                side=side,
                amount=quantity,
                price=limit_price
            )
            
            return {
                'success': True,
                'order_id': order.get('id'),
                'price': limit_price,
                'quantity': quantity,
                'strategy': 'LIMIT_CONSERVATIVE'
            }
            
        except Exception as e:
            self.logger.error(f"Limit order failed: {e}")
            return {'success': False, 'reason': str(e)}
    
    async def _monitor_and_adjust_order(self, initial_order: Dict, signal: Dict, 
                                      exchange_client, market_info: Dict) -> Dict:
        """Monitor order and adjust price if needed"""
        
        order_id = initial_order.get('id')
        symbol = signal['symbol']
        start_time = datetime.now()
        
        for attempt in range(self.retry_attempts):
            # Wait a bit for order to fill
            await asyncio.sleep(5)
            
            # Check order status
            try:
                order_status = await exchange_client.fetch_order(order_id, symbol)
                
                if order_status['status'] == 'closed':
                    # Order filled successfully
                    return {
                        'success': True,
                        'order_id': order_id,
                        'price': order_status['average'] or order_status['price'],
                        'quantity': order_status['filled'],
                        'strategy': 'SMART_LIMIT_FILLED'
                    }
                
                # Check if we should adjust price
                if datetime.now() - start_time > timedelta(seconds=self.order_timeout):
                    # Cancel and retry with more aggressive pricing
                    await exchange_client.cancel_order(order_id, symbol)
                    
                    # Try market order as fallback
                    return await self._execute_market_order(signal, exchange_client, market_info)
                    
            except Exception as e:
                self.logger.warning(f"Error monitoring order: {e}")
                continue
        
        # If we get here, order didn't fill and retries exhausted
        try:
            await exchange_client.cancel_order(order_id, symbol)
        except:
            pass
        
        return {
            'success': False,
            'reason': 'Order timeout - could not fill within acceptable parameters'
        }
    
    def _update_spread_stats(self, spread_pct: float):
        """Update spread statistics for better decision making"""
        self.recent_spreads.append(spread_pct)
        
        # Keep only recent spreads (last 50)
        if len(self.recent_spreads) > 50:
            self.recent_spreads = self.recent_spreads[-50:]
        
        # Calculate rolling average
        if self.recent_spreads:
            self.avg_spread = sum(self.recent_spreads) / len(self.recent_spreads)
    
    def get_spread_analysis(self) -> Dict:
        """Get current spread analysis"""
        if not self.recent_spreads:
            return {'status': 'No data available'}
        
        return {
            'current_avg_spread': self.avg_spread,
            'min_spread': min(self.recent_spreads),
            'max_spread': max(self.recent_spreads),
            'spread_samples': len(self.recent_spreads),
            'recommended_strategy': self._recommend_strategy()
        }
    
    def _recommend_strategy(self) -> str:
        """Recommend order strategy based on recent spread analysis"""
        if not self.recent_spreads:
            return "Insufficient data"
        
        if self.avg_spread < 0.0005:  # 0.05%
            return "Market orders recommended - tight spreads"
        elif self.avg_spread < 0.001:  # 0.1%
            return "Smart limit orders recommended"
        else:
            return "Conservative limit orders recommended - wide spreads"