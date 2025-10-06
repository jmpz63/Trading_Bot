#!/usr/bin/env python3
"""
🔧 KRAKEN API DIAGNOSTIC TOOL
Test real API permissions and order placement capabilities
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
    """Make authenticated request to Kraken API with detailed error reporting"""
    url = f"https://api.kraken.com{endpoint}"
    
    if data is None:
        data = {}
        
    data['nonce'] = str(int(time.time() * 1000000))
    
    headers = {
        'API-Key': KRAKEN_API_KEY,
        'API-Sign': create_signature(endpoint, data, data['nonce'])
    }
    
    print(f"🔗 Making request to: {url}")
    print(f"📋 Data: {data}")
    print(f"🔑 API Key: {KRAKEN_API_KEY[:8]}...{KRAKEN_API_KEY[-4:]}")
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        print(f"📡 Response Status: {response.status_code}")
        
        result = response.json()
        print(f"📝 Response Data: {json.dumps(result, indent=2)}")
        
        if 'error' in result and result['error']:
            print(f"❌ Kraken API Error: {result['error']}")
            
        return result
        
    except Exception as e:
        print(f"💥 Request Exception: {e}")
        return None

def test_api_permissions():
    """Test various Kraken API endpoints to diagnose permission issues"""
    
    print("🔧 KRAKEN API DIAGNOSTIC TEST")
    print("=" * 50)
    
    # Test 1: Account Balance (should work with any API key)
    print("\n📊 TEST 1: Account Balance")
    print("-" * 30)
    balance_result = kraken_request('/0/private/Balance')
    
    # Test 2: Account Info (check trading permissions)
    print("\n🏦 TEST 2: Account Info")  
    print("-" * 30)
    account_result = kraken_request('/0/private/Account')
    
    # Test 3: Open Orders (check order permissions)
    print("\n📋 TEST 3: Open Orders")
    print("-" * 30)
    orders_result = kraken_request('/0/private/OpenOrders')
    
    # Test 4: Trading Fee Info
    print("\n💰 TEST 4: Trade Volume/Fees")
    print("-" * 30)
    fees_result = kraken_request('/0/private/TradeVolume')
    
    # Test 5: SMALL Test Order (validate mode - won't execute)
    print("\n🧪 TEST 5: Validate Small BTC Order (Test Mode)")
    print("-" * 50)
    
    test_order_data = {
        'pair': 'XBTUSD',
        'type': 'buy', 
        'ordertype': 'market',
        'volume': '0.00001',  # Very small amount
        'validate': 'true'    # VALIDATE ONLY - doesn't execute
    }
    
    test_order_result = kraken_request('/0/private/AddOrder', test_order_data)
    
    # Summary
    print("\n🎯 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if balance_result and 'result' in balance_result:
        print("✅ API Authentication: WORKING")
    else:
        print("❌ API Authentication: FAILED")
        
    if account_result and 'result' in account_result:
        print("✅ Account Access: WORKING")
    else:
        print("❌ Account Access: FAILED")
        
    if orders_result is not None:
        print("✅ Order Queries: WORKING")
    else:
        print("❌ Order Queries: FAILED")
        
    if test_order_result and 'result' in test_order_result:
        print("✅ Order Validation: WORKING")
        print("🚀 REAL TRADING SHOULD WORK!")
    else:
        print("❌ Order Validation: FAILED")
        if test_order_result and 'error' in test_order_result:
            print(f"   Error Details: {test_order_result['error']}")
            
        # Common issues
        print("\n🔧 POSSIBLE ISSUES:")
        print("   • API key lacks 'Orders and Trades' permission")
        print("   • API key is for 'Query' only, not 'Trade'")
        print("   • Account needs additional verification")
        print("   • Insufficient balance for minimum order")

if __name__ == "__main__":
    test_api_permissions()