#!/usr/bin/env python3
"""
Daily Swing Trading Scanner
Run this daily (morning or evening) to get swing trading signals
"""

import sys
from pathlib import Path
import asyncio

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from strategies.swing_trading_analyzer import SwingTradingAnalyzer, SwingTradingNotifier

def main():
    """Daily swing trading analysis"""
    
    print("🎯 Daily Swing Trading Scanner")
    print("Purpose: Find 2-30 day hold opportunities")
    print("Strategy: Technical analysis + trend following")
    print()
    
    # Configuration
    config = {
        'watchlist': [
            # Market ETFs (good for beginners)
            'SPY',   # S&P 500
            'QQQ',   # NASDAQ 100
            'IWM',   # Russell 2000
            'XLF',   # Financial Sector
            'XLK',   # Technology Sector
            
            # Blue Chip Stocks
            'AAPL',  # Apple
            'MSFT',  # Microsoft
            'GOOGL', # Alphabet
            'AMZN',  # Amazon
            'TSLA',  # Tesla
            
            # More Opportunities
            'NVDA',  # NVIDIA
            'META',  # Meta
            'JPM',   # JPMorgan
            'JNJ',   # Johnson & Johnson
            'V',     # Visa
            'WMT',   # Walmart
            'PG',    # Procter & Gamble
            'KO',    # Coca-Cola
            'DIS',   # Disney
            'NFLX'   # Netflix
        ],
        'notifications': {
            'console': True,
            'email': False,  # Can add email later
            'save_to_file': True
        }
    }
    
    # Initialize analyzer and notifier
    analyzer = SwingTradingAnalyzer(config)
    notifier = SwingTradingNotifier(config)
    
    # Run analysis
    print("Starting analysis...")
    results = analyzer.scan_watchlist()
    
    # Display results
    notifier.send_notifications(results)
    
    # Save to file for historical tracking
    if config['notifications'].get('save_to_file'):
        import json
        from datetime import datetime
        
        filename = f"swing_signals_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = Path("data/signals") / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filepath}")
    
    print("\n✅ Daily scan complete!")
    print("\n🔔 Set up a daily reminder to run this script:")
    print("   - Morning: Before market open (8:00 AM ET)")
    print("   - Evening: After market close (5:00 PM ET)")

if __name__ == "__main__":
    main()