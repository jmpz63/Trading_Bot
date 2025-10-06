"""
Enhanced Risk Manager with Fee-Aware Position Sizing
Addresses the issues identified in the trading bot performance
"""

from typing import Dict, Optional, List
import logging
import math

class EnhancedRiskManager:
    """
    Enhanced risk management with fee awareness and better position sizing
    """
    
    def __init__(self, config: Dict):
        """Initialize enhanced risk manager"""
        self.config = config.get('risk_management', {})
        self.logger = logging.getLogger(__name__)
        
        # Enhanced risk parameters
        self.max_portfolio_risk = self.config.get('max_portfolio_risk', 0.02)
        self.min_position_value = self.config.get('min_position_value', 50.0)  # Minimum $50
        self.max_position_size = self.config.get('max_position_size', 0.25)  # 25% max
        self.fee_rate = self.config.get('fee_rate', 0.0016)  # 0.16% taker fee
        self.min_profit_target = self.config.get('min_profit_target', 0.005)  # 0.5% minimum
        self.max_spread_tolerance = self.config.get('max_spread_tolerance', 0.001)  # 0.1%
        
        # Trade tracking
        self.recent_trades: List[Dict] = []
        self.daily_trade_limit = self.config.get('daily_trade_limit', 20)  # Reduce overtrading
        self.win_rate_threshold = self.config.get('win_rate_threshold', 0.3)  # 30% minimum
        
    async def validate_trade(self, signal: Dict, portfolio_value: float, 
                           current_positions: Dict) -> Dict:
        """
        Enhanced trade validation with fee awareness
        
        Returns:
            Dict with 'approved', 'reason', 'adjusted_quantity', 'risk_metrics'
        """
        try:
            result = {
                'approved': False,
                'reason': '',
                'adjusted_quantity': 0.0,
                'risk_metrics': {}
            }
            
            # Check recent performance
            if not self._check_performance_threshold():
                result['reason'] = 'Performance below threshold - reducing activity'
                return result
            
            # Check daily trade limit
            if not self._check_daily_limit():
                result['reason'] = f'Daily limit of {self.daily_trade_limit} trades reached'
                return result
            
            # Check spread tolerance
            if not self._check_spread_tolerance(signal):
                result['reason'] = f"Spread too wide: {signal.get('spread_pct', 0):.4f}"
                return result
            
            # Calculate fee-aware position size
            adjusted_quantity = self._calculate_fee_aware_position_size(
                signal, portfolio_value
            )
            
            if adjusted_quantity <= 0:
                result['reason'] = 'Position size too small after fee adjustment'
                return result
            
            # Check minimum position value
            position_value = adjusted_quantity * signal['price']
            if position_value < self.min_position_value:
                result['reason'] = f'Position value ${position_value:.2f} below minimum ${self.min_position_value}'
                return result
            
            # Check if trade can be profitable after fees
            if not self._check_profitability_potential(signal, adjusted_quantity):
                result['reason'] = 'Trade unlikely to be profitable after fees'
                return result
            
            # All checks passed
            result.update({
                'approved': True,
                'reason': 'Trade approved',
                'adjusted_quantity': adjusted_quantity,
                'risk_metrics': self._calculate_risk_metrics(signal, adjusted_quantity, portfolio_value)
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error validating trade: {e}")
            return {'approved': False, 'reason': f'Validation error: {str(e)}'}
    
    def _check_performance_threshold(self) -> bool:
        """Check if recent performance meets minimum threshold"""
        if len(self.recent_trades) < 10:
            return True  # Not enough data yet
        
        # Calculate recent win rate
        recent_wins = sum(1 for trade in self.recent_trades[-20:] if trade.get('pnl', 0) > 0)
        recent_win_rate = recent_wins / min(len(self.recent_trades), 20)
        
        # If win rate is too low, be more conservative
        if recent_win_rate < self.win_rate_threshold:
            # Only trade with very high confidence signals
            return False
        
        return True
    
    def _check_daily_limit(self) -> bool:
        """Check daily trading limit"""
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        today_trades = sum(
            1 for trade in self.recent_trades 
            if trade.get('timestamp', datetime.min).date() == today
        )
        
        return today_trades < self.daily_trade_limit
    
    def _check_spread_tolerance(self, signal: Dict) -> bool:
        """Check if spread is within tolerance"""
        spread_pct = signal.get('spread_pct', 0)
        return spread_pct <= self.max_spread_tolerance
    
    def _calculate_fee_aware_position_size(self, signal: Dict, portfolio_value: float) -> float:
        """
        Calculate position size that accounts for fees and minimum profit
        """
        # Base position size (percentage of portfolio)
        base_position_pct = min(
            self.max_position_size,
            signal.get('confidence', 0.5) * self.max_position_size * 2
        )
        
        base_position_value = portfolio_value * base_position_pct
        
        # Adjust for minimum position value
        position_value = max(base_position_value, self.min_position_value)
        
        # Don't exceed portfolio limits
        position_value = min(position_value, portfolio_value * self.max_position_size)
        
        # Calculate quantity
        price = signal['price']
        quantity = position_value / price
        
        # Round to appropriate precision for exchange
        quantity = self._round_to_precision(quantity, signal.get('symbol', 'BTCUSD'))
        
        return quantity
    
    def _check_profitability_potential(self, signal: Dict, quantity: float) -> bool:
        """
        Check if trade has potential to be profitable after fees
        """
        position_value = quantity * signal['price']
        
        # Calculate total fees (entry + exit)
        total_fees = position_value * self.fee_rate * 2
        
        # Minimum price movement needed to cover fees + minimum profit
        min_price_move_pct = (total_fees / position_value) + self.min_profit_target
        
        # Check if signal confidence suggests this move is likely
        confidence = signal.get('confidence', 0)
        expected_move = confidence * 0.02  # Assume max 2% move for high confidence
        
        return expected_move > min_price_move_pct
    
    def _round_to_precision(self, quantity: float, symbol: str) -> float:
        """Round quantity to exchange precision"""
        # BTC precision is typically 8 decimal places
        if 'BTC' in symbol.upper():
            return round(quantity, 8)
        
        # Default to 6 decimal places
        return round(quantity, 6)
    
    def _calculate_risk_metrics(self, signal: Dict, quantity: float, portfolio_value: float) -> Dict:
        """Calculate risk metrics for the trade"""
        position_value = quantity * signal['price']
        position_pct = position_value / portfolio_value
        
        # Estimate potential loss (assuming 2% stop loss)
        potential_loss = position_value * 0.02
        portfolio_risk_pct = potential_loss / portfolio_value
        
        return {
            'position_value': position_value,
            'position_pct': position_pct,
            'potential_loss': potential_loss,
            'portfolio_risk_pct': portfolio_risk_pct,
            'estimated_fees': position_value * self.fee_rate * 2,
            'min_profit_needed': position_value * self.min_profit_target
        }
    
    def record_trade(self, trade_result: Dict):
        """Record trade result for performance tracking"""
        self.recent_trades.append({
            'timestamp': trade_result.get('timestamp'),
            'symbol': trade_result.get('symbol'),
            'action': trade_result.get('action'),
            'quantity': trade_result.get('quantity'),
            'price': trade_result.get('price'),
            'pnl': trade_result.get('pnl', 0),
            'fees': trade_result.get('fees', 0)
        })
        
        # Keep only recent trades (last 100)
        if len(self.recent_trades) > 100:
            self.recent_trades = self.recent_trades[-100:]
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary and recommendations"""
        if not self.recent_trades:
            return {'status': 'No trades recorded'}
        
        # Calculate metrics
        total_trades = len(self.recent_trades)
        winning_trades = sum(1 for t in self.recent_trades if t.get('pnl', 0) > 0)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        total_pnl = sum(t.get('pnl', 0) for t in self.recent_trades)
        total_fees = sum(t.get('fees', 0) for t in self.recent_trades)
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_fees': total_fees,
            'net_pnl': total_pnl - total_fees,
            'avg_trade': total_pnl / total_trades if total_trades > 0 else 0,
            'recommendation': self._get_recommendation(win_rate, total_pnl)
        }
    
    def _get_recommendation(self, win_rate: float, total_pnl: float) -> str:
        """Get trading recommendation based on performance"""
        if win_rate < 0.2:
            return "STOP: Win rate critically low. Review strategy immediately."
        elif win_rate < 0.3:
            return "CAUTION: Reduce position sizes and review strategy."
        elif total_pnl < 0 and win_rate < 0.4:
            return "REVIEW: Strategy needs adjustment."
        else:
            return "CONTINUE: Performance within acceptable range."