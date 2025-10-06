#!/usr/bin/env python3
"""
AGGRESSIVE LIVE GROWTH TRADER
Focus: Growing your balance, not preserving it
"""

import time
import json
import hmac
import hashlib
import requests
import base64
import urllib.parse
from datetime import datetime

class AggressiveLiveTrader:
    def __init__(self):
        # Growth-focused configuration
        self.starting_balance = 97.95
        self.trade_percentage = 0.10  # 10% of current balance per trade (more aggressive)
        self.max_daily_loss = 50.00  # Higher risk tolerance for growth
        
        # API configuration
        self.load_api_credentials()
        
        # Trading state
        self.session_start_balance = 0
        self.trades_today = 0
        
        print(f"AGGRESSIVE LIVE GROWTH TRADER")
        print(f"Starting Balance: ${self.starting_balance}")
        print(f"Trade Size: 10% of current balance")
        print(f"Max Daily Loss: ${self.max_daily_loss}")
        print(f"FOCUS: GROWING YOUR MONEY!")
    
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
    
    def calculate_trade_size(self, current_total_value):
        """Calculate trade size as percentage of current balance."""
        return current_total_value * self.trade_percentage
    
    def place_buy_order(self, usd_amount, btc_price):
        """Place a buy order."""
        btc_amount = usd_amount / btc_price
        
        print(f"LIVE BUY: ${usd_amount:.2f} -> {btc_amount:.8f} BTC @ ${btc_price:,.0f}")
        
        order_data = {
            'pair': 'XBTUSD',
            'type': 'buy',
            'ordertype': 'market',
            'volume': f"{btc_amount:.8f}"
        }
        
        result = self.kraken_request('/0/private/AddOrder', order_data)
        
        if result and 'result' in result and not result.get('error'):
            txid = result['result']['txid'][0]
            print(f"BUY ORDER EXECUTED: {txid}")
            self.trades_today += 1
            return txid
        else:
            error_msg = result.get('error', ['Unknown error']) if result else ['API error']
            print(f"BUY ORDER FAILED: {error_msg}")
            return None
    
    def place_sell_order(self, btc_amount, btc_price):
        """Place a sell order."""
        usd_value = btc_amount * btc_price
        
        print(f"LIVE SELL: {btc_amount:.8f} BTC -> ${usd_value:.2f} @ ${btc_price:,.0f}")
        
        order_data = {
            'pair': 'XBTUSD',
            'type': 'sell',
            'ordertype': 'market',
            'volume': f"{btc_amount:.8f}"
        }
        
        result = self.kraken_request('/0/private/AddOrder', order_data)
        
        if result and 'result' in result and not result.get('error'):
            txid = result['result']['txid'][0]
            print(f"SELL ORDER EXECUTED: {txid}")
            self.trades_today += 1
            return txid
        else:
            error_msg = result.get('error', ['Unknown error']) if result else ['API error']
            print(f"SELL ORDER FAILED: {error_msg}")
            return None
    
    def should_trade(self, price):
        """Aggressive trading logic for growth."""
        if not hasattr(self, 'price_history'):
            self.price_history = []
        
        self.price_history.append(price)
        
        if len(self.price_history) > 10:
            self.price_history = self.price_history[-10:]
        
        if len(self.price_history) < 5:
            return None
        
        # More aggressive thresholds for growth
        recent_avg = sum(self.price_history[-3:]) / 3
        older_avg = sum(self.price_history[-6:-3]) / 3
        
        price_change = (recent_avg - older_avg) / older_avg
        
        if price_change > 0.0005:  # 0.05% up = BUY
            return "buy"
        elif price_change < -0.0005:  # 0.05% down = SELL
            return "sell"
        
        return None
    
    def run_aggressive_session(self):
        """Run aggressive live trading session."""
        print(f"\nAGGRESSIVE LIVE TRADING SESSION")
        print("="*50)
        print("FOCUS: GROWING YOUR BALANCE")
        print("WARNING: REAL MONEY TRADING!")
        
        # Get starting balance
        usd_balance, btc_balance = self.get_account_balance()
        btc_price = self.get_btc_price()
        
        if btc_price == 0:
            print("Cannot get Bitcoin price, aborting")
            return
        
        self.session_start_balance = usd_balance + (btc_balance * btc_price)
        print(f"Session starting balance: ${self.session_start_balance:.2f}")
        
        # Confirm
        print(f"Trade size will be: {self.trade_percentage*100}% of current balance")
        confirm = input("Type 'GROW' to start aggressive trading: ")
        if confirm != 'GROW':
            print("Aggressive trading cancelled")
            return
        
        print("\nSTARTING AGGRESSIVE LIVE TRADING...")
        
        while True:
            try:
                # Get current state
                usd_balance, btc_balance = self.get_account_balance()
                btc_price = self.get_btc_price()
                
                if btc_price == 0:
                    print("Price unavailable, waiting...")
                    time.sleep(30)
                    continue
                
                current_total = usd_balance + (btc_balance * btc_price)
                session_pnl = current_total - self.session_start_balance
                
                # Check loss limit
                if session_pnl <= -self.max_daily_loss:
                    print(f"STOPPING: Loss limit reached: ${session_pnl:.2f}")
                    break
                
                # Calculate dynamic trade size
                trade_size = self.calculate_trade_size(current_total)
                
                # Trading decision
                action = self.should_trade(btc_price)
                
                if action == "buy" and usd_balance >= trade_size:
                    self.place_buy_order(trade_size, btc_price)
                    
                elif action == "sell" and btc_balance > 0:
                    # Sell portion of BTC holdings
                    btc_to_sell = min(btc_balance, trade_size / btc_price)
                    if btc_to_sell > 0.00001:  # Minimum order size
                        self.place_sell_order(btc_to_sell, btc_price)
                
                # Status update
                growth_pct = (session_pnl / self.session_start_balance) * 100
                
                print(f"BTC: ${btc_price:,.0f} | USD: ${usd_balance:.2f} | BTC: {btc_balance:.8f} | Total: ${current_total:.2f} | Growth: {growth_pct:+.2f}% | Trades: {self.trades_today}")
                
                # Wait 45 seconds (more frequent than conservative)
                time.sleep(45)
                
            except KeyboardInterrupt:
                print("\nAggressive session stopped by user")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(30)
        
        # Final results
        final_usd, final_btc = self.get_account_balance()
        final_price = self.get_btc_price()
        final_total = final_usd + (final_btc * final_price)
        final_growth = final_total - self.session_start_balance
        final_growth_pct = (final_growth / self.session_start_balance) * 100
        
        print(f"\nAGGRESSIVE SESSION RESULTS")
        print("="*40)
        print(f"Starting Balance: ${self.session_start_balance:.2f}")
        print(f"Final Balance: ${final_total:.2f}")
        print(f"Growth: ${final_growth:+.2f} ({final_growth_pct:+.2f}%)")
        print(f"Total Trades: {self.trades_today}")

def main():
    """Main function for aggressive live trading."""
    print("AGGRESSIVE LIVE GROWTH TRADER")
    print("="*50)
    print("WARNING: REAL MONEY TRADING!")
    print("FOCUS: GROWING YOUR BALANCE")
    
    trader = AggressiveLiveTrader()
    trader.run_aggressive_session()

if __name__ == "__main__":
    main()
