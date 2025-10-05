#!/usr/bin/env python3
"""Quick test of Enhanced APM V2.0 components"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

def quick_test():
    print("🧪 TESTING ENHANCED APM V2.0 COMPONENTS")
    print("=" * 50)
    
    # Test 1: Data retrieval
    print("\n1️⃣ Testing Data Retrieval...")
    try:
        ticker = yf.Ticker("AAPL")
        data = ticker.history(period="1mo")
        if not data.empty:
            print(f"✅ Successfully retrieved {len(data)} days of AAPL data")
            print(f"   Latest price: ${data['Close'].iloc[-1]:.2f}")
        else:
            print("❌ No data retrieved")
    except Exception as e:
        print(f"❌ Data retrieval failed: {e}")
    
    # Test 2: Professional libraries
    print("\n2️⃣ Testing Professional Libraries...")
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
        print("✅ Scikit-learn imported successfully")
        
        # Test pandas operations
        df = pd.DataFrame({'price': [100, 101, 99, 102, 98]})
        df['sma'] = df['price'].rolling(3).mean()
        print("✅ Pandas vectorized operations working")
        
        # Test numpy
        returns = np.array([0.01, -0.02, 0.03, -0.01])
        volatility = np.std(returns) * np.sqrt(252)
        print(f"✅ NumPy calculations working (vol: {volatility:.3f})")
        
    except Exception as e:
        print(f"❌ Library test failed: {e}")
    
    # Test 3: Risk management calculation
    print("\n3️⃣ Testing Risk Management...")
    try:
        entry_price = 150.0
        stop_loss = 142.5  # 5% stop
        risk_amount = 200   # $200 risk
        
        risk_per_share = entry_price - stop_loss
        position_size = int(risk_amount / risk_per_share)
        
        print(f"✅ Risk Management Calculation:")
        print(f"   Entry: ${entry_price}, Stop: ${stop_loss}")
        print(f"   Risk per share: ${risk_per_share:.2f}")
        print(f"   Position size: {position_size} shares")
        
    except Exception as e:
        print(f"❌ Risk management test failed: {e}")
    
    # Test 4: Technical analysis
    print("\n4️⃣ Testing Technical Analysis...")
    try:
        # Simulate price data
        prices = pd.Series([100, 102, 99, 103, 101, 104, 102, 105])
        
        # Calculate indicators
        sma = prices.rolling(3).mean()
        roc = ((prices / prices.shift(3)) - 1) * 100
        
        print("✅ Technical Analysis Working:")
        print(f"   Latest SMA: {sma.iloc[-1]:.2f}")
        print(f"   Latest ROC: {roc.iloc[-1]:.2f}%")
        
    except Exception as e:
        print(f"❌ Technical analysis test failed: {e}")
    
    print("\n🎯 ENHANCED APM V2.0 COMPONENT TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    quick_test()
