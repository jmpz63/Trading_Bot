"""
Paper Trading Bot - Safe Testing Environment
Simulates trading with $1000 starting capital using enhanced strategy
"""

import asyncio
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json
import time
import random

# Import our enhanced components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.strategies.improved_momentum import ImprovedMomentumStrategy
from src.risk.enhanced_risk_manager import EnhancedRiskManager
from src.bot.spread_aware_order_manager import SpreadAwareOrderManager

class PaperTradingBot:
    """
    Paper trading bot with $1000 starting capital
    """
    
    def __init__(self, config_path: str = "config/enhanced_settings.yaml"):
        """Initialize paper trading bot"""
        
        # Load configuration
        import yaml
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Paper trading state
        self.starting_balance = self.config['advanced']['paper_starting_balance']
        self.current_balance = self.starting_balance
        self.btc_balance = 0.0
        self.current_btc_price = 0.0
        
        # Trading components
        self.strategy = ImprovedMomentumStrategy(
            "Enhanced Momentum", 
            self.config['trading']['strategy']
        )
        self.risk_manager = EnhancedRiskManager(self.config['trading'])
        self.order_manager = SpreadAwareOrderManager(self.config['trading'])
        
        # Trading state
        self.is_running = False
        self.trades_today = 0
        self.trade_history = []
        self.session_start = datetime.now()
        
        # Market simulation
        self.market_data = pd.DataFrame()
        self.last_price_update = datetime.now()
        
    async def start_paper_trading(self):
        """Start the paper trading session"""
        
        print("🚀 STARTING PAPER TRADING BOT 2.0")
        print("="*50)
        print(f"💰 Starting Balance: ${self.starting_balance:,.2f}")
        print(f"🎯 Strategy: {self.strategy.name}")
        print(f"📅 Session Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        
        self.is_running = True
        
        try:
            while self.is_running:
                # Update market data
                await self._update_market_data()
                
                # Update strategy with new data
                await self.strategy.update_data(self.market_data)
                
                # Generate trading signals
                signals = await self.strategy.generate_signals()
                
                # Process signals
                for signal in signals:
                    await self._process_signal(signal)
                
                # Display status
                self._display_status()
                
                # Check stop conditions
                if self._should_stop_trading():
                    break
                
                # Wait before next iteration
                await asyncio.sleep(30)  # 30 second intervals
                
        except KeyboardInterrupt:
            print("\n⏹️  Paper trading stopped by user")
        except Exception as e:
            print(f"\n❌ Error in paper trading: {e}")
        finally:
            await self._end_session()
    
    async def _update_market_data(self):
        """Simulate real market data updates"""
        
        # Simulate BTC price movement (realistic volatility)
        if len(self.market_data) == 0:
            # Starting price around current BTC level
            self.current_btc_price = 62500.0
        else:
            # Simulate price movement with realistic volatility
            volatility = 0.002  # 0.2% per 30-second period
            change_pct = np.random.normal(0, volatility)
            self.current_btc_price *= (1 + change_pct)
        
        # Simulate bid/ask spread (typical 0.02-0.08%)
        spread_pct = random.uniform(0.0002, 0.0008)
        bid = self.current_btc_price * (1 - spread_pct/2)
        ask = self.current_btc_price * (1 + spread_pct/2)
        
        # Simulate volume
        volume = random.uniform(10000, 50000)
        
        # Create new data point
        new_data = {
            'timestamp': datetime.now(),
            'open': self.current_btc_price,
            'high': self.current_btc_price * random.uniform(1.0, 1.002),
            'low': self.current_btc_price * random.uniform(0.998, 1.0),
            'close': self.current_btc_price,
            'volume': volume,
            'bid': bid,
            'ask': ask
        }
        
        # Add to market data
        if len(self.market_data) == 0:
            self.market_data = pd.DataFrame([new_data])
        else:
            self.market_data = pd.concat([
                self.market_data, 
                pd.DataFrame([new_data])
            ], ignore_index=True)
        
        # Keep only recent data (last 100 points)
        if len(self.market_data) > 100:
            self.market_data = self.market_data.tail(100).reset_index(drop=True)
    
    async def _process_signal(self, signal: Dict):
        """Process a trading signal"""
        
        # Calculate current portfolio value
        portfolio_value = self.current_balance + (self.btc_balance * self.current_btc_price)
        
        # Validate trade with risk manager
        validation = await self.risk_manager.validate_trade(
            signal, portfolio_value, {}
        )
        
        if not validation['approved']:
            print(f"🚫 Trade rejected: {validation['reason']}")
            return
        
        # Execute paper trade
        await self._execute_paper_trade(signal, validation['adjusted_quantity'])
    
    async def _execute_paper_trade(self, signal: Dict, quantity: float):
        """Execute a simulated trade"""
        
        action = signal['action']
        price = signal['price']
        
        # Simulate spread costs (use bid/ask)
        latest = self.market_data.iloc[-1]
        if action == 'BUY':
            execution_price = latest['ask']  # Buy at ask
            cost = quantity * execution_price
            
            if cost > self.current_balance:
                print(f"❌ Insufficient funds: Need ${cost:.2f}, have ${self.current_balance:.2f}")
                return
            
            # Execute buy
            self.current_balance -= cost
            self.btc_balance += quantity
            
        else:  # SELL
            execution_price = latest['bid']  # Sell at bid
            
            if quantity > self.btc_balance:
                print(f"❌ Insufficient BTC: Need {quantity:.8f}, have {self.btc_balance:.8f}")
                return
            
            # Execute sell
            proceeds = quantity * execution_price
            self.current_balance += proceeds
            self.btc_balance -= quantity
        
        # Calculate fees
        trade_value = quantity * execution_price
        fee = trade_value * 0.0016  # 0.16% Kraken fee
        self.current_balance -= fee
        
        # Record trade
        trade_record = {
            'timestamp': datetime.now(),
            'action': action,
            'quantity': quantity,
            'price': execution_price,
            'value': trade_value,
            'fee': fee,
            'balance_usd': self.current_balance,
            'balance_btc': self.btc_balance,
            'signal_confidence': signal.get('confidence', 0),
            'reasoning': signal.get('reasoning', [])
        }
        
        self.trade_history.append(trade_record)
        self.trades_today += 1
        
        # Display trade
        print(f"\n{'🟢 BUY' if action == 'BUY' else '🔴 SELL'}: {quantity:.8f} BTC @ ${execution_price:,.2f}")
        print(f"💰 Trade Value: ${trade_value:.2f} | Fee: ${fee:.2f}")
        print(f"💵 Balance: ${self.current_balance:.2f} | ₿ BTC: {self.btc_balance:.8f}")
        print(f"🎯 Confidence: {signal.get('confidence', 0):.2f} | Reasons: {', '.join(signal.get('reasoning', []))}")
        
        # Record with risk manager
        self.risk_manager.record_trade(trade_record)
    
    def _display_status(self):
        """Display current trading status"""
        
        portfolio_value = self.current_balance + (self.btc_balance * self.current_btc_price)
        total_return = portfolio_value - self.starting_balance
        return_pct = (total_return / self.starting_balance) * 100
        
        session_time = datetime.now() - self.session_start
        
        # Calculate win rate
        if len(self.trade_history) >= 2:
            # Compare consecutive buy/sell pairs
            wins = 0
            trades = 0
            for i in range(1, len(self.trade_history)):
                prev_trade = self.trade_history[i-1]
                curr_trade = self.trade_history[i]
                
                if prev_trade['action'] == 'BUY' and curr_trade['action'] == 'SELL':
                    trades += 1
                    if curr_trade['price'] > prev_trade['price']:
                        wins += 1
            
            win_rate = (wins / trades * 100) if trades > 0 else 0
        else:
            win_rate = 0
        
        print(f"\n⚡ PAPER TRADING STATUS | BTC: ${self.current_btc_price:,.0f}")
        print(f"💰 Portfolio Value: ${portfolio_value:.2f} | Return: ${total_return:+.2f} ({return_pct:+.2f}%)")
        print(f"💵 USD: ${self.current_balance:.2f} | ₿ BTC: {self.btc_balance:.8f} (${self.btc_balance * self.current_btc_price:.2f})")
        print(f"📊 Trades Today: {self.trades_today} | Win Rate: {win_rate:.1f}% | Session: {session_time}")
        
        if len(self.trade_history) >= 5:
            recent_pnl = sum(t.get('pnl', 0) for t in self.trade_history[-5:])
            print(f"🎯 Recent 5 Trades P&L: ${recent_pnl:.2f}")
    
    def _should_stop_trading(self) -> bool:
        """Check if trading should stop"""
        
        # Daily trade limit
        if self.trades_today >= 15:
            print(f"\n🏁 DAILY LIMIT: {self.trades_today} trades completed")
            return True
        
        # Loss limit
        portfolio_value = self.current_balance + (self.btc_balance * self.current_btc_price)
        loss_pct = (self.starting_balance - portfolio_value) / self.starting_balance
        
        if loss_pct > 0.05:  # 5% daily loss limit
            print(f"\n🛑 DAILY LOSS LIMIT: {loss_pct:.1%} loss reached")
            return True
        
        # Check performance-based stopping
        performance = self.risk_manager.get_performance_summary()
        if len(self.trade_history) > 10 and performance.get('win_rate', 0) < 0.2:
            print(f"\n⚠️  LOW WIN RATE: {performance.get('win_rate', 0):.1%} - Stopping trading")
            return True
        
        return False
    
    async def _end_session(self):
        """End the paper trading session and show results"""
        
        self.is_running = False
        
        print(f"\n\n🏆 PAPER TRADING SESSION RESULTS")
        print("="*60)
        
        final_portfolio = self.current_balance + (self.btc_balance * self.current_btc_price)
        total_return = final_portfolio - self.starting_balance
        return_pct = (total_return / self.starting_balance) * 100
        
        print(f"💰 Starting Balance: ${self.starting_balance:,.2f}")
        print(f"💰 Final Portfolio: ${final_portfolio:.2f}")
        print(f"   └─ USD: ${self.current_balance:.2f} | BTC: {self.btc_balance:.8f} (${self.btc_balance * self.current_btc_price:.2f})")
        print(f"📊 Total Return: ${total_return:+.2f} ({return_pct:+.2f}%)")
        print(f"🎯 Trades Executed: {len(self.trade_history)}")
        
        # Performance analysis
        performance = self.risk_manager.get_performance_summary()
        if performance.get('total_trades', 0) > 0:
            print(f"✅ Win Rate: {performance.get('win_rate', 0):.1%}")
            print(f"💸 Total Fees: ${performance.get('total_fees', 0):.2f}")
            print(f"⏱️  Session Duration: {datetime.now() - self.session_start}")
            print(f"💡 Recommendation: {performance.get('recommendation', 'N/A')}")
        
        print("="*60)
        
        # Save results
        await self._save_results()
    
    async def _save_results(self):
        """Save trading results to file"""
        
        results = {
            'session_start': self.session_start.isoformat(),
            'session_end': datetime.now().isoformat(),
            'starting_balance': self.starting_balance,
            'final_balance': self.current_balance + (self.btc_balance * self.current_btc_price),
            'trades': self.trade_history,
            'performance': self.risk_manager.get_performance_summary()
        }
        
        filename = f"data/logs/paper_trading_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"📊 Results saved to: {filename}")

async def main():
    """Main function to start paper trading"""
    
    print("🎯 INITIALIZING PAPER TRADING BOT...")
    
    try:
        bot = PaperTradingBot()
        await bot.start_paper_trading()
    except Exception as e:
        print(f"❌ Failed to start paper trading: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())