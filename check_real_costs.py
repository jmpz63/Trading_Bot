#!/usr/bin/env python3
"""
💰 REAL TRADING COST CALCULATOR
Shows actual Kraken fees and true P&L
"""

import requests
import time
import hmac
import hashlib
import base64
import urllib.parse
from secure_api_config import KRAKEN_API_KEY, KRAKEN_API_SECRET

def create_signature(endpoint, data, nonce):
    postdata = urllib.parse.urlencode(data)
    encoded = f"{nonce}{postdata}".encode()
    message = endpoint.encode() + hashlib.sha256(encoded).digest()
    signature = hmac.new(
        base64.b64decode(KRAKEN_API_SECRET),
        message,
        hashlib.sha512
    )
    return base64.b64encode(signature.digest()).decode()

def kraken_request(endpoint, data=None):
    url = f"https://api.kraken.com{endpoint}"
    if data is None:
        data = {}
    data['nonce'] = str(int(time.time() * 1000000))
    
    headers = {
        'API-Key': KRAKEN_API_KEY,
        'API-Sign': create_signature(endpoint, data, data['nonce'])
    }
    
    response = requests.post(url, headers=headers, data=data, timeout=10)
    return response.json()

def check_real_costs():
    print("💰 REAL TRADING COST ANALYSIS")
    print("=" * 50)
    
    # Get current balance
    balance_result = kraken_request('/0/private/Balance')
    if balance_result and 'result' in balance_result:
        usd_balance = float(balance_result['result'].get('ZUSD', 0))
        btc_balance = float(balance_result['result'].get('XXBT', 0))
        
        print(f"💵 Current USD Balance: ${usd_balance:.2f}")
        print(f"₿ Current BTC Balance: {btc_balance:.8f} BTC")
        
        # Calculate total value
        btc_price_response = requests.get("https://api.kraken.com/0/public/Ticker?pair=XBTUSD")
        btc_price = float(btc_price_response.json()['result']['XXBTZUSD']['c'][0])
        
        total_value = usd_balance + (btc_balance * btc_price)
        print(f"💰 Total Account Value: ${total_value:.2f}")
        
        # Compare to starting balance
        estimated_start = 38.36  # From your session
        total_loss = estimated_start - total_value
        
        if total_loss > 0:
            print(f"📉 TOTAL LOSS: ${total_loss:.2f} ({total_loss/estimated_start*100:.1f}%)")
            print("   This includes ALL fees, spreads, and market losses")
        else:
            print(f"📈 TOTAL GAIN: ${-total_loss:.2f}")
    
    print("\n📊 KRAKEN FEE STRUCTURE:")
    print("   • Market Orders: 0.16% fee")
    print("   • $6.20 trade = ~$0.01 fee")
    print("   • Round trip = ~$0.02 in fees")
    print("   • Plus bid-ask spread losses")
    
    # Get recent trades to show actual fees
    print("\n🔍 RECENT TRADES (last 10):")
    trades_result = kraken_request('/0/private/TradesHistory', {'count': 10})
    
    if trades_result and 'result' in trades_result and 'trades' in trades_result['result']:
        total_fees = 0
        for trade_id, trade in trades_result['result']['trades'].items():
            if trade.get('pair') == 'XXBTZUSD':
                fee = float(trade.get('fee', 0))
                total_fees += fee
                
                print(f"   {trade['type'].upper()}: {trade['vol']} BTC @ ${float(trade['price']):.2f} | Fee: ${fee:.4f}")
        
        print(f"\n💸 TOTAL FEES PAID: ${total_fees:.4f}")
        
        if total_fees > 0.05:  # More than 5 cents in fees
            print("⚠️  HIGH FEE WARNING: Consider larger, less frequent trades")

if __name__ == "__main__":
    check_real_costs()