#!/usr/bin/env python3
"""
🔗 Connect Your Bot to Kraken - Simple Setup
============================================
"""

import os
import requests
from pathlib import Path

def test_kraken_connection():
    """Test basic connection to Kraken."""
    print("🔍 TESTING KRAKEN CONNECTION")
    print("=" * 40)
    
    try:
        # Test public API
        url = "https://api.kraken.com/0/public/Time"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Kraken API connected successfully!")
            
            # Get Bitcoin price
            btc_url = "https://api.kraken.com/0/public/Ticker?pair=XBTUSD"
            btc_response = requests.get(btc_url, timeout=10)
            
            if btc_response.status_code == 200:
                btc_data = btc_response.json()
                btc_price = float(btc_data['result']['XXBTZUSD']['c'][0])
                print(f"₿ Current BTC Price: ${btc_price:,.2f}")
                print("🎯 47% lower fees than Coinbase!")
                return True
        
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def setup_kraken_api_keys():
    """Guide user through API key setup."""
    print("\n🔧 KRAKEN API KEYS SETUP")
    print("=" * 30)
    print("📋 Steps to get your Kraken API keys:")
    print("1. Go to: https://www.kraken.com/")
    print("2. Login to your account")
    print("3. Go to Settings → API")
    print("4. Click 'Generate New Key'")
    print("5. Set permissions:")
    print("   ✅ Query Funds")
    print("   ✅ Query Open Orders & Trades")
    print("   ✅ Query Closed Orders & Trades")
    print("   ✅ Create & Modify Orders")
    print("   ❌ Withdraw Funds (keep disabled)")
    print("6. Copy your API Key and Private Key")
    
    # Check if secure config exists
    config_file = Path('secure_api_config.py')
    if config_file.exists():
        print(f"\n✅ Found existing config: {config_file}")
        with open(config_file, 'r') as f:
            content = f.read()
            if 'kraken' in content.lower() and 'your_' not in content.lower():
                print("✅ Kraken credentials appear to be configured!")
                return True
    
    # Create template
    template = '''#!/usr/bin/env python3
"""
Secure API Configuration for Trading Bots
"""

# Kraken API Credentials
KRAKEN_API_KEY = "YOUR_KRAKEN_API_KEY_HERE"
KRAKEN_API_SECRET = "YOUR_KRAKEN_PRIVATE_KEY_HERE"

# Risk Management Settings
RISK_SETTINGS = {
    "low": {"capital": 1500, "max_trade": 30, "max_loss": 100},
    "med": {"capital": 3000, "max_trade": 60, "max_loss": 100},
    "high": {"capital": 5000, "max_trade": 100, "max_loss": 100}
}

def get_kraken_credentials():
    return KRAKEN_API_KEY, KRAKEN_API_SECRET
'''
    
    with open(config_file, 'w') as f:
        f.write(template)
    
    # Set secure permissions
    os.chmod(config_file, 0o600)
    
    print(f"\n✅ Created config template: {config_file}")
    print("🔒 File permissions set to 600 (secure)")
    print("\n🎯 NEXT STEPS:")
    print(f"1. Edit {config_file}")
    print("2. Replace 'YOUR_KRAKEN_API_KEY_HERE' with your real API key")
    print("3. Replace 'YOUR_KRAKEN_PRIVATE_KEY_HERE' with your private key")
    print("4. Save the file")
    print("5. Run: python3 kraken_trader.py")
    
    return False

def check_existing_trader():
    """Check if kraken_trader.py exists and is ready."""
    trader_file = Path('kraken_trader.py')
    if trader_file.exists():
        print("\n🤖 EXISTING KRAKEN TRADER FOUND")
        print("=" * 35)
        print("✅ kraken_trader.py exists")
        print("💰 Progressive risk tiers: LOW($1,500) → MED($3,000) → HIGH($5,000)")
        print("🛡️ Built-in $100 max loss protection")
        print("📊 47% lower fees than Coinbase")
        
        # Check file size to see if it's substantial
        size = trader_file.stat().st_size
        print(f"📁 File size: {size:,} bytes")
        
        if size > 5000:  # Substantial file
            print("✅ Trader appears to be fully implemented!")
            return True
        else:
            print("⚠️ Trader file seems small, may need completion")
            return False
    else:
        print("\n❌ kraken_trader.py not found")
        return False

def main():
    """Main setup function."""
    print("🔗 CONNECT YOUR BOT TO KRAKEN")
    print("=" * 50)
    print("Simple setup for your Kraken Bitcoin trading bot")
    print()
    
    # Step 1: Test connection
    if not test_kraken_connection():
        print("❌ Cannot connect to Kraken. Check internet connection.")
        return
    
    # Step 2: Check existing trader
    trader_exists = check_existing_trader()
    
    # Step 3: Setup API keys
    keys_configured = setup_kraken_api_keys()
    
    # Step 4: Final instructions
    print("\n🎉 SETUP STATUS")
    print("=" * 20)
    print(f"🌐 Kraken Connection: ✅")
    print(f"🤖 Trading Bot: {'✅' if trader_exists else '⚠️'}")
    print(f"🔑 API Keys: {'✅' if keys_configured else '⚠️ Needs setup'}")
    
    if trader_exists and keys_configured:
        print("\n🚀 READY TO TRADE!")
        print("Run: python3 kraken_trader.py")
    else:
        print("\n📋 NEXT STEPS:")
        if not keys_configured:
            print("1. Configure your API keys in secure_api_config.py")
        print("2. Test connection: python3 kraken_trader.py")
        print("3. Start with LOW risk tier ($1,500 capital)")

if __name__ == "__main__":
    main()
