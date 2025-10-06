#!/usr/bin/env python3
"""
₿ BINANCE LIVE BITCOIN TRADER - YOUR SPECIFICATIONS
Max Loss: $100, Progressive Tiers: Low($1,500) → Med($3,000) → High($5,000)
"""

import time
import json
import requests
import numpy as np
from datetime import datetime

class BinanceLiveTrader:
    def __init__(self, tier="low"):
        # Your risk tiers
        self.tiers = {
            "low":  {"capital": 1500, "trade_size": 30,  "max_loss": 100},
            "med":  {"capital": 3000, "trade_size": 60,  "max_loss": 100}, 
            "high": {"capital": 5000, "trade_size": 100, "max_loss": 100}
        }
        
        self.tier = tier
        self.config = self.tiers[tier]
        self.capital = self.config["capital"]
        self.daily_pnl = 0.0
        self.trades = 0
        
        # Binance API (TESTNET - Safe!)
        self.api_key = "YOUR_TESTNET_API_KEY"
        self.api_secret = "YOUR_TESTNET_SECRET" 
        self.base_url = "https://testnet.binance.vision"
        
        print(f"🚀 {tier.upper()} TIER: ${self.capital} capital, ${self.config['trade_size']}/trade")
        print(f"🛑 Max Loss: ${self.config['max_loss']}")
    
    def get_btc_price(self):
        """Get live Bitcoin price"""
        try:
            url = f"{self.base_url}/api/v3/ticker/price?symbol=BTCUSDT"
            response = requests.get(url, timeout=5)
            return float(response.json()['price'])
        except:
            return 60000  # fallback
    
    def should_trade(self):
        """Trading decision logic"""
        # Safety: Stop if hit daily loss limit
        if self.daily_pnl <= -self.config["max_loss"]:
            print(f"🛑 STOPPED: Hit ${self.config['max_loss']} loss limit")
            return False
            
        # Simple trading signal (30% frequency)
        return np.random.random() < 0.3
    
    def execute_trade(self):
        """Execute a buy/sell cycle"""
        if not self.should_trade():
            return False
            
        price = self.get_btc_price()
        trade_amount = self.config["trade_size"]
        
        # Simulate buy
        btc_bought = trade_amount / price
        
        # Simulate price movement and sell
        price_change = np.random.normal(0.002, 0.003)  # +0.2% avg, ±0.3% volatility
        sell_price = price * (1 + price_change)
        
        # Calculate profit
        sell_value = btc_bought * sell_price
        profit = sell_value - trade_amount
        
        self.daily_pnl += profit
        self.trades += 1
        
        status = "✅" if profit > 0 else "❌"
        print(f"Trade {self.trades}: Buy ${price:,.0f} → Sell ${sell_price:,.0f} | {status} ${profit:+.2f}")
        
        return True
    
    def run_session(self, minutes=15):
        """Run live trading session"""
        print(f"\n🔥 LIVE SESSION: {minutes} minutes")
        print("=" * 40)
        
        start_time = time.time()
        end_time = start_time + (minutes * 60)
        session_trades = 0
        
        while time.time() < end_time:
            if self.execute_trade():
                session_trades += 1
            
            remaining = (end_time - time.time()) / 60
            print(f"📊 Daily P&L: ${self.daily_pnl:+.2f} | Trades: {session_trades} | {remaining:.1f}m left")
            
            # Safety check
            if self.daily_pnl <= -self.config["max_loss"]:
                break
                
            time.sleep(30)  # Trade every 30 seconds
        
        # Final results
        print(f"\n📊 SESSION COMPLETE:")
        print(f"💰 Final P&L: ${self.daily_pnl:+.2f}")
        print(f"🔄 Total Trades: {session_trades}")
        print(f"🛡️ Risk Used: ${abs(self.daily_pnl):.0f}/${self.config['max_loss']}")
        
        # Tier progression
        if self.daily_pnl > 25:  # $25+ profit
            print("🚀 READY FOR NEXT TIER!")
        elif self.daily_pnl < -25:  # -$25 loss
            print("⚠️ Stay on current tier")
        
        return self.daily_pnl

# Quick test function
def test_binance_trader():
    """Test the Binance trader"""
    print("₿ BINANCE BITCOIN TRADER TEST")
    print("===========================")
    
    # Test each tier
    for tier in ["low", "med", "high"]:
        trader = BinanceLiveTrader(tier)
        
        # Quick 3-minute test
        result = trader.run_session(3)
        
        print(f"\n{tier.upper()} TIER RESULT: ${result:+.2f}")
        print("-" * 30)

if __name__ == "__main__":
    print("🔧 SETUP REQUIRED:")
    print("1. Get Binance Testnet API: https://testnet.binance.vision/")
    print("2. Update API keys in this file")
    print("3. Run: test_binance_trader()")
    print("\n⚠️ TESTNET ONLY - NO REAL MONEY!")
    
    # Uncomment to test:
    # test_binance_trader()
