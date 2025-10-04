#!/usr/bin/env python3
"""
S&P 500 Trading Bot Example
Demonstrates how to trade S&P 500 using the trading bot framework
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from data.sp500_integration import SP500MarketData, SP500TradingInterface, SP500Strategy
import yaml

async def main():
    """Main S&P 500 trading bot example"""
    
    print("🎯 S&P 500 Trading Bot Starting...")
    print("=" * 50)
    
    # Load configuration
    config_path = Path("config/sp500_config.yaml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    else:
        print("⚠️  S&P 500 config not found, using defaults")
        config = {'paper_trading': True}
    
    # Initialize components
    print("📊 Initializing market data...")
    market_data = SP500MarketData(config)
    
    print("💼 Initializing trading interface...")
    trading_interface = SP500TradingInterface(config)
    
    print("🧠 Initializing strategy...")
    strategy = SP500Strategy()
    
    print("\n📈 Market Analysis:")
    print("-" * 30)
    
    # Check market hours
    market_status = await market_data.get_market_hours()
    print(f"Market Open: {'✅ YES' if market_status.get('is_open') else '❌ NO'}")
    
    # Get S&P 500 ETF data
    print("\n📊 S&P 500 ETF Data:")
    spy_data = await market_data.get_sp500_data("SPY", "5d")
    if not spy_data.empty:
        latest_close = spy_data['Close'].iloc[-1]
        daily_change = spy_data['Close'].pct_change().iloc[-1] * 100
        print(f"SPY Latest Close: ${latest_close:.2f}")
        print(f"Daily Change: {daily_change:+.2f}%")
    
    # Get real-time prices for major stocks
    print("\n💰 Major Stock Prices:")
    major_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    
    for symbol in major_stocks:
        price_data = await market_data.get_real_time_price(symbol)
        if price_data:
            price = price_data.get('price', 0)
            change_pct = price_data.get('change_percent', 0)
            print(f"{symbol}: ${price:.2f} ({change_pct:+.2f}%)")
    
    # Scan for opportunities
    print("\n🔍 Scanning for Trading Opportunities:")
    opportunities = await market_data.scan_sp500_opportunities()
    
    if opportunities:
        print(f"Found {len(opportunities)} opportunities:")
        for opp in opportunities[:5]:  # Top 5
            momentum = opp['momentum']
            signal = opp['signal']
            emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "🟡"
            print(f"  {emoji} {opp['symbol']}: {momentum:+.2f}% momentum → {signal}")
    else:
        print("No significant opportunities found.")
    
    # Generate trading signals
    print("\n🎯 Strategy Signals:")
    signals = await strategy.analyze(market_data)
    
    if signals:
        print(f"Generated {len(signals)} trading signals:")
        for signal in signals:
            action_emoji = "🟢" if signal['action'] == 'BUY' else "🔴"
            confidence = signal['confidence'] * 100
            print(f"  {action_emoji} {signal['action']} {signal['symbol']} "
                  f"(Confidence: {confidence:.0f}%) - {signal['reason']}")
            
            # Execute paper trade (if enabled)
            if config.get('paper_trading', True):
                quantity = 10  # Example: 10 shares
                order_result = await trading_interface.place_order(
                    symbol=signal['symbol'],
                    quantity=quantity,
                    side=signal['action'].lower()
                )
                
                if order_result.get('paper_trade'):
                    print(f"    📝 Paper Trade Executed: {order_result['order_id']}")
    else:
        print("No trading signals generated.")
    
    print("\n" + "=" * 50)
    print("✅ S&P 500 Trading Bot Analysis Complete!")
    print("\n💡 Next Steps:")
    print("1. Review signals and opportunities")
    print("2. Adjust strategy parameters if needed") 
    print("3. Set up real broker API for live trading")
    print("4. Run in continuous mode for automated trading")

if __name__ == "__main__":
    asyncio.run(main())