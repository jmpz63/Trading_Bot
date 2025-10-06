#!/usr/bin/env python3
"""
Elite Trading Bot Monitor
Real-time monitoring of 24/7 trading bot performance
"""

import json
import os
import time
import subprocess
from datetime import datetime, timedelta
import glob

class TradingBotMonitor:
    """Monitor the 24/7 elite trading bot"""
    
    def __init__(self):
        self.project_root = "/home/arm1/Trade_Bot"
        
    def get_latest_log_file(self):
        """Find the most recent log file"""
        log_pattern = f"{self.project_root}/data/logs/elite_bot_*.json"
        log_files = glob.glob(log_pattern)
        if log_files:
            return max(log_files, key=os.path.getctime)
        return None
    
    def check_bot_running(self):
        """Check if the bot process is still running"""
        try:
            result = subprocess.run(
                ["ps", "aux"], 
                capture_output=True, 
                text=True
            )
            return "elite_trading_bot.py" in result.stdout
        except:
            return False
    
    def analyze_recent_data(self, log_file, minutes=60):
        """Analyze recent trading data"""
        
        if not log_file or not os.path.exists(log_file):
            return None
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_data = []
        
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        timestamp = datetime.fromisoformat(data['timestamp'])
                        if timestamp >= cutoff_time:
                            recent_data.append(data)
        except Exception as e:
            print(f"Error reading log: {e}")
            return None
        
        if not recent_data:
            return None
        
        # Calculate statistics
        latest = recent_data[-1]
        
        # Price analysis
        prices = [d['price'] for d in recent_data]
        price_change = ((latest['price'] - recent_data[0]['price']) / recent_data[0]['price']) * 100
        
        # Signal analysis
        signals = [d['signal_action'] for d in recent_data]
        buy_signals = signals.count('BUY')
        sell_signals = signals.count('SELL')
        hold_signals = signals.count('HOLD')
        
        # Regime analysis
        regimes = [d['regime'] for d in recent_data]
        current_regime = latest['regime']
        
        stats = {
            'latest_data': latest,
            'data_points': len(recent_data),
            'price_change_pct': price_change,
            'signal_counts': {
                'BUY': buy_signals,
                'SELL': sell_signals,
                'HOLD': hold_signals
            },
            'current_regime': current_regime,
            'avg_confidence': sum(d['signal_confidence'] for d in recent_data) / len(recent_data)
        }
        
        return stats
    
    def display_status(self):
        """Display current bot status"""
        
        # Check if bot is running
        bot_running = self.check_bot_running()
        
        # Get latest log file
        log_file = self.get_latest_log_file()
        
        # Analyze recent data (last hour)
        stats = self.analyze_recent_data(log_file, 60)
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n🤖 ELITE TRADING BOT MONITOR")
        print("="*60)
        print(f"📅 Current Time: {current_time}")
        print(f"🏃 Bot Status: {'🟢 RUNNING' if bot_running else '🔴 STOPPED'}")
        
        if log_file:
            print(f"📁 Log File: {os.path.basename(log_file)}")
        else:
            print("📁 Log File: No log file found")
            return
        
        if stats:
            latest = stats['latest_data']
            
            print(f"\n💰 CURRENT PORTFOLIO:")
            print(f"   Portfolio Value: ${latest['portfolio_value']:.2f}")
            print(f"   BTC Balance: {latest['btc_balance']:.8f}")
            print(f"   Cash Balance: ${latest['cash_balance']:.2f}")
            
            print(f"\n📊 MARKET DATA (Last Hour):")
            print(f"   BTC Price: ${latest['price']:,.2f}")
            print(f"   Price Change: {stats['price_change_pct']:+.2f}%")
            print(f"   Spread: {latest['spread_pct']*10000:.1f} bps")
            print(f"   Data Points: {stats['data_points']}")
            
            print(f"\n🎯 TECHNICAL INDICATORS:")
            print(f"   RSI: {latest['rsi']:.1f}")
            print(f"   Momentum: {latest['momentum']:+.1f}%")
            print(f"   BB Position: {latest['bb_position']:.2f}")
            print(f"   Volatility: {latest['volatility']:.1f}%")
            
            print(f"\n🧠 TRADING ANALYSIS:")
            print(f"   Current Regime: {stats['current_regime'].upper()}")
            print(f"   Avg Confidence: {stats['avg_confidence']:.2f}")
            print(f"   Signals (1h): BUY:{stats['signal_counts']['BUY']} SELL:{stats['signal_counts']['SELL']} HOLD:{stats['signal_counts']['HOLD']}")
            
        print("="*60)
    
    def monitor_loop(self, refresh_seconds=30):
        """Continuous monitoring loop"""
        
        print("🚀 Starting Elite Trading Bot Monitor")
        print("Press Ctrl+C to stop monitoring\n")
        
        try:
            while True:
                os.system('clear')  # Clear screen
                self.display_status()
                
                print(f"\n⏱️ Refreshing in {refresh_seconds} seconds... (Ctrl+C to stop)")
                time.sleep(refresh_seconds)
                
        except KeyboardInterrupt:
            print("\n👋 Monitor stopped by user")

def main():
    """Main monitoring function"""
    
    monitor = TradingBotMonitor()
    
    print("🤖 Elite Trading Bot Monitor")
    print("1. Show current status")
    print("2. Start continuous monitoring")
    
    try:
        choice = input("\nSelect option (1-2): ")
    except KeyboardInterrupt:
        print("\nExiting...")
        return
    
    if choice == "1":
        monitor.display_status()
    elif choice == "2":
        monitor.monitor_loop()
    else:
        monitor.display_status()

if __name__ == "__main__":
    main()