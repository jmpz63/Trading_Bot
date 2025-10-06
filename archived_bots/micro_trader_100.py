#!/usr/bin/env python3
"""
$100 MICRO KRAKEN TRADER
Perfect for starting with $100 capital
Small trades, same safety features
"""

import time
import json
import requests
from datetime import datetime

class MicroKrakenTrader:
    def __init__(self):
        # $100 MICRO tier configuration
        self.capital = 100
        self.trade_size = 5  # $5 per trade (5% of capital)
        self.max_daily_loss = 25  # $25 max loss (25% of capital)
        self.position_size = 0.05  # 5% position size
        
        # API configuration
        self.load_api_credentials()
        
        # Trading state
        self.daily_pnl = 0.0
        self.trades_today = 0
        self.positions = {}
        
        print(f"MICRO KRAKEN TRADER")
        print(f"Capital: ${self.capital}")
        print(f"Trade Size: ${self.trade_size} per trade")
        print(f"Max Loss: ${self.max_daily_loss}")
        print(f"Perfect for learning!")
    
    def load_api_credentials(self):
        """Load API credentials from secure config."""
        try:
            import sys
            sys.path.append('.')
            from secure_api_config import get_kraken_credentials
            self.api_key, self.api_secret = get_kraken_credentials()
            print("API credentials loaded")
        except Exception as e:
            print(f"Error loading credentials: {e}")
            self.api_key = None
            self.api_secret = None
    
    def get_btc_price(self):
        """Get current Bitcoin price from Kraken."""
        try:
            url = "https://api.kraken.com/0/public/Ticker?pair=XBTUSD"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                price = float(data['result']['XXBTZUSD']['c'][0])
                return price
            return 0.0
            
        except Exception as e:
            print(f"Price error: {e}")
            return 0.0
    
    def simulate_trade(self, action, btc_price):
        """Simulate a trade for $100 capital (safe mode)."""
        trade_usd = self.trade_size
        
        # Simple profit/loss simulation
        if action == "buy":
            outcome = "profit" if self.trades_today % 3 == 0 else "loss"
            if outcome == "profit":
                pnl = trade_usd * 0.02  # 2% profit
                print(f"BUY ${trade_usd} @ ${btc_price:.0f} -> +${pnl:.2f}")
            else:
                pnl = -trade_usd * 0.01  # 1% loss
                print(f"BUY ${trade_usd} @ ${btc_price:.0f} -> ${pnl:.2f}")
        else:
            outcome = "profit" if self.trades_today % 4 == 0 else "loss"
            if outcome == "profit":
                pnl = trade_usd * 0.015  # 1.5% profit
                print(f"SELL ${trade_usd} @ ${btc_price:.0f} -> +${pnl:.2f}")
            else:
                pnl = -trade_usd * 0.008  # 0.8% loss
                print(f"SELL ${trade_usd} @ ${btc_price:.0f} -> ${pnl:.2f}")
        
        self.daily_pnl += pnl
        self.trades_today += 1
        
        return pnl
    
    def should_trade(self, price):
        """Simple trading logic for micro trades."""
        if not hasattr(self, 'price_history'):
            self.price_history = []
        
        self.price_history.append(price)
        
        # Keep last 5 prices
        if len(self.price_history) > 5:
            self.price_history = self.price_history[-5:]
        
        if len(self.price_history) < 3:
            return None
        
        # Simple momentum strategy
        recent_avg = sum(self.price_history[-2:]) / 2
        older_avg = sum(self.price_history[-3:-1]) / 2
        
        if recent_avg > older_avg * 1.0005:  # 0.05% threshold
            return "buy"
        elif recent_avg < older_avg * 0.9995:  # 0.05% threshold
            return "sell"
        
        return None
    
    def run_micro_session(self, minutes=3):
        """Run a micro trading session."""
        print(f"\nMICRO TRADING SESSION - {minutes} minutes")
        print("="*50)
        print("Running in SAFE SIMULATION mode for $100 capital")
        
        start_time = time.time()
        end_time = start_time + (minutes * 60)
        
        while time.time() < end_time:
            try:
                # Check daily loss limit
                if self.daily_pnl <= -self.max_daily_loss:
                    print(f"Daily loss limit reached: ${self.daily_pnl:.2f}")
                    break
                
                # Get current price
                btc_price = self.get_btc_price()
                if btc_price == 0:
                    print("Price unavailable, waiting...")
                    time.sleep(10)
                    continue
                
                # Trading decision
                action = self.should_trade(btc_price)
                
                if action:
                    self.simulate_trade(action, btc_price)
                
                # Status update
                remaining = (end_time - time.time()) / 60
                portfolio_value = self.capital + self.daily_pnl
                
                print(f"Time: {remaining:.1f}m | BTC: ${btc_price:,.0f} | Portfolio: ${portfolio_value:.2f} | P&L: ${self.daily_pnl:+.2f} | Trades: {self.trades_today}")
                
                # Wait 10 seconds for demo
                time.sleep(10)
                
            except KeyboardInterrupt:
                print("\nSession stopped by user")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(10)
        
        # Final summary
        final_portfolio = self.capital + self.daily_pnl
        return_pct = (self.daily_pnl / self.capital) * 100
        
        print(f"\nMICRO SESSION COMPLETE")
        print("="*30)
        print(f"Starting Capital: ${self.capital:.2f}")
        print(f"Final Portfolio: ${final_portfolio:.2f}")
        print(f"P&L: ${self.daily_pnl:+.2f} ({return_pct:+.1f}%)")
        print(f"Total Trades: {self.trades_today}")
        safety_status = "Safe" if self.daily_pnl > -self.max_daily_loss else "Triggered"
        print(f"Max Loss Protection: ${self.max_daily_loss} ({safety_status})")
        
        return {
            'starting_capital': self.capital,
            'final_portfolio': final_portfolio,
            'pnl': self.daily_pnl,
            'return_pct': return_pct,
            'trades': self.trades_today
        }

def main():
    """Main function for micro trading."""
    print("$100 MICRO KRAKEN TRADER")
    print("="*40)
    
    trader = MicroKrakenTrader()
    
    print("\nSession Options:")
    print("1. Quick test (3 minutes)")
    print("2. Learning session (10 minutes)")
    print("3. Extended test (30 minutes)")
    
    # Run 3-minute demo session
    print("\nRunning 3-minute demo session...")
    results = trader.run_micro_session(minutes=3)
    
    print(f"\nSession complete!")
    print(f"Performance: {results['return_pct']:+.1f}%")
    print(f"Perfect for your $100 starting capital!")

if __name__ == "__main__":
    main()
