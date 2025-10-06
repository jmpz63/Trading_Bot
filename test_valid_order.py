#!/usr/bin/env python3
"""
🧪 Test REAL Kraken order with proper minimums
"""

import time
import json
import hmac
import hashlib
import requests
import base64
import urllib.parse
from secure_api_config import KRAKEN_API_KEY, KRAKEN_API_SECRET

def create_signature(endpoint, data, nonce):
    """Create Kraken API signature"""
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
    """Make authenticated request to Kraken API"""
    url = f"https://api.kraken.com{endpoint}"
    
    if data is None:
        data = {}
        
    data['nonce'] = str(int(time.time() * 1000000))
    
    headers = {
        'API-Key': KRAKEN_API_KEY,
        'API-Sign': create_signature(endpoint, data, data['nonce'])
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Request error: {e}")
        return None

def test_valid_order():
    """Test order with proper Kraken minimums"""
    
    print("🧪 TESTING VALID KRAKEN ORDER")
    print("=" * 40)
    
    # Get current BTC price
    btc_price_response = requests.get("https://api.kraken.com/0/public/Ticker?pair=XBTUSD")
    btc_price = float(btc_price_response.json()['result']['XXBTZUSD']['c'][0])
    
    print(f"💰 Current BTC Price: ${btc_price:,.2f}")
    
    # Calculate order that meets minimums
    min_btc = 0.00005  # Kraken minimum
    min_usd = 0.50     # Kraken minimum
    
    # Use slightly above minimum for safety
    test_btc = 0.000055  # 5% above minimum
    test_usd = test_btc * btc_price
    
    print(f"📊 Test Order Size: {test_btc:.8f} BTC")
    print(f"💵 Test Order Value: ${test_usd:.2f}")
    
    if test_usd < min_usd:
        print(f"❌ Still too small! Need ${min_usd} minimum")
        return
    
    # Test order validation (safe - won't execute)
    test_order_data = {
        'pair': 'XBTUSD',
        'type': 'buy', 
        'ordertype': 'market',
        'volume': f"{test_btc:.8f}",
        'validate': 'true'  # VALIDATION ONLY
    }
    
    print("\n🔍 VALIDATING ORDER (Test Mode - Won't Execute)")
    print("-" * 50)
    
    result = kraken_request('/0/private/AddOrder', test_order_data)
    
    if result:
        print(f"📝 Response: {json.dumps(result, indent=2)}")
        
        if 'error' in result and result['error']:
            print(f"❌ Validation Error: {result['error']}")
            
            # Common fixes
            if 'volume minimum not met' in str(result['error']):
                print("🔧 Solution: Increase order size")
            elif 'Insufficient funds' in str(result['error']):  
                print("🔧 Solution: Add more USD to account")
            elif 'General:Permission denied' in str(result['error']):
                print("🔧 Solution: Enable 'Orders and Trades' API permission")
                
        elif 'result' in result:
            print("✅ ORDER VALIDATION SUCCESSFUL!")
            print("🚀 REAL TRADING SHOULD WORK WITH THIS SIZE!")
            
            if 'descr' in result['result']:
                order_desc = result['result']['descr']
                print(f"📋 Order Description: {order_desc}")
    else:
        print("❌ No response from Kraken API")

if __name__ == "__main__":
    test_valid_order()