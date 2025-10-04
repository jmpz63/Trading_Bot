"""
S&P 500 Market Data Integration
Extends trading bot for traditional stock market access
"""

import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import logging

class SP500MarketData:
    """
    S&P 500 and traditional stock market data provider
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # S&P 500 symbols and major ETFs
        self.sp500_symbols = [
            "SPY",   # SPDR S&P 500 ETF
            "VOO",   # Vanguard S&P 500 ETF  
            "IVV",   # iShares Core S&P 500 ETF
            "^GSPC", # S&P 500 Index
        ]
        
        # Major S&P 500 stocks
        self.major_stocks = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
            "META", "NVDA", "JPM", "JNJ", "V"
        ]
        
        self.data_cache = {}
        
    async def get_sp500_data(self, symbol: str = "SPY", period: str = "1d") -> pd.DataFrame:
        """
        Get S&P 500 data via Yahoo Finance
        
        Args:
            symbol: Stock symbol (SPY, VOO, ^GSPC, etc.)
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            self.logger.info(f"Retrieved {len(data)} data points for {symbol}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def get_real_time_price(self, symbol: str) -> Dict:
        """Get real-time price data for S&P 500 symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'price': info.get('currentPrice', 0),
                'change': info.get('regularMarketChange', 0),
                'change_percent': info.get('regularMarketChangePercent', 0),
                'volume': info.get('regularMarketVolume', 0),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get real-time data for {symbol}: {e}")
            return {}
    
    async def get_market_hours(self) -> Dict:
        """Check if US stock market is open"""
        try:
            # Get SPY info to check market status
            spy = yf.Ticker("SPY")
            info = spy.info
            
            return {
                'is_open': info.get('regularMarketTime', 0) > 0,
                'next_open': None,  # Would need additional logic
                'timezone': 'EST'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get market hours: {e}")
            return {'is_open': False}
    
    async def scan_sp500_opportunities(self) -> List[Dict]:
        """Scan S&P 500 for trading opportunities"""
        opportunities = []
        
        for symbol in self.major_stocks:
            try:
                price_data = await self.get_real_time_price(symbol)
                historical = await self.get_sp500_data(symbol, "5d")
                
                if not historical.empty and price_data:
                    # Simple momentum analysis
                    recent_avg = historical['Close'].tail(5).mean()
                    current_price = price_data['price']
                    
                    momentum = (current_price - recent_avg) / recent_avg * 100
                    
                    opportunities.append({
                        'symbol': symbol,
                        'price': current_price,
                        'momentum': momentum,
                        'volume': price_data['volume'],
                        'signal': 'BUY' if momentum > 2 else 'SELL' if momentum < -2 else 'HOLD'
                    })
                    
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol}: {e}")
                
        return sorted(opportunities, key=lambda x: abs(x['momentum']), reverse=True)


class SP500TradingInterface:
    """
    Trading interface for S&P 500 via brokers
    Note: This requires actual broker API integration
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.paper_trading = config.get('paper_trading', True)
        
    async def place_order(self, symbol: str, quantity: float, side: str, order_type: str = "market") -> Dict:
        """
        Place order for S&P 500 stocks
        
        Args:
            symbol: Stock symbol (AAPL, SPY, etc.)
            quantity: Number of shares
            side: 'buy' or 'sell'
            order_type: 'market', 'limit', 'stop'
        """
        
        if self.paper_trading:
            # Paper trading simulation
            self.logger.info(f"PAPER TRADE: {side.upper()} {quantity} shares of {symbol}")
            
            return {
                'order_id': f"paper_{datetime.now().timestamp()}",
                'symbol': symbol,
                'quantity': quantity,
                'side': side,
                'status': 'filled',
                'paper_trade': True
            }
        else:
            # Real trading would require broker API integration
            self.logger.warning("Real S&P 500 trading requires broker API setup")
            return {'error': 'Real trading not configured'}


# Integration example
class SP500Strategy:
    """
    Example S&P 500 trading strategy
    """
    
    def __init__(self):
        self.name = "SP500 Momentum Strategy"
        
    async def analyze(self, market_data: SP500MarketData) -> List[Dict]:
        """Analyze S&P 500 for trading signals"""
        
        # Get market opportunities
        opportunities = await market_data.scan_sp500_opportunities()
        
        signals = []
        
        for opp in opportunities:
            if opp['momentum'] > 3:  # Strong upward momentum
                signals.append({
                    'symbol': opp['symbol'],
                    'action': 'BUY',
                    'confidence': min(abs(opp['momentum']) / 10, 1.0),
                    'reason': f"Strong momentum: {opp['momentum']:.2f}%"
                })
            elif opp['momentum'] < -3:  # Strong downward momentum
                signals.append({
                    'symbol': opp['symbol'],
                    'action': 'SELL',
                    'confidence': min(abs(opp['momentum']) / 10, 1.0),
                    'reason': f"Negative momentum: {opp['momentum']:.2f}%"
                })
                
        return signals


# Example usage
async def main():
    """Example usage of S&P 500 integration"""
    
    config = {
        'paper_trading': True,
        'logging': {'level': 'INFO'}
    }
    
    # Initialize components
    market_data = SP500MarketData(config)
    trading_interface = SP500TradingInterface(config)
    strategy = SP500Strategy()
    
    # Get S&P 500 data
    spy_data = await market_data.get_sp500_data("SPY", "1mo")
    print(f"SPY data: {len(spy_data)} rows")
    
    # Get real-time price
    spy_price = await market_data.get_real_time_price("SPY")
    print(f"SPY current price: ${spy_price.get('price', 'N/A')}")
    
    # Analyze opportunities
    opportunities = await market_data.scan_sp500_opportunities()
    print(f"Found {len(opportunities)} opportunities")
    
    # Generate trading signals
    signals = await strategy.analyze(market_data)
    print(f"Generated {len(signals)} trading signals")
    
    for signal in signals:
        print(f"Signal: {signal['action']} {signal['symbol']} - {signal['reason']}")

if __name__ == "__main__":
    asyncio.run(main())