#!/usr/bin/env python3
"""
Simple Swing Trading Daily Scanner
Run this daily to get your swing trading signals
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

def analyze_stock(symbol):
    """Quick swing trading analysis for a stock"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="3mo")  # 3 months of data
        
        if data.empty:
            return None
        
        # Current price
        current = data['Close'].iloc[-1]
        
        # Simple moving averages
        sma20 = data['Close'].rolling(20).mean().iloc[-1]
        sma50 = data['Close'].rolling(50).mean().iloc[-1]
        
        # RSI calculation
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        # Price change
        week_ago = data['Close'].iloc[-5] if len(data) >= 5 else data['Close'].iloc[0]
        week_change = (current - week_ago) / week_ago * 100
        
        # Simple signal logic
        signal = "HOLD"
        confidence = 0
        
        if current > sma20 > sma50 and rsi < 70 and week_change > 0:
            signal = "BUY"
            confidence = 70
        elif current > sma20 and rsi < 60:
            signal = "WEAK BUY"  
            confidence = 40
        elif current < sma20 < sma50 and rsi > 30:
            signal = "SELL"
            confidence = 60
        elif current < sma50 and rsi > 40:
            signal = "WEAK SELL"
            confidence = 35
        
        return {
            'symbol': symbol,
            'price': current,
            'signal': signal,
            'confidence': confidence,
            'rsi': rsi,
            'week_change': week_change,
            'above_sma20': current > sma20,
            'above_sma50': current > sma50
        }
        
    except Exception as e:
        return {'symbol': symbol, 'error': str(e)}

def main():
    """Run daily swing trading scan"""
    
    print("🎯 DAILY SWING TRADING SCANNER")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎪 Strategy: 2-30 day holds, technical analysis")
    print()
    
    # Watchlist - adjust as needed
    watchlist = [
        'SPY', 'QQQ', 'IWM',           # Market ETFs
        'AAPL', 'MSFT', 'GOOGL',       # Tech giants  
        'AMZN', 'TSLA', 'NVDA',        # Growth stocks
        'JPM', 'JNJ', 'V',             # Blue chips
        'XLF', 'XLK', 'XLE'            # Sector ETFs
    ]
    
    results = []
    
    print("🔍 Scanning watchlist...")
    for symbol in watchlist:
        print(f"  Analyzing {symbol}...", end="")
        analysis = analyze_stock(symbol)
        
        if analysis and 'error' not in analysis:
            results.append(analysis)
            print(" ✅")
        else:
            print(" ❌")
    
    # Sort by signal strength
    buy_signals = [r for r in results if 'BUY' in r['signal']]
    sell_signals = [r for r in results if 'SELL' in r['signal']]
    hold_signals = [r for r in results if r['signal'] == 'HOLD']
    
    buy_signals.sort(key=lambda x: x['confidence'], reverse=True)
    sell_signals.sort(key=lambda x: x['confidence'], reverse=True)
    
    print("\n" + "="*60)
    print("📊 SWING TRADING OPPORTUNITIES")
    print("="*60)
    
    # Buy signals
    if buy_signals:
        print(f"\n🟢 BUY OPPORTUNITIES ({len(buy_signals)}):")
        print("-" * 40)
        for stock in buy_signals:
            trend = "📈" if stock['above_sma20'] and stock['above_sma50'] else "📊"
            print(f"  {trend} {stock['symbol']:<6} ${stock['price']:>7.2f} "
                  f"({stock['week_change']:+5.1f}%) RSI:{stock['rsi']:>5.1f} "
                  f"Conf:{stock['confidence']}%")
            print(f"       Signal: {stock['signal']}")
            
            # Quick reasoning
            reasons = []
            if stock['above_sma20']: reasons.append("Above 20-day avg")
            if stock['above_sma50']: reasons.append("Above 50-day avg") 
            if stock['rsi'] < 70: reasons.append("Not overbought")
            if stock['week_change'] > 0: reasons.append("Weekly momentum")
            
            if reasons:
                print(f"       Why: {', '.join(reasons)}")
            print()
    else:
        print("\n🟢 No strong buy signals today")
    
    # Sell signals  
    if sell_signals:
        print(f"\n🔴 SELL/AVOID OPPORTUNITIES ({len(sell_signals)}):")
        print("-" * 40)
        for stock in sell_signals:
            trend = "📉" if not stock['above_sma20'] and not stock['above_sma50'] else "📊"
            print(f"  {trend} {stock['symbol']:<6} ${stock['price']:>7.2f} "
                  f"({stock['week_change']:+5.1f}%) RSI:{stock['rsi']:>5.1f} "
                  f"Conf:{stock['confidence']}%")
            print(f"       Signal: {stock['signal']}")
            
            # Quick reasoning
            reasons = []
            if not stock['above_sma20']: reasons.append("Below 20-day avg")
            if not stock['above_sma50']: reasons.append("Below 50-day avg")
            if stock['rsi'] > 70: reasons.append("Overbought")
            if stock['week_change'] < 0: reasons.append("Weekly decline")
            
            if reasons:
                print(f"       Why: {', '.join(reasons)}")
            print()
    else:
        print("\n🔴 No strong sell signals today")
    
    print("\n" + "="*60)
    print("💡 SWING TRADING REMINDERS:")
    print("="*60)
    print("1. 📋 Do your own research before trading")
    print("2. 📊 Check earnings calendar and news")
    print("3. 💰 Position size: 2-5% of portfolio per trade")
    print("4. 🛡️  Always set stop losses (5-8% below entry)")
    print("5. 🎯 Target profits: 10-20% for swing trades")
    print("6. ⏰ Be patient - hold 2-30 days typically")
    print("7. 📈 Trade in direction of overall market trend")
    print("\n✅ Analysis complete! Review and trade wisely.")

if __name__ == "__main__":
    main()