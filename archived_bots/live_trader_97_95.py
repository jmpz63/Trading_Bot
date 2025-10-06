#!/usr/bin/env python3
"""
LIVE $97.95 KRAKEN TRADER
Real trading with your exact balance
"""

import time
import json
import hmac
import hashlib
import requests
import base64
import urllib.parse
from datetime import datetime

class LiveTrader9795:
    def __init__(self):
        # Your exact balance configuration
        self.capital = 97.95
        self.trade_size_usd = 4.90  # $4.90 per trade
        self.max_daily_loss = 24.49  # $24.49 max loss
        
        # API configuration
        self.load_api_credentials()
        
        # Trading state
        self.daily_pnl = 0.0
        self.trades_today = 0
        
        print(f"LIVE KRAKEN TRADER - $97.95")
        print(f"Capital: ${self.capital}")
        print(f"Trade Size: ${self.trade_size_usd} USD per trade")
        print(f"Max Loss: ${self.max_daily_loss}")
        print(f"WARNING: THIS IS REAL MONEY TRADING!")
    
    def load_api_credentials(self):
        """Load API credentials."""
        try:
            from secure_api_config import get_kraken_credentials
            self.api_key, self.api_secret = get_kraken_credentials()
            print("Live API credentials loaded")
            return True
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return False
    
    def create_signature(self, endpoint, data, nonce):
        """Create Kraken API signature."""
        postdata = urllib.parse.urlencode(data)
        encoded = f"{nonce}{postdata}".encode()
        message = endpoint.encode() + hashlib.sha256(encoded).digest()
        signature = hmac.new(
            base64.b64decode(self.api_secret),
            message,
            hashlib.sha512
        )
        return base64.b64encode(signature.digest()).decode()
    
    def kraken_request(self, endpoint, data=None):
        """Make authenticated request to Kraken API."""
        if not self.api_key or not self.api_secret:
            return None
            
        url = f"https://api.kraken.com{endpoint}"
        
        if data is None:
            data = {}
            
        data['nonce'] = str(int(time.time() * 1000000))
        
        headers = {
            'API-Key': self.api_key,
            'API-Sign': self.create_signature(endpoint, data, data['nonce'])
        }
        
        try:
            response = requests.post(url, headers=headers, data=data, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    def get_btc_price(self):
        """Get current Bitcoin price."""
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
    
    def calculate_btc_amount(self, usd_amount, btc_price):
        """Calculate BTC amount for USD value."""
        return usd_amount / btc_price
    
    def place_buy_order(self, btc_amount):
        """Place a buy order for BTC."""
        print(f"PLACING REAL BUY ORDER: {btc_amount:.8f} BTC (~${self.trade_size_usd:.2f})")
        
        order_data = {
            'pair': 'XBTUSD',
            'type': 'buy',
            'ordertype': 'market',
            'volume': f"{btc_amount:.8f}"
        }
        
        result = self.kraken_request('/0/private/AddOrder', order_data)
        
        if result and 'result' in result and not result.get('error'):
            txid = result['result']['txid'][0]
            print(f"BUY ORDER PLACED: {txid}")
            return txid
        else:
            error_msg = result.get('error', ['Unknown error']) if result else ['API error']
            print(f"BUY ORDER FAILED: {error_msg}")
            return None
    
    def place_sell_order(self, btc_amount):
        """Place a sell order for BTC."""
        print(f"PLACING REAL SELL ORDER: {btc_amount:.8f} BTC (~${self.trade_size_usd:.2f})")
        
        order_data = {
            'pair': 'XBTUSD',
            'type': 'sell',
            'ordertype': 'market',
            'volume': f"{btc_amount:.8f}"
        }
        
        result = self.kraken_request('/0/private/AddOrder', order_data)
        
        if result and 'result' in result and not result.get('error'):
            txid = result['result']['txid'][0]
            print(f"SELL ORDER PLACED: {txid}")
            return txid
        else:
            error_msg = result.get('error', ['Unknown error']) if result else ['API error']
            print(f"SELL ORDER FAILED: {error_msg}")
            return None
    
    def get_account_balance(self):
        """Get current account balance."""
        result = self.kraken_request('/0/private/Balance')
        
        if result and 'result' in result and not result.get('error'):
            balances = result['result']
            usd_balance = float(balances.get('ZUSD', 0))
            btc_balance = float(balances.get('XXBT', 0))
            
            return usd_balance, btc_balance
        else:
            print("Could not get balance")
            return 0.0, 0.0
    
    def should_trade(self, price):
        """Simple trading logic."""
        if not hasattr(self, 'price_history'):
            self.price_history = []
        
        self.price_history.append(price)
        
        if len(self.price_history) > 5:
            self.price_history = self.price_history[-5:]
        
        if len(self.price_history) < 3:
            return None
        
        # Simple momentum
        recent_avg = sum(self.price_history[-2:]) / 2
        older_avg = sum(self.price_history[-3:-1]) / 2
        
        if recent_avg > older_avg * 1.001:  # 0.1% threshold
            return "buy"
        elif recent_avg < older_avg * 0.999:  # 0.1% threshold
            return "sell"
        
        return None
    
    def run_live_session(self, minutes=10):
        """Run live trading session."""
        print(f"\nLIVE TRADING SESSION - {minutes} minutes")
        print("="*50)
        print("WARNING: USING REAL MONEY!")
        
        # Confirm before starting
        confirm = input("Type 'YES' to start live trading: ")
        if confirm != 'YES':
            print("Live trading cancelled")
            return
        
        start_time = time.time()
        end_time = start_time + (minutes * 60)
        
        while time.time() < end_time:
            try:
                # Check loss limit
                if self.daily_pnl <= -self.max_daily_loss:
                    print(f"STOPPING: Daily loss limit reached: ${self.daily_pnl:.2f}")
                    break
                
                # Get price and balance
                btc_price = self.get_btc_price()
                if btc_price == 0:
                    print("Price unavailable")
                    time.sleep(30)
                    continue
                
                usd_balance, btc_balance = self.get_account_balance()
                
                # Trading decision
                action = self.should_trade(btc_price)
                
                if action and usd_balance > self.trade_size_usd:
                    if action == "buy":
                        btc_amount = self.calculate_btc_amount(self.trade_size_usd, btc_price)
                        order_id = self.place_buy_order(btc_amount)
                        if order_id:
                            self.trades_today += 1
                    
                    elif action == "sell" and btc_balance > 0:
                        # Sell small amount
                        btc_to_sell = min(btc_balance, self.calculate_btc_amount(self.trade_size_usd, btc_price))
                        order_id = self.place_sell_order(btc_to_sell)
                        if order_id:
                            self.trades_today += 1
                
                # Status
                remaining = (end_time - time.time()) / 60
                total_value = usd_balance + (btc_balance * btc_price)
                
                print(f"Time: {remaining:.1f}m | BTC: ${btc_price:,.0f} | USD: ${usd_balance:.2f} | BTC: {btc_balance:.8f} | Total: ${total_value:.2f} | Trades: {self.trades_today}")
                
                # Wait 60 seconds for live trading
                time.sleep(60)
                
            except KeyboardInterrupt:
                print("\nLive session stopped by user")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(30)
        
        print(f"\nLIVE SESSION COMPLETE")
        print(f"Total trades executed: {self.trades_today}")

def main():
    """Main function for live trading."""
    print("LIVE $97.95 KRAKEN TRADER")
    print("="*45)
    print("WARNING: THIS TRADES WITH REAL MONEY!")
    
    trader = LiveTrader9795()
    
    print("\nOptions:")
    print("1. Paper trade first (recommended)")
    print("2. Live trading (REAL MONEY)")
    
    choice = input("Choose option (1 or 2): ")
    
    if choice == "1":
        print("Starting paper trading session...")
        # Use the simulation trader instead
        import subprocess
        subprocess.run(["python3", "trader_97_95.py"])
    elif choice == "2":
        print("Starting LIVE trading session...")
        trader.run_live_session(minutes=10)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
