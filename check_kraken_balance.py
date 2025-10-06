#!/usr/bin/env python3
"""
KRAKEN ACCOUNT BALANCE CHECKER
Check your real Kraken account balance and positions
"""

import time
import json
import hmac
import hashlib
import requests
import base64
import urllib.parse
from datetime import datetime

class KrakenBalanceChecker:
    def __init__(self):
        self.load_api_credentials()
        
    def load_api_credentials(self):
        """Load API credentials from secure config."""
        try:
            import sys
            sys.path.append('.')
            from secure_api_config import get_kraken_credentials
            self.api_key, self.api_secret = get_kraken_credentials()
            print("API credentials loaded")
            return True
        except Exception as e:
            print(f"Error loading credentials: {e}")
            self.api_key = None
            self.api_secret = None
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
    
    def get_account_balance(self):
        """Get account balance from Kraken."""
        print("Checking Kraken account balance...")
        
        result = self.kraken_request('/0/private/Balance')
        
        if result and 'result' in result and not result.get('error'):
            balances = result['result']
            print("\nKRAKEN ACCOUNT BALANCE")
            print("=" * 40)
            
            total_usd_value = 0
            
            for currency, balance in balances.items():
                balance_float = float(balance)
                if balance_float > 0:
                    # Convert some common currency codes
                    display_currency = currency
                    if currency == 'ZUSD':
                        display_currency = 'USD'
                        total_usd_value += balance_float
                    elif currency == 'XXBT':
                        display_currency = 'BTC'
                        # Get BTC price to calculate USD value
                        btc_price = self.get_btc_price()
                        if btc_price > 0:
                            usd_value = balance_float * btc_price
                            total_usd_value += usd_value
                            print(f"{display_currency}: {balance_float:.8f} (~${usd_value:,.2f})")
                        else:
                            print(f"{display_currency}: {balance_float:.8f}")
                    else:
                        print(f"{display_currency}: {balance_float:.8f}")
            
            print("-" * 40)
            print(f"TOTAL USD VALUE: ${total_usd_value:,.2f}")
            
            # Trading readiness check
            print(f"\nTRADING READINESS:")
            if total_usd_value >= 100:
                if total_usd_value < 1500:
                    tier = "MICRO"
                elif total_usd_value < 3000:
                    tier = "LOW"
                elif total_usd_value < 5000:
                    tier = "MED"
                else:
                    tier = "HIGH"
                    
                print(f"Ready for {tier} tier trading")
                trade_size = min(total_usd_value * 0.05, 100)
                print(f"Recommended trade size: ${trade_size:.0f}")
            else:
                print(f"Balance too low for safe trading")
                print(f"Minimum recommended: $100")
            
            return balances, total_usd_value
        else:
            if result:
                error_msg = result.get('error', ['Unknown error'])
                print(f"Error getting balance: {error_msg}")
            else:
                print("API connection failed")
            return None, 0
    
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
        except:
            return 0.0

def main():
    """Main function to check Kraken account."""
    print("KRAKEN ACCOUNT CHECKER")
    print("=" * 50)
    
    checker = KrakenBalanceChecker()
    
    # Check account balance
    balances, total_value = checker.get_account_balance()
    
    if balances is not None:
        print(f"\nAccount check complete!")
        print(f"Total portfolio value: ${total_value:,.2f}")
        
        # Determine best trading approach
        if total_value >= 1500:
            print(f"You can use the full kraken_trader.py (LOW tier)")
        elif total_value >= 100:
            print(f"Perfect for micro_trader_100.py (MICRO tier)")
        else:
            print(f"Consider depositing more funds for safe trading")
    else:
        print("Could not access account information")

if __name__ == "__main__":
    main()
