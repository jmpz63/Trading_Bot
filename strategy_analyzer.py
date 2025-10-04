#!/usr/bin/env python3
"""
Trade Strategy Analysis & Categorization
Show all trades organized by strategy type
"""

import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add the Trade_Bot directory to the path
trade_bot_dir = Path(__file__).parent
sys.path.append(str(trade_bot_dir))

from paper_trading_system import PaperTradingPortfolio
from trade_categorization import TradeCategorizer

def analyze_trade_strategies():
    """
    Analyze all trades by strategy category
    """
    
    print("📊 TRADE STRATEGY ANALYSIS & CATEGORIZATION")
    print("=" * 70)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize systems
    portfolio = PaperTradingPortfolio()
    categorizer = TradeCategorizer()
    
    # Get all trades
    trades = portfolio.trade_history
    
    if not trades:
        print("📊 No trades to analyze yet.")
        print("💡 Make some trades first using:")
        print("   python combined_trading.py")
        return
    
    print(f"📈 ANALYZING {len(trades)} TRADES:")
    print("-" * 50)
    
    # Categorize trades by strategy
    strategy_groups = defaultdict(list)
    
    for trade in trades:
        # Get strategy info (either from trade record or categorize it)
        if 'strategy_category' in trade:
            strategy_info = trade['strategy_category']
            strategy_type = strategy_info['primary_strategy']
        else:
            # Categorize old trades that don't have strategy info
            analysis = {'final_score': 60, 'confidence': 'MEDIUM'}
            market_context = {'regime': 'BULL'}
            strategy_info = categorizer.categorize_trade_intent(
                trade['symbol'], analysis, market_context
            )
            strategy_type = strategy_info['primary_strategy']
        
        strategy_groups[strategy_type].append({
            'trade': trade,
            'strategy_info': strategy_info
        })
    
    # Display trades by strategy
    for strategy_type, trade_group in strategy_groups.items():
        print(f"\n🎯 {strategy_type.upper()} TRADES ({len(trade_group)} trades)")
        print("-" * 60)
        
        total_value = 0
        
        for item in trade_group:
            trade = item['trade']
            strategy_info = item['strategy_info']
            
            # Trade details
            asset_type = "CRYPTO" if '-USD' in trade['symbol'] else "STOCK"
            shares_text = f"{trade['shares']:.6f}" if '-USD' in trade['symbol'] else f"{int(trade['shares'])}"
            
            print(f"📋 {trade['timestamp'][:19]} | {trade['action']} {shares_text} {trade['symbol']} ({asset_type})")
            print(f"    💰 Price: ${trade['price']:,.2f} | Value: ${trade['trade_value']:,.2f}")
            
            if 'expected_hold_period' in strategy_info:
                print(f"    ⏰ Expected Hold: {strategy_info['expected_hold_period']}")
                print(f"    🎯 Target: +{strategy_info.get('profit_target_pct', 0):.1f}% | Stop: {strategy_info.get('stop_loss_pct', 0):.1f}%")
                
            if 'rationale' in strategy_info:
                print(f"    🧠 Rationale: {strategy_info['rationale'][:80]}...")
            
            total_value += trade['trade_value']
            print()
        
        print(f"📊 {strategy_type} Total Value: ${total_value:,.2f}")
    
    # Strategy summary
    print("\n📈 STRATEGY BREAKDOWN SUMMARY:")
    print("-" * 50)
    
    strategy_stats = {}
    for strategy_type, trade_group in strategy_groups.items():
        count = len(trade_group)
        total_value = sum(t['trade']['trade_value'] for t in trade_group)
        avg_value = total_value / count if count > 0 else 0
        
        strategy_stats[strategy_type] = {
            'count': count,
            'total_value': total_value,
            'avg_value': avg_value,
            'percentage': (count / len(trades)) * 100
        }
        
        print(f"🎯 {strategy_type}:")
        print(f"   Trades: {count} ({strategy_stats[strategy_type]['percentage']:.1f}%)")
        print(f"   Total Value: ${total_value:,.2f}")
        print(f"   Avg Trade Size: ${avg_value:,.2f}")
        print()
    
    # Current positions analysis
    positions = portfolio.get_positions()
    
    if positions:
        print("📋 CURRENT POSITIONS BY STRATEGY:")
        print("-" * 50)
        
        for symbol, pos in positions.items():
            # Find the most recent BUY trade for this symbol to get strategy
            recent_buy = None
            for trade in reversed(trades):
                if trade['symbol'] == symbol and trade['action'] == 'BUY':
                    recent_buy = trade
                    break
            
            if recent_buy and 'strategy_category' in recent_buy:
                strategy_info = recent_buy['strategy_category']
                strategy_type = strategy_info['primary_strategy']
                
                asset_type = "crypto" if '-USD' in symbol else "stock"
                shares_text = f"{pos['shares']:.6f}" if '-USD' in symbol else f"{int(pos['shares'])}"
                
                print(f"📊 {symbol} ({asset_type}) - {strategy_type}")
                print(f"   Holdings: {shares_text} @ ${pos['avg_price']:,.2f}")
                print(f"   Current: ${pos['current_price']:,.2f} | P&L: ${pos['unrealized_pnl']:+.2f} ({pos['unrealized_pnl_pct']:+.2f}%)")
                
                if 'expected_hold_period' in strategy_info:
                    print(f"   Expected Hold: {strategy_info['expected_hold_period']}")
                    
                # Calculate days held
                entry_date = datetime.fromisoformat(recent_buy['timestamp'])
                days_held = (datetime.now() - entry_date).days
                print(f"   Days Held: {days_held}")
                print()
    
    # Strategy performance
    print("🏆 STRATEGY PERFORMANCE INSIGHTS:")
    print("-" * 50)
    
    # Most used strategy
    most_used = max(strategy_stats.items(), key=lambda x: x[1]['count'])
    print(f"🎯 Most Used Strategy: {most_used[0]} ({most_used[1]['count']} trades)")
    
    # Largest allocation strategy
    largest_allocation = max(strategy_stats.items(), key=lambda x: x[1]['total_value'])
    print(f"💰 Largest Allocation: {largest_allocation[0]} (${largest_allocation[1]['total_value']:,.2f})")
    
    # Trading style analysis
    print("\n📊 TRADING STYLE ANALYSIS:")
    print("-" * 50)
    
    swing_pct = strategy_stats.get('Swing Trading', {}).get('percentage', 0)
    position_pct = strategy_stats.get('Position Trading', {}).get('percentage', 0)
    momentum_pct = strategy_stats.get('Momentum', {}).get('percentage', 0)
    long_term_pct = strategy_stats.get('Long Term', {}).get('percentage', 0)
    
    if swing_pct >= 50:
        print("🎯 Primary Style: SWING TRADER")
        print("   • Focus on 2-10 day holds")
        print("   • Capitalize on short-term price movements")
    elif position_pct >= 40:
        print("🎯 Primary Style: POSITION TRADER")  
        print("   • Focus on 2-8 week trends")
        print("   • Medium-term trend following")
    elif momentum_pct >= 30:
        print("🎯 Primary Style: MOMENTUM TRADER")
        print("   • Follow strong price trends")
        print("   • High conviction, shorter holds")
    else:
        print("🎯 Primary Style: DIVERSIFIED TRADER")
        print("   • Mixed strategy approach")
        print("   • Flexible time horizons")
    
    print()
    print("✅ Trade strategy analysis complete!")
    
    return strategy_groups, strategy_stats

def make_new_categorized_trade():
    """
    Make a new trade with full strategy categorization
    """
    
    print("\n🎯 MAKING NEW CATEGORIZED TRADE:")
    print("-" * 50)
    
    portfolio = PaperTradingPortfolio()
    
    # Example: Buy some Tesla with strategy categorization
    symbol = 'TSLA'
    amount = 800
    
    # Get current analysis (simplified for demo)
    import yfinance as yf
    ticker = yf.Ticker(symbol)
    current_price = ticker.history(period="1d")['Close'].iloc[-1]
    
    # Create signal info for categorization
    signal_info = {
        'final_score': 72,  # Strong signal
        'confidence': 'HIGH',
        'action': 'BUY',
        'current_price': current_price
    }
    
    print(f"🚀 Buying ${amount} of {symbol} with strategy categorization...")
    
    # The buy_stock method will now automatically categorize the trade
    result = portfolio.buy_stock(symbol, amount)
    
    if result['success']:
        print(f"✅ {result['message']}")
        
        # Get the latest trade to show categorization
        latest_trade = portfolio.trade_history[-1]
        if 'strategy_category' in latest_trade:
            strategy_info = latest_trade['strategy_category']
            print(f"📋 Strategy: {strategy_info['primary_strategy']}")
            print(f"⏰ Expected Hold: {strategy_info['expected_hold_period']}")
            print(f"🎯 Target: +{strategy_info['profit_target_pct']:.1f}%")
            print(f"🛡️  Stop Loss: {strategy_info['stop_loss_pct']:.1f}%")
            print(f"🧠 Rationale: {strategy_info['rationale']}")
    else:
        print(f"❌ {result['message']}")
    
    # Save the portfolio
    portfolio.save_portfolio_data()

if __name__ == "__main__":
    # Run analysis
    analyze_trade_strategies()
    
    # Optionally make a new categorized trade
    make_new_categorized_trade()