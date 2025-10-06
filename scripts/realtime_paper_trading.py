"""
Real-Time Paper Trading Bot - Uses Live Market Data
Connects to real exchanges for actual BTC prices and spreads
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

class RealTimePaperTradingBot:
    """
    Paper trading bot using real-time market data from exchanges
    """
    
    def __init__(self):
        # Trading state
        self.starting_balance = 1000.0
        self.current_balance = 1000.0
        self.btc_balance = 0.0
        
        # Strategy parameters
        self.daily_trade_limit = 15
        self.min_position_value = 75.0
        self.max_position_pct = 0.15  # 15% max position
        self.fee_rate = 0.0016
        self.max_spread_pct = 0.0008  # 0.08%
        self.cooldown_minutes = 15
        
        # Session tracking
        self.trades_today = 0
        self.trade_history = []
        self.last_trade_time = None
        self.session_start = datetime.now()
        self.is_running = True
        
        # Market data storage
        self.price_data = []
        self.current_price = 0.0
        self.current_bid = 0.0
        self.current_ask = 0.0
        self.current_spread_pct = 0.0
        
        # Technical indicators
        self.rsi_period = 14
        self.momentum_period = 10
        
    async def start_real_time_trading(self, duration_minutes: int = 60):
        """Start real-time paper trading"""
        
        print("🚀 REAL-TIME PAPER TRADING BOT")
        print("="*50)
        print(f"💰 Starting Balance: ${self.starting_balance:,.2f}")
        print(f"📡 Data Source: Live Kraken BTC/USD")
        print(f"⏱️  Duration: {duration_minutes} minutes")
        print("="*50)
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            try:
                while datetime.now() < end_time and self.is_running:
                    # Fetch real market data
                    success = await self._fetch_real_market_data()
                    
                    if success:
                        # Update technical indicators
                        self._calculate_indicators()
                        
                        # Check for trading opportunities
                        await self._check_trading_opportunity()
                        
                        # Display status more frequently
                        if len(self.price_data) % 3 == 0:  # Every 3rd update (~30 seconds)
                            self._display_status()
                        elif len(self.price_data) % 1 == 0:  # Show price every update
                            self._display_brief_status()
                    else:
                        print("⚠️  Failed to fetch market data, retrying...")
                    
                    # Check stop conditions
                    if self._should_stop_trading():
                        break
                    
                    # Wait 10 seconds between updates
                    await asyncio.sleep(10)
                    
            except KeyboardInterrupt:
                print("\n⏹️  Real-time trading stopped by user")
            except Exception as e:
                print(f"\n❌ Error in real-time trading: {e}")
        
        self._display_final_results()
    
    async def _fetch_real_market_data(self) -> bool:
        """Fetch real-time data from Kraken API"""
        
        try:
            # Kraken public API for BTC/USD ticker
            url = "https://api.kraken.com/0/public/Ticker?pair=XBTUSD"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'result' in data and 'XXBTZUSD' in data['result']:
                        ticker = data['result']['XXBTZUSD']
                        
                        # Extract price data
                        self.current_ask = float(ticker['a'][0])  # Ask price
                        self.current_bid = float(ticker['b'][0])  # Bid price
                        self.current_price = (self.current_ask + self.current_bid) / 2  # Mid price
                        
                        # Calculate spread
                        self.current_spread_pct = (self.current_ask - self.current_bid) / self.current_bid
                        
                        # Store price data for technical analysis
                        price_point = {
                            'timestamp': datetime.now(),
                            'price': self.current_price,
                            'bid': self.current_bid,
                            'ask': self.current_ask,
                            'spread_pct': self.current_spread_pct,
                            'high': float(ticker['h'][1]),  # 24h high
                            'low': float(ticker['l'][1]),   # 24h low
                            'volume': float(ticker['v'][1])  # 24h volume
                        }
                        
                        self.price_data.append(price_point)
                        
                        # Keep only recent data (last 100 points)
                        if len(self.price_data) > 100:
                            self.price_data = self.price_data[-100:]
                        
                        return True
                    else:
                        print(f"❌ Invalid response format: {data}")
                        return False
                else:
                    print(f"❌ HTTP error {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error fetching market data: {e}")
            return False
    
    def _calculate_indicators(self):
        """Calculate technical indicators from real price data"""
        
        if len(self.price_data) < self.rsi_period:
            return
        
        # Extract price series
        prices = [p['price'] for p in self.price_data]
        
        # Calculate RSI
        self.current_rsi = self._calculate_rsi(prices)
        
        # Calculate momentum
        if len(prices) >= self.momentum_period:
            self.current_momentum = (prices[-1] / prices[-self.momentum_period] - 1) * 100
        else:
            self.current_momentum = 0
        
        # Calculate simple moving averages
        if len(prices) >= 20:
            self.sma_20 = sum(prices[-20:]) / 20
            self.price_vs_sma = (prices[-1] / self.sma_20 - 1) * 100
        else:
            self.sma_20 = prices[-1]
            self.price_vs_sma = 0
    
    def _calculate_rsi(self, prices: List[float]) -> float:
        """Calculate RSI from price data"""
        
        if len(prices) < self.rsi_period + 1:
            return 50.0
        
        # Calculate price changes
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # Separate gains and losses
        gains = [change if change > 0 else 0 for change in changes[-self.rsi_period:]]
        losses = [-change if change < 0 else 0 for change in changes[-self.rsi_period:]]
        
        # Calculate average gain and loss
        avg_gain = sum(gains) / self.rsi_period if gains else 0.01
        avg_loss = sum(losses) / self.rsi_period if losses else 0.01
        
        # Calculate RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    async def _check_trading_opportunity(self):
        """Check for trading opportunities using real market data"""
        
        if len(self.price_data) < 20:  # Need enough data
            return
        
        # Check cooldown
        if self.last_trade_time:
            time_since_last = datetime.now() - self.last_trade_time
            if time_since_last.total_seconds() < self.cooldown_minutes * 60:
                return
        
        # Check daily limit
        if self.trades_today >= self.daily_trade_limit:
            return
        
        # Check spread tolerance
        if self.current_spread_pct > self.max_spread_pct:
            return
        
        # Generate signal based on real data
        signal = self._analyze_real_market_conditions()
        
        if signal['action'] != 'HOLD':
            await self._execute_paper_trade(signal)
    
    def _analyze_real_market_conditions(self) -> Dict:
        """Analyze real market conditions for trading signals"""
        
        buy_conditions = []
        sell_conditions = []
        
        # RSI analysis
        if hasattr(self, 'current_rsi'):
            if self.current_rsi < 25:
                buy_conditions.append('RSI_EXTREMELY_OVERSOLD')
            elif self.current_rsi < 30:
                buy_conditions.append('RSI_OVERSOLD')
            elif self.current_rsi > 75:
                sell_conditions.append('RSI_EXTREMELY_OVERBOUGHT')
            elif self.current_rsi > 70:
                sell_conditions.append('RSI_OVERBOUGHT')
        
        # Momentum analysis
        if hasattr(self, 'current_momentum'):
            if self.current_momentum > 2.0:
                buy_conditions.append('STRONG_MOMENTUM')
            elif self.current_momentum > 0.5:
                buy_conditions.append('POSITIVE_MOMENTUM')
            elif self.current_momentum < -2.0:
                sell_conditions.append('STRONG_NEGATIVE_MOMENTUM')
            elif self.current_momentum < -0.5:
                sell_conditions.append('NEGATIVE_MOMENTUM')
        
        # Price vs SMA analysis
        if hasattr(self, 'price_vs_sma'):
            if self.price_vs_sma < -2.0:  # More than 2% below SMA
                buy_conditions.append('BELOW_SMA_SUPPORT')
            elif self.price_vs_sma > 2.0:  # More than 2% above SMA
                sell_conditions.append('ABOVE_SMA_RESISTANCE')
        
        # Volume analysis (using 24h volume data)
        if len(self.price_data) >= 2:
            current_vol = self.price_data[-1]['volume']
            prev_vol = self.price_data[-2]['volume']
            
            if current_vol > prev_vol * 1.5:  # 50% volume increase
                if buy_conditions:
                    buy_conditions.append('HIGH_VOLUME')
                if sell_conditions:
                    sell_conditions.append('HIGH_VOLUME')
        
        # Spread quality (tighter spread = better conditions)
        if self.current_spread_pct < 0.0004:  # Very tight spread
            if buy_conditions:
                buy_conditions.append('TIGHT_SPREAD')
            if sell_conditions:
                sell_conditions.append('TIGHT_SPREAD')
        
        # Price action confirmation
        if len(self.price_data) >= 5:
            recent_prices = [p['price'] for p in self.price_data[-5:]]
            if all(recent_prices[i] <= recent_prices[i+1] for i in range(4)):  # Rising trend
                buy_conditions.append('RISING_TREND')
            elif all(recent_prices[i] >= recent_prices[i+1] for i in range(4)):  # Falling trend
                sell_conditions.append('FALLING_TREND')
        
        # Decision logic - need 4+ strong conditions
        min_conditions = 4
        
        if len(buy_conditions) >= min_conditions and self.btc_balance == 0:
            return {
                'action': 'BUY',
                'confidence': min(len(buy_conditions) / 6.0, 1.0),
                'conditions': buy_conditions,
                'price': self.current_ask,  # Buy at ask
                'spread_pct': self.current_spread_pct
            }
        elif len(sell_conditions) >= min_conditions and self.btc_balance > 0:
            return {
                'action': 'SELL',
                'confidence': min(len(sell_conditions) / 6.0, 1.0),
                'conditions': sell_conditions,
                'price': self.current_bid,  # Sell at bid
                'spread_pct': self.current_spread_pct
            }
        
        return {'action': 'HOLD', 'confidence': 0}
    
    async def _execute_paper_trade(self, signal: Dict):
        """Execute paper trade with real market prices"""
        
        action = signal['action']
        price = signal['price']
        confidence = signal['confidence']
        
        # Calculate position size
        portfolio_value = self.current_balance + (self.btc_balance * self.current_price)
        position_pct = min(0.12 * confidence, self.max_position_pct)  # Scale with confidence
        position_value = max(portfolio_value * position_pct, self.min_position_value)
        position_value = min(position_value, self.current_balance * 0.9)
        
        if action == 'BUY':
            quantity = position_value / price
            
            if position_value > self.current_balance:
                return
            
            # Execute buy
            self.current_balance -= position_value
            self.btc_balance += quantity
            fee = position_value * self.fee_rate
            self.current_balance -= fee
            
        else:  # SELL
            quantity = self.btc_balance
            proceeds = quantity * price
            
            # Execute sell
            self.current_balance += proceeds
            self.btc_balance = 0.0
            fee = proceeds * self.fee_rate
            self.current_balance -= fee
            position_value = proceeds
        
        # Record trade
        trade = {
            'timestamp': datetime.now(),
            'action': action,
            'quantity': quantity,
            'price': price,
            'value': position_value,
            'fee': fee,
            'confidence': confidence,
            'conditions': signal.get('conditions', []),
            'rsi': getattr(self, 'current_rsi', 50),
            'momentum': getattr(self, 'current_momentum', 0),
            'spread_pct': signal['spread_pct']
        }
        
        self.trade_history.append(trade)
        self.trades_today += 1
        self.last_trade_time = datetime.now()
        
        # Display trade
        print(f"\n{'🟢 BUY' if action == 'BUY' else '🔴 SELL'}: {quantity:.8f} BTC @ ${price:,.2f}")
        print(f"💰 Value: ${position_value:.2f} | Fee: ${fee:.2f} | Confidence: {confidence:.2f}")
        print(f"🎯 Conditions: {', '.join(signal.get('conditions', []))}")
        print(f"📊 RSI: {getattr(self, 'current_rsi', 50):.0f} | Momentum: {getattr(self, 'current_momentum', 0):.1f}%")
    
    def _display_status(self):
        """Display current trading status"""
        
        portfolio_value = self.current_balance + (self.btc_balance * self.current_price)
        total_return = portfolio_value - self.starting_balance
        return_pct = (total_return / self.starting_balance) * 100
        
        # Show current time
        current_time = datetime.now().strftime('%H:%M:%S')
        
        print(f"\n⚡ REAL-TIME STATUS | {current_time} | BTC: ${self.current_price:,.0f}")
        print(f"💰 Portfolio: ${portfolio_value:.2f} | Return: ${total_return:+.2f} ({return_pct:+.1f}%)")
        print(f"💵 USD: ${self.current_balance:.2f} | ₿ BTC: {self.btc_balance:.8f}")
        print(f"📊 Bid: ${self.current_bid:,.0f} | Ask: ${self.current_ask:,.0f} | Spread: {self.current_spread_pct:.4f}")
        print(f"🎯 Trades: {self.trades_today}/{self.daily_trade_limit}")
        
        if hasattr(self, 'current_rsi'):
            print(f"📈 RSI: {self.current_rsi:.0f} | Momentum: {getattr(self, 'current_momentum', 0):.1f}%")
            
        # Show recent price movement
        if len(self.price_data) >= 5:
            recent_prices = [p['price'] for p in self.price_data[-5:]]
            price_change = recent_prices[-1] - recent_prices[0]
            change_pct = (price_change / recent_prices[0]) * 100
            trend = "📈" if price_change > 0 else "📉" if price_change < 0 else "➡️"
            print(f"{trend} 5min Change: ${price_change:+.0f} ({change_pct:+.2f}%)")
    
    def _display_brief_status(self):
        """Display brief status update"""
        
        portfolio_value = self.current_balance + (self.btc_balance * self.current_price)
        total_return = portfolio_value - self.starting_balance
        return_pct = (total_return / self.starting_balance) * 100
        
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # Show brief update
        print(f"⏱️  {current_time} | BTC: ${self.current_price:,.0f} | Portfolio: ${portfolio_value:.2f} ({return_pct:+.1f}%) | Spread: {self.current_spread_pct:.4f}")
    
    def _should_stop_trading(self) -> bool:
        """Check stop conditions"""
        
        portfolio_value = self.current_balance + (self.btc_balance * self.current_price)
        loss_pct = (self.starting_balance - portfolio_value) / self.starting_balance
        
        if loss_pct > 0.05:  # 5% loss limit
            print(f"\n🛑 STOP: Portfolio loss {loss_pct:.1%}")
            return True
        
        if self.trades_today >= self.daily_trade_limit:
            print(f"\n🏁 DAILY LIMIT: {self.trades_today} trades completed")
            return True
        
        return False
    
    def _display_final_results(self):
        """Display final results"""
        
        final_portfolio = self.current_balance + (self.btc_balance * self.current_price)
        total_return = final_portfolio - self.starting_balance
        return_pct = (total_return / self.starting_balance) * 100
        
        print(f"\n\n🏆 REAL-TIME PAPER TRADING RESULTS")
        print("="*55)
        print(f"💰 Starting Balance: ${self.starting_balance:,.2f}")
        print(f"💰 Final Portfolio: ${final_portfolio:.2f}")
        print(f"📊 Total Return: ${total_return:+.2f} ({return_pct:+.1f}%)")
        print(f"🎯 Trades Executed: {len(self.trade_history)}")
        print(f"📡 Data Source: Live Kraken BTC/USD market data")
        print("="*55)

async def main():
    """Main function"""
    print("📡 Real-Time Paper Trading Bot")
    print("Uses live market data from Kraken exchange")
    
    try:
        duration = int(input("\n⏱️  Enter duration in minutes (default 30): ") or "30")
    except:
        duration = 30
    
    bot = RealTimePaperTradingBot()
    await bot.start_real_time_trading(duration)

if __name__ == "__main__":
    asyncio.run(main())