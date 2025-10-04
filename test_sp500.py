#!/usr/bin/env python3
"""Quick test of S&P 500 data connection"""

import yfinance as yf
import pandas as pd

def test_sp500_connection():
    print('📊 Testing S&P 500 Data Connection...')
    print('=' * 40)
    
    try:
        # Test SPY data
        spy = yf.Ticker('SPY')
        spy_info = spy.info
        print(f'SPY Current Price: ${spy_info.get("currentPrice", "N/A")}')
        print(f'Market Cap: ${spy_info.get("marketCap", 0):,}')
        
        # Test historical data
        hist = spy.history(period='5d')
        print(f'Historical Data Points: {len(hist)}')
        if not hist.empty:
            print(f'Latest Close: ${hist["Close"].iloc[-1]:.2f}')
        
        # Test major stocks
        stocks = ['AAPL', 'MSFT', 'GOOGL']
        print(f'\n📈 Major Stocks:')
        for symbol in stocks:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            price = info.get('currentPrice', 'N/A')
            print(f'{symbol}: ${price}')
        
        print('\n✅ S&P 500 connection successful!')
        return True
        
    except Exception as e:
        print(f'❌ Error connecting to S&P 500 data: {e}')
        return False

if __name__ == "__main__":
    test_sp500_connection()