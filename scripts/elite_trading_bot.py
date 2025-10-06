"""
ELITE TRADING BOT - Consolidated Professional Version
Combines the WORKING realtime_paper_trading.py with enhanced features

✅ PROVEN FEATURES:
- Real Kraken API integration (WORKING)
- Paper trading with accurate spreads 
- Technical analysis (RSI, Momentum, SMA)
- Risk management with position sizing

🚀 ENHANCED FEATURES:
- Multi-factor signal confirmation
- Advanced risk management
- Better technical indicators
- Performance tracking
- 24/7 operational capability

Last Updated: October 6, 2025
Status: ACTIVE - Ready for 24/7 operation
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum
import statistics
import os
import sys

# Add parent directory to path for imports
sys.path.append('/home/arm1/Trade_Bot')
from apm_workflow import APMTradingWorkflow

class MarketRegime(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_vol"

@dataclass
class TradeSignal:
    action: str  # BUY, SELL, HOLD
    confidence: float  # 0.0 to 1.0
    factors: Dict[str, float]
    expected_return: float
    risk_score: float

class EliteTradingBot:
    """
    Elite paper trading bot with institutional-grade features
    Built on proven realtime_paper_trading.py foundation
    """
    
    def __init__(self):
        # Core trading parameters (proven working values)
        self.starting_balance = 1000.0
        self.current_balance = 1000.0
        self.btc_balance = 0.0
        
        # Strategy parameters (conservative proven settings)
        self.daily_trade_limit = 12
        self.min_position_value = 75.0
        self.max_position_pct = 0.15  # 15% max position
        self.fee_rate = 0.0016  # Kraken fee
        self.max_spread_pct = 0.0008  # 0.08% max spread
        self.cooldown_minutes = 15
        
        # Enhanced risk parameters
        self.max_daily_loss_pct = 0.05  # 5% max daily loss
        self.max_total_drawdown_pct = 0.15  # 15% max total drawdown
        self.volatility_lookback = 20
        
        # Technical indicator parameters
        self.rsi_period = 14
        self.momentum_period = 10
        self.sma_short = 10
        self.sma_long = 20
        self.bb_period = 20
        self.bb_std_dev = 2.0
        
        # Session tracking
        self.trades_today = 0
        self.trade_history = []
        self.last_trade_time = None
        self.session_start = datetime.now()
        self.is_running = True
        
        # Market data storage
        self.price_data = []
        self.return_data = []
        self.current_price = 0.0
        self.current_bid = 0.0
        self.current_ask = 0.0
        self.current_spread_pct = 0.0
        self.current_volume = 0.0
        
        # Technical indicators (current values)
        self.current_rsi = 50.0
        self.current_momentum = 0.0
        self.sma_short_value = 0.0
        self.sma_long_value = 0.0
        self.bb_upper = 0.0
        self.bb_middle = 0.0
        self.bb_lower = 0.0
        self.bb_position = 0.5
        self.current_volatility = 0.0
        self.current_regime = MarketRegime.RANGING
        
        # Performance tracking
        self.peak_balance = self.starting_balance
        self.max_drawdown = 0.0
        self.daily_start_balance = self.starting_balance
        self.win_count = 0
        self.loss_count = 0
        
        # Data logging
        self.log_file = f"data/logs/elite_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.ensure_log_directory()
        
        # APM Workflow integration
        self.apm_workflow = APMTradingWorkflow()
        self.session_start_time = time.time()
        
    def ensure_log_directory(self):
        """Create log directory if it doesn't exist"""
        os.makedirs("data/logs", exist_ok=True)
    
    async def start_elite_trading(self, duration_minutes: int = 1440):  # Default 24 hours
        """Start the elite trading system for long-term operation"""
        
        print("🚀 ELITE TRADING BOT - PROFESSIONAL EDITION")
        print("="*60)
        print(f"💰 Starting Capital: ${self.starting_balance:,.2f}")
        print(f"🎯 Strategy: Multi-factor momentum with risk management")
        print(f"📡 Data Source: Live Kraken BTC/USD")
        print(f"⏱️ Duration: {duration_minutes} minutes ({duration_minutes/60:.1f} hours)")
        print(f"🗂️ Logging to: {self.log_file}")
        print("="*60)
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            try:
                iteration = 0
                while datetime.now() < end_time and self.is_running:
                    iteration += 1
                    
                    # Fetch market data
                    success = await self._fetch_market_data()
                    
                    if success:
                        # Update all indicators
                        self._calculate_all_indicators()
                        
                        # Detect market regime
                        self._detect_market_regime()
                        
                        # Generate trading signal
                        signal = self._generate_elite_signal()
                        
                        # Execute trade if signal is strong
                        if signal.action != 'HOLD' and self._can_trade():
                            await self._execute_elite_trade(signal)
                        
                        # Log data every iteration
                        self._log_market_data(signal)
                        
                        # Display status every 12 iterations (1 minute)
                        if iteration % 12 == 0:
                            self._display_elite_status()
                        
                        # Check risk limits
                        if self._check_risk_limits():
                            print("🚨 Risk limits breached - stopping trading")
                            break
                    
                    # Check for new trading day (reset counters)
                    self._check_new_day()
                    
                    await asyncio.sleep(5)  # 5-second intervals
                    
            except KeyboardInterrupt:
                print("\n⏹️ Elite trading bot stopped by user")
            except Exception as e:
                print(f"\n❌ Critical error: {e}")
                
            finally:
                await self._generate_final_report()
                
                # Execute APM Workflow: Track → Learn → Document → Index → Push
                await self._execute_apm_workflow()
    
    async def _fetch_market_data(self) -> bool:
        """Fetch real-time data from Kraken API (proven working method)"""
        
        try:
            # Kraken public API for BTC/USD ticker
            url = "https://api.kraken.com/0/public/Ticker?pair=XBTUSD"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'result' in data and 'XXBTZUSD' in data['result']:
                        ticker = data['result']['XXBTZUSD']
                        
                        # Extract market data
                        self.current_bid = float(ticker['b'][0])
                        self.current_ask = float(ticker['a'][0])
                        self.current_price = (self.current_bid + self.current_ask) / 2
                        self.current_volume = float(ticker['v'][1])  # 24hr volume
                        
                        # Calculate spread
                        self.current_spread_pct = (self.current_ask - self.current_bid) / self.current_price
                        
                        # Store price data with timestamp
                        price_entry = {
                            'timestamp': datetime.now().isoformat(),
                            'price': self.current_price,
                            'bid': self.current_bid,
                            'ask': self.current_ask,
                            'spread_pct': self.current_spread_pct,
                            'volume': self.current_volume,
                            'high': float(ticker['h'][1]),
                            'low': float(ticker['l'][1])
                        }
                        
                        self.price_data.append(price_entry)
                        
                        # Keep only recent data for performance (last 500 points)
                        if len(self.price_data) > 500:
                            self.price_data = self.price_data[-200:]
                        
                        # Calculate returns for volatility
                        if len(self.price_data) >= 2:
                            prev_price = self.price_data[-2]['price']
                            return_pct = (self.current_price / prev_price) - 1
                            self.return_data.append(return_pct)
                            
                            # Keep return data manageable
                            if len(self.return_data) > 100:
                                self.return_data = self.return_data[-50:]
                        
                        return True
                        
        except Exception as e:
            print(f"❌ Error fetching market data: {e}")
        
        return False
    
    def _calculate_all_indicators(self):
        """Calculate all technical indicators from price data"""
        
        if len(self.price_data) < self.rsi_period:
            return
        
        # Extract price series
        prices = [p['price'] for p in self.price_data]
        
        # RSI calculation
        self.current_rsi = self._calculate_rsi(prices)
        
        # Momentum calculation
        if len(prices) >= self.momentum_period:
            self.current_momentum = (prices[-1] / prices[-self.momentum_period] - 1) * 100
        
        # Simple Moving Averages
        if len(prices) >= self.sma_long:
            self.sma_short_value = sum(prices[-self.sma_short:]) / self.sma_short
            self.sma_long_value = sum(prices[-self.sma_long:]) / self.sma_long
        
        # Bollinger Bands
        if len(prices) >= self.bb_period:
            recent_prices = prices[-self.bb_period:]
            self.bb_middle = sum(recent_prices) / self.bb_period
            std_dev = statistics.stdev(recent_prices)
            self.bb_upper = self.bb_middle + (std_dev * self.bb_std_dev)
            self.bb_lower = self.bb_middle - (std_dev * self.bb_std_dev)
            
            # BB position (0 = at lower band, 1 = at upper band)
            if self.bb_upper != self.bb_lower:
                self.bb_position = (prices[-1] - self.bb_lower) / (self.bb_upper - self.bb_lower)
            else:
                self.bb_position = 0.5
        
        # Volatility calculation
        if len(self.return_data) >= self.volatility_lookback:
            recent_returns = self.return_data[-self.volatility_lookback:]
            self.current_volatility = statistics.stdev(recent_returns) * (288 ** 0.5)  # Annualized
    
    def _calculate_rsi(self, prices: List[float]) -> float:
        """Calculate RSI (proven working method)"""
        
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
    
    def _detect_market_regime(self):
        """Detect current market regime based on multiple factors"""
        
        if len(self.price_data) < 20:
            self.current_regime = MarketRegime.RANGING
            return
        
        # Trend detection using moving averages
        trend_bullish = self.sma_short_value > self.sma_long_value
        momentum_strong = abs(self.current_momentum) > 2.0  # 2% momentum threshold
        
        # Volatility check
        high_volatility = self.current_volatility > 0.4 if self.current_volatility > 0 else False
        
        # Regime classification
        if high_volatility:
            self.current_regime = MarketRegime.HIGH_VOLATILITY
        elif trend_bullish and self.current_momentum > 1.0:
            self.current_regime = MarketRegime.BULLISH
        elif not trend_bullish and self.current_momentum < -1.0:
            self.current_regime = MarketRegime.BEARISH
        else:
            self.current_regime = MarketRegime.RANGING
    
    def _generate_elite_signal(self) -> TradeSignal:
        """Generate sophisticated trading signals with multiple factors"""
        
        factors = {}
        
        # RSI factor (adaptive thresholds based on regime)
        if self.current_regime == MarketRegime.BULLISH:
            rsi_oversold, rsi_overbought = 40, 80
        elif self.current_regime == MarketRegime.BEARISH:
            rsi_oversold, rsi_overbought = 20, 60
        else:
            rsi_oversold, rsi_overbought = 30, 70
        
        if self.current_rsi < rsi_oversold:
            factors['rsi_oversold'] = (rsi_oversold - self.current_rsi) / rsi_oversold
        elif self.current_rsi > rsi_overbought:
            factors['rsi_overbought'] = (self.current_rsi - rsi_overbought) / (100 - rsi_overbought)
        
        # Momentum factor
        if self.current_momentum > 1.5:
            factors['momentum_bullish'] = min(self.current_momentum / 5.0, 1.0)
        elif self.current_momentum < -1.5:
            factors['momentum_bearish'] = min(-self.current_momentum / 5.0, 1.0)
        
        # Moving average crossover
        if len(self.price_data) >= self.sma_long:
            if self.sma_short_value > self.sma_long_value:
                ma_diff = (self.sma_short_value / self.sma_long_value - 1) * 100
                factors['ma_bullish'] = min(ma_diff / 2.0, 1.0)
            else:
                ma_diff = (1 - self.sma_short_value / self.sma_long_value) * 100
                factors['ma_bearish'] = min(ma_diff / 2.0, 1.0)
        
        # Bollinger Bands mean reversion
        if self.bb_position < 0.2:
            factors['bb_oversold'] = (0.2 - self.bb_position) * 5
        elif self.bb_position > 0.8:
            factors['bb_overbought'] = (self.bb_position - 0.8) * 5
        
        # Spread quality factor
        if self.current_spread_pct < self.max_spread_pct * 0.5:
            factors['tight_spread'] = 0.3  # Bonus for tight spreads
        
        # Volume factor (simplified)
        if hasattr(self, 'avg_volume') and self.current_volume > self.avg_volume * 1.2:
            factors['high_volume'] = 0.2
        
        # Calculate composite scores
        buy_factors = ['rsi_oversold', 'momentum_bullish', 'ma_bullish', 'bb_oversold', 'tight_spread', 'high_volume']
        sell_factors = ['rsi_overbought', 'momentum_bearish', 'ma_bearish', 'bb_overbought', 'tight_spread', 'high_volume']
        
        buy_score = sum(factors.get(f, 0) for f in buy_factors)
        sell_score = sum(factors.get(f, 0) for f in sell_factors)
        
        # Signal threshold (conservative)
        min_signal_strength = 0.8
        
        if buy_score > min_signal_strength and self.btc_balance == 0:
            expected_return = min(buy_score * 0.02, 0.05)  # Max 5% expected return
            risk_score = self._calculate_risk_score()
            return TradeSignal('BUY', buy_score, factors, expected_return, risk_score)
        
        elif sell_score > min_signal_strength and self.btc_balance > 0:
            expected_return = min(sell_score * 0.02, 0.05)
            risk_score = self._calculate_risk_score()
            return TradeSignal('SELL', sell_score, factors, expected_return, risk_score)
        
        return TradeSignal('HOLD', max(buy_score, sell_score), factors, 0.0, 0.5)
    
    def _calculate_risk_score(self) -> float:
        """Calculate current risk score (0 = low risk, 1 = high risk)"""
        
        risk_factors = []
        
        # Volatility risk
        if self.current_volatility > 0:
            vol_risk = min(self.current_volatility / 0.5, 1.0)  # Normalize to 50% vol
            risk_factors.append(vol_risk)
        
        # Spread risk
        spread_risk = min(self.current_spread_pct / (self.max_spread_pct * 2), 1.0)
        risk_factors.append(spread_risk)
        
        # Drawdown risk
        current_portfolio = self.current_balance + (self.btc_balance * self.current_price)
        drawdown = (self.peak_balance - current_portfolio) / self.peak_balance
        drawdown_risk = min(drawdown / 0.1, 1.0)  # Normalize to 10% drawdown
        risk_factors.append(drawdown_risk)
        
        return sum(risk_factors) / len(risk_factors) if risk_factors else 0.5
    
    def _can_trade(self) -> bool:
        """Check if trading is allowed based on various conditions"""
        
        # Check daily trade limit
        if self.trades_today >= self.daily_trade_limit:
            return False
        
        # Check cooldown period
        if self.last_trade_time:
            time_since_last = datetime.now() - self.last_trade_time
            if time_since_last < timedelta(minutes=self.cooldown_minutes):
                return False
        
        # Check spread quality
        if self.current_spread_pct > self.max_spread_pct:
            return False
        
        # Check minimum position size
        portfolio_value = self.current_balance + (self.btc_balance * self.current_price)
        if portfolio_value * self.max_position_pct < self.min_position_value:
            return False
        
        return True
    
    async def _execute_elite_trade(self, signal: TradeSignal):
        """Execute trade with proper position sizing and risk management"""
        
        portfolio_value = self.current_balance + (self.btc_balance * self.current_price)
        
        if signal.action == 'BUY':
            # Calculate position size (conservative)
            position_value = min(
                portfolio_value * self.max_position_pct,
                self.current_balance * 0.9  # Leave some cash buffer
            )
            
            # Adjust for confidence
            position_value *= signal.confidence
            
            if position_value < self.min_position_value:
                return
            
            # Execute buy at ask price (realistic)
            btc_quantity = position_value / self.current_ask
            fees = position_value * self.fee_rate
            
            # Update balances
            self.current_balance -= (position_value + fees)
            self.btc_balance += btc_quantity
            
            print(f"\n🟢 BUY EXECUTED")
            print(f"💰 Position: ${position_value:.2f} | ₿ Quantity: {btc_quantity:.8f}")
            print(f"💲 Price: ${self.current_ask:,.2f} | 🎯 Confidence: {signal.confidence:.2f}")
            print(f"📊 Factors: {len([f for f, v in signal.factors.items() if v > 0])}")
            
        else:  # SELL
            if self.btc_balance <= 0:
                return
            
            # Sell all BTC at bid price (realistic)
            sale_proceeds = self.btc_balance * self.current_bid
            fees = sale_proceeds * self.fee_rate
            
            # Update balances
            self.current_balance += (sale_proceeds - fees)
            sold_btc = self.btc_balance
            self.btc_balance = 0.0
            
            print(f"\n🔴 SELL EXECUTED")
            print(f"💰 Proceeds: ${sale_proceeds:.2f} | ₿ Sold: {sold_btc:.8f}")
            print(f"💲 Price: ${self.current_bid:,.2f} | 🎯 Confidence: {signal.confidence:.2f}")
        
        # Record trade
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            'action': signal.action,
            'price': self.current_ask if signal.action == 'BUY' else self.current_bid,
            'quantity': btc_quantity if signal.action == 'BUY' else sold_btc,
            'value': position_value if signal.action == 'BUY' else sale_proceeds,
            'confidence': signal.confidence,
            'factors': signal.factors,
            'portfolio_value': self.current_balance + (self.btc_balance * self.current_price),
            'regime': self.current_regime.value
        }
        
        self.trade_history.append(trade_record)
        self.trades_today += 1
        self.last_trade_time = datetime.now()
    
    def _check_risk_limits(self) -> bool:
        """Check if risk limits are breached"""
        
        current_portfolio = self.current_balance + (self.btc_balance * self.current_price)
        
        # Update peak for drawdown calculation
        if current_portfolio > self.peak_balance:
            self.peak_balance = current_portfolio
        
        # Check maximum drawdown
        current_drawdown = (self.peak_balance - current_portfolio) / self.peak_balance
        self.max_drawdown = max(self.max_drawdown, current_drawdown)
        
        if current_drawdown > self.max_total_drawdown_pct:
            print(f"🚨 Total drawdown limit breached: {current_drawdown:.2%}")
            return True
        
        # Check daily loss
        daily_loss = (self.daily_start_balance - current_portfolio) / self.daily_start_balance
        if daily_loss > self.max_daily_loss_pct:
            print(f"🚨 Daily loss limit breached: {daily_loss:.2%}")
            return True
        
        return False
    
    def _check_new_day(self):
        """Check if it's a new trading day and reset counters"""
        
        now = datetime.now()
        session_hours = (now - self.session_start).total_seconds() / 3600
        
        # Reset daily counters every 24 hours
        if session_hours >= 24:
            self.trades_today = 0
            self.session_start = now
            self.daily_start_balance = self.current_balance + (self.btc_balance * self.current_price)
            print(f"\n🌅 New trading day started. Portfolio: ${self.daily_start_balance:.2f}")
    
    def _log_market_data(self, signal: TradeSignal):
        """Log market data and signals for analysis"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'price': self.current_price,
            'bid': self.current_bid,
            'ask': self.current_ask,
            'spread_pct': self.current_spread_pct * 100,
            'rsi': self.current_rsi,
            'momentum': self.current_momentum,
            'bb_position': self.bb_position,
            'volatility': self.current_volatility * 100 if self.current_volatility > 0 else 0,
            'regime': self.current_regime.value,
            'signal_action': signal.action,
            'signal_confidence': signal.confidence,
            'portfolio_value': self.current_balance + (self.btc_balance * self.current_price),
            'btc_balance': self.btc_balance,
            'cash_balance': self.current_balance
        }
        
        # Append to log file
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"⚠️ Logging error: {e}")
    
    def _display_elite_status(self):
        """Display comprehensive trading status"""
        
        portfolio_value = self.current_balance + (self.btc_balance * self.current_price)
        total_return = (portfolio_value - self.starting_balance) / self.starting_balance * 100
        
        # Calculate win rate if we have trades
        if self.trade_history:
            profitable_trades = 0
            for i in range(1, len(self.trade_history)):
                prev_portfolio = self.trade_history[i-1].get('portfolio_value', self.starting_balance)
                curr_portfolio = self.trade_history[i].get('portfolio_value', self.starting_balance)
                if curr_portfolio > prev_portfolio:
                    profitable_trades += 1
            win_rate = profitable_trades / len(self.trade_history) * 100
        else:
            win_rate = 0
        
        current_time = datetime.now().strftime('%H:%M:%S')
        
        print(f"\n⚡ ELITE STATUS | {current_time} | BTC: ${self.current_price:,.0f}")
        print(f"💰 Portfolio: ${portfolio_value:.2f} | Return: {total_return:+.2f}% | Drawdown: {self.max_drawdown:.1%}")
        print(f"📊 RSI: {self.current_rsi:.0f} | Mom: {self.current_momentum:+.1f}% | BB: {self.bb_position:.2f}")
        print(f"🎯 Regime: {self.current_regime.value.upper()} | Vol: {self.current_volatility*100:.1f}% | Spread: {self.current_spread_pct*10000:.1f}bps")
        print(f"🔄 Trades: {self.trades_today}/{self.daily_trade_limit} | Win Rate: {win_rate:.0f}%")
    
    async def _generate_final_report(self):
        """Generate comprehensive final performance report"""
        
        final_portfolio = self.current_balance + (self.btc_balance * self.current_price)
        total_return = final_portfolio - self.starting_balance
        return_pct = (total_return / self.starting_balance) * 100
        
        session_duration = datetime.now() - self.session_start
        hours = session_duration.total_seconds() / 3600
        
        print(f"\n\n🏆 ELITE TRADING BOT - FINAL REPORT")
        print("="*70)
        print(f"⏱️ Session Duration: {hours:.1f} hours")
        print(f"💰 Starting Balance: ${self.starting_balance:,.2f}")
        print(f"💰 Final Portfolio: ${final_portfolio:.2f}")
        print(f"📊 Total Return: ${total_return:+.2f} ({return_pct:+.2f}%)")
        print(f"📈 Peak Portfolio: ${self.peak_balance:.2f}")
        print(f"📉 Max Drawdown: {self.max_drawdown:.2%}")
        print(f"🔄 Total Trades: {len(self.trade_history)}")
        print(f"📅 Trades Today: {self.trades_today}")
        
        if self.trade_history:
            avg_trade_value = sum(t['value'] for t in self.trade_history) / len(self.trade_history)
            print(f"💵 Average Trade Size: ${avg_trade_value:.2f}")
            
            # Regime analysis
            regime_counts = {}
            for trade in self.trade_history:
                regime = trade.get('regime', 'unknown')
                regime_counts[regime] = regime_counts.get(regime, 0) + 1
            
            print(f"🧠 Regime Distribution:")
            for regime, count in regime_counts.items():
                pct = count / len(self.trade_history) * 100
                print(f"   {regime}: {count} trades ({pct:.0f}%)")
        
        print(f"📁 Log File: {self.log_file}")
        print("="*70)
    
    async def _execute_apm_workflow(self):
        """Execute APM workflow for knowledge management"""
        
        try:
            # Calculate session metrics
            session_duration = (time.time() - self.session_start_time) / 3600  # hours
            final_portfolio = self.current_balance + (self.btc_balance * self.current_price)
            total_return = (final_portfolio - self.starting_balance) / self.starting_balance * 100
            
            print(f"\n🔄 Executing APM Workflow...")
            
            # Run complete APM workflow
            success = self.apm_workflow.run_complete_workflow(
                log_file=self.log_file,
                session_duration=session_duration,
                total_return=total_return,
                trades_executed=len(self.trade_history)
            )
            
            if success:
                print(f"✅ APM Workflow completed successfully")
            else:
                print(f"⚠️ APM Workflow completed with issues")
                
        except Exception as e:
            print(f"❌ APM Workflow error: {e}")
            print(f"📁 Raw log file available: {self.log_file}")

async def main():
    """Launch the Elite Trading Bot"""
    
    print("🚀 Launching Elite Trading Bot...")
    print("💡 This bot combines proven features with enhanced capabilities")
    
    try:
        duration_input = input("\n⏱️ Duration in minutes (default 60, use 1440 for 24 hours): ")
        duration = int(duration_input) if duration_input else 60
    except:
        duration = 60
    
    if duration >= 60:
        confirm = input(f"\n⚠️ You're about to run for {duration/60:.1f} hours. Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return
    
    bot = EliteTradingBot()
    await bot.start_elite_trading(duration)

if __name__ == "__main__":
    asyncio.run(main())