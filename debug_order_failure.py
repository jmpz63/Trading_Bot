#!/usr/bin/env python3
"""
🔍 Real-time order failure diagnostic
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
    
    print(f"🔗 Request URL: {url}")
    print(f"📋 Request Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        print(f"📡 Status Code: {response.status_code}")
        
        result = response.json()
        print(f"📝 Full Response: {json.dumps(result, indent=2)}")
        
        return result
        
    except Exception as e:
        print(f"💥 Exception: {e}")
        return None

def test_realistic_order():
    """Test the exact order the bot is trying to place"""
    
    # Get current BTC price
    price_response = requests.get("https://api.kraken.com/0/public/Ticker?pair=XBTUSD")
    btc_price = float(price_response.json()['result']['XXBTZUSD']['c'][0])
    
    print(f"💰 Current BTC Price: ${btc_price:,.2f}")
    
    # Simulate bot's order calculation
    balance = 64.15  # Your current balance
    trade_percentage = 0.10  # 10%
    trade_amount = balance * trade_percentage  # $6.42
    btc_amount = trade_amount / btc_price
    
    print(f"🤖 Bot would calculate:")
    print(f"   Balance: ${balance}")
    print(f"   Trade %: {trade_percentage*100}%") 
    print(f"   Trade $: ${trade_amount:.2f}")
    print(f"   BTC Amount: {btc_amount:.8f}")
    
    # Check minimums
    min_btc = 0.00005
    min_usd = 0.50
    
    if trade_amount < min_usd:
        print(f"⚠️ Adjusting: ${trade_amount:.2f} → ${min_usd} (minimum)")
        trade_amount = min_usd
        btc_amount = trade_amount / btc_price
        
    if btc_amount < min_btc:
        print(f"⚠️ Adjusting: {btc_amount:.8f} → {min_btc:.8f} BTC (minimum)")
        btc_amount = min_btc
        trade_amount = btc_amount * btc_price
    
    print(f"📊 Final Order:")
    print(f"   BTC: {btc_amount:.8f}")
    print(f"   USD: ${trade_amount:.2f}")
    print()
    
    # Test 1: Validation only (safe)
    print("🧪 TEST 1: Order Validation (Safe)")
    print("-" * 40)
    
    validate_data = {
        'pair': 'XBTUSD',
        'type': 'buy',
        'ordertype': 'market',
        'volume': f"{btc_amount:.8f}",
        'validate': 'true'
    }
    
    validate_result = kraken_request('/0/private/AddOrder', validate_data)
    
    if validate_result and validate_result.get('error'):
        print(f"❌ Validation failed: {validate_result['error']}")
        
        # Specific error handling
        for error in validate_result['error']:
            if 'Permission denied' in error:
                print("🔧 FIX: API key needs 'Orders and Trades' permission")
            elif 'Insufficient funds' in error:
                print("🔧 FIX: Need more USD in account")
            elif 'volume minimum' in error:
                print("🔧 FIX: Order too small, increase size")
            elif 'Invalid arguments' in error:
                print(f"🔧 FIX: Check order parameters: {error}")
    else:
        print("✅ Validation successful!")
        
    # Test 2: Check account permissions
    print("\n🔑 TEST 2: API Permissions")
    print("-" * 40)
    
    # Check what permissions we have
    balance_result = kraken_request('/0/private/Balance')
    if balance_result and not balance_result.get('error'):
        print("✅ Can read account balance")
    else:
        print("❌ Cannot read balance")
        
    orders_result = kraken_request('/0/private/OpenOrders')
    if orders_result and not orders_result.get('error'):
        print("✅ Can query orders")
    else:
        print("❌ Cannot query orders")

if __name__ == "__main__":
    test_realistic_order()