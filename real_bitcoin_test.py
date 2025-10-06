#!/usr/bin/env python3
"""
₿ REAL Bitcoin Day Trading: Original vs Optimized
5-minute sessions with live market data
"""

import yfinance as yf
import json
import time
import numpy as np
from datetime import datetime
from pathlib import Path

class RealBitcoinTrader:
    def __init__(self, capital=50000, model="original"):
        self.capital = capital
        self.starting_capital = capital
        self.btc_position = 0.0
        self.trades = 0
        self.profits = []
        self.model = model
        
        # Model parameters
        if model == "original":
            self.profit_target = 0.003  # 0.3%
            self.position_size = 0.05   # 5%
            self.trade_freq = 0.3       # 30%
        else:  # optimized
            self.profit_target = 0.005  # 0.5% 
            self.position_size = 0.08   # 8%
            self.trade_freq = 0.4       # 40%
        
        # Bitcoin connection
        self.btc = yf.Ticker("BTC-USD")
        self.price_history = []
        
        print(f"₿ {model.title()} Model - ${capital:,} capital")
    
    def get_live_price(self):
        """Get real Bitcoin price"""
        try:
            hist = self.btc.history(period="1d")
            price = float(hist['Close'].iloc[-1])
            self.price_history.append(price)
            return price
        except:
            return self.price_history[-1] if self.price_history else 60000
    
    def should_trade(self, price):
        """Trading signals for live data"""
        # Calculate momentum if we have price history
        momentum = 0
        if len(self.price_history) >= 3:
            recent = self.price_history[-3:]
            momentum = (recent[-1] - recent[0]) / recent[0]
        
        # Trade logic based on model
        if self.btc_position == 0:  # Look to buy
            return (momentum > 0.0005 or np.random.random() < self.trade_freq)
        else:  # Look to sell
            pnl = (price - self.entry_price) / self.entry_price
            return (pnl >= self.profit_target or pnl <= -0.002 or momentum < -0.001)
    
    def execute_trade(self, price):
        """Execute trade with live price"""
        if self.btc_position == 0 and self.should_trade(price):
            # BUY
            amount = self.capital * self.position_size
            btc_bought = amount / price
            self.capital -= amount
            self.btc_position = btc_bought
            self.entry_price = price
            self.trades += 1
            print(f"₿ BUY: {btc_bought:.6f} BTC @ ${price:,.2f}")
            
        elif self.btc_position > 0 and self.should_trade(price):
            # SELL
            value = self.btc_position * price
            profit = value - (self.btc_position * self.entry_price)
            self.capital += value
            self.profits.append(profit)
            
            status = "✅ PROFIT" if profit > 0 else "❌ LOSS"
            print(f"₿ SELL: {self.btc_position:.6f} BTC @ ${price:,.2f} | {status}: ${profit:+,.2f}")
            self.btc_position = 0.0
    
    def run_session(self, minutes=5):
        """Run live trading session"""
        print(f"\n🚀 {self.model.upper()} - {minutes} min REAL DATA session")
        print("=" * 50)
        
        start_time = time.time()
        end_time = start_time + (minutes * 60)
        
        while time.time() < end_time:
            price = self.get_live_price()
            self.execute_trade(price)
            
            # Status
            portfolio = self.capital + (self.btc_position * price)
            pnl = portfolio - self.starting_capital
            remaining = (end_time - time.time()) / 60
            
            print(f"🔄 ${price:,.0f} | Portfolio: ${portfolio:,.0f} | P&L: ${pnl:+,.0f} | {remaining:.1f}m left")
            time.sleep(15)  # Check every 15 seconds
        
        # Final close
        if self.btc_position > 0:
            final_price = self.get_live_price()
            final_value = self.btc_position * final_price
            final_profit = final_value - (self.btc_position * self.entry_price)
            self.capital += final_value
            self.profits.append(final_profit)
            print(f"₿ FINAL CLOSE: ${final_profit:+,.2f}")
            self.btc_position = 0.0
        
        # Results
        total_profit = self.capital - self.starting_capital
        return_pct = total_profit / self.starting_capital
        win_rate = (len([p for p in self.profits if p > 0]) / len(self.profits) * 100) if self.profits else 0
        
        print(f"\n📊 {self.model.upper()} RESULTS:")
        print(f"Real Profit: ${total_profit:+,.2f}")
        print(f"Return: {return_pct:+.2%}")
        print(f"Trades: {len(self.profits)}")
        print(f"Win Rate: {win_rate:.0f}%")
        print(f"Price Samples: {len(self.price_history)}")
        
        return {
            'model': self.model,
            'profit': total_profit,
            'return_pct': return_pct,
            'trades': len(self.profits),
            'win_rate': win_rate,
            'price_samples': len(self.price_history)
        }

def run_comparison():
    """Run original vs optimized comparison"""
    print("₿ REAL BITCOIN DATA DAY TRADING COMPARISON")
    print("=" * 60)
    
    # Session 1: Original Model
    original = RealBitcoinTrader(50000, "original")
    orig_results = original.run_session(5)
    
    print(f"\n⏳ 30 second pause between sessions...")
    time.sleep(30)
    
    # Session 2: Optimized Model
    optimized = RealBitcoinTrader(50000, "optimized") 
    opt_results = optimized.run_session(5)
    
    # Comparison
    print(f"\n🏆 COMPARISON RESULTS")
    print("=" * 40)
    
    profit_diff = opt_results['profit'] - orig_results['profit']
    return_diff = opt_results['return_pct'] - orig_results['return_pct']
    
    print(f"ORIGINAL: ${orig_results['profit']:+,.2f} ({orig_results['return_pct']:+.1%}) | {orig_results['trades']} trades")
    print(f"OPTIMIZED: ${opt_results['profit']:+,.2f} ({opt_results['return_pct']:+.1%}) | {opt_results['trades']} trades")
    print(f"\nIMPROVEMENT: ${profit_diff:+,.2f} ({return_diff:+.1%})")
    
    if profit_diff > 0:
        print("✅ OPTIMIZATION SUCCESSFUL!")
        improvement_pct = (profit_diff / abs(orig_results['profit']) * 100) if orig_results['profit'] != 0 else 0
        print(f"Performance gain: {improvement_pct:+.0f}%")
    else:
        print("⚠️ Need further optimization")
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'original': orig_results,
        'optimized': opt_results,
        'improvement': profit_diff,
        'success': profit_diff > 0
    }
    
    Path('logs').mkdir(exist_ok=True)
    with open('logs/real_bitcoin_comparison.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to logs/real_bitcoin_comparison.json")
    
    # Next iteration suggestions
    print(f"\n💡 NEXT OPTIMIZATION:")
    if opt_results['win_rate'] > orig_results['win_rate']:
        print("✅ Win rate improved - keep entry logic")
    else:
        print("📊 Adjust entry signals")
    
    if opt_results['trades'] > orig_results['trades']:
        print("✅ More trades executed")  
    else:
        print("⚡ Increase trade frequency")
    
    print("🚀 Ready for next iteration!")
    return results

if __name__ == "__main__":
    run_comparison()
