#!/usr/bin/env python3
"""
Combined Stock + Crypto Paper Trading
Execute trades in both traditional markets and cryptocurrency
"""

import sys
from pathlib import Path
from datetime import datetime

# Add the Trade_Bot directory to the path
trade_bot_dir = Path(__file__).parent
sys.path.append(str(trade_bot_dir))

from paper_trading_system import PaperTradingPortfolio
from enhanced_trading_system import AdvancedMarketAnalyzer, EnhancedSwingAnalyzer
from crypto_analyzer import CryptoAnalyzer
from performance_analytics import TradePerformanceAnalyzer

def run_combined_trading_session():
    """
    Run comprehensive trading session with stocks and crypto
    """
    
    print("🚀 COMBINED STOCK + CRYPTO TRADING SESSION")
    print("=" * 70)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize systems
    portfolio = PaperTradingPortfolio()
    market_analyzer = AdvancedMarketAnalyzer()
    swing_analyzer = EnhancedSwingAnalyzer()
    crypto_analyzer = CryptoAnalyzer()
    
    # Show current portfolio status
    print("💰 CURRENT PORTFOLIO STATUS:")
    print("-" * 50)
    portfolio_value = portfolio.get_portfolio_value()
    summary = portfolio.get_portfolio_summary()
    
    print(f"📈 Total Value: ${portfolio_value:,.2f}")
    print(f"💵 Cash: ${portfolio.cash_balance:,.2f}")
    print(f"📊 Invested: ${summary['invested_value']:,.2f}")
    print(f"📊 Total P&L: ${summary['total_pnl']:+.2f}")
    print(f"📊 Return: {summary['total_return_pct']:+.2f}%")
    
    if summary['total_pnl'] > 0:
        print("🟢 Status: NET POSITIVE! 🎉")
    elif summary['total_pnl'] < 0:
        print("🔴 Status: NET NEGATIVE")
    else:
        print("🟡 Status: BREAKEVEN")
    
    print()
    
    # Show current positions
    positions = portfolio.get_positions()
    if positions:
        print("📋 CURRENT POSITIONS:")
        print("-" * 50)
        for symbol, pos in positions.items():
            asset_type = "crypto" if '-USD' in symbol else "stock"
            shares_text = f"{pos['shares']:.6f}" if '-USD' in symbol else f"{int(pos['shares'])}"
            print(f"  {symbol} ({asset_type}): {shares_text} @ ${pos['avg_price']:.2f}")
            print(f"    Current: ${pos['current_price']:.2f} | P&L: ${pos['unrealized_pnl']:+.2f} ({pos['unrealized_pnl_pct']:+.2f}%)")
        print()
    
    # 1. ANALYZE STOCK MARKET OPPORTUNITIES
    print("📊 STOCK MARKET ANALYSIS:")
    print("-" * 50)
    
    # Get market context
    market_context = market_analyzer.get_market_regime()
    print(f"Market Regime: {market_context.get('regime', 'Unknown')}")
    
    # Analyze top stocks
    stock_symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA']
    stock_opportunities = []
    
    for symbol in stock_symbols:
        try:
            print(f"Analyzing {symbol}...", end=" ")
            analysis = swing_analyzer.comprehensive_analysis(symbol, market_context)
            
            stock_opportunities.append({
                'symbol': symbol,
                'type': 'stock',
                'recommendation': analysis.get('action', 'HOLD'),
                'score': analysis.get('final_score', 50),
                'price': analysis.get('current_price', 0),
                'analysis': analysis
            })
            
            print(f"{analysis.get('action', 'HOLD')} (Score: {analysis.get('final_score', 50):.1f})")
            
        except Exception as e:
            print(f"Error: {e}")
    
    print()
    
    # 2. ANALYZE CRYPTO OPPORTUNITIES
    print("🪙 CRYPTOCURRENCY ANALYSIS:")
    print("-" * 50)
    
    crypto_opportunities = crypto_analyzer.scan_crypto_opportunities()
    
    # Convert crypto opportunities to match stock format
    crypto_opps_formatted = []
    for opp in crypto_opportunities:
        crypto_opps_formatted.append({
            'symbol': opp['symbol'],
            'type': 'crypto',
            'recommendation': opp['recommendation'],
            'score': opp['score'],
            'price': opp['current_price'],
            'analysis': opp
        })
    
    print()
    
    # 3. COMBINE AND RANK ALL OPPORTUNITIES
    all_opportunities = stock_opportunities + crypto_opps_formatted
    all_opportunities.sort(key=lambda x: x['score'], reverse=True)
    
    print("🎯 TOP COMBINED OPPORTUNITIES:")
    print("-" * 50)
    
    # Show top BUY signals
    buy_opportunities = [opp for opp in all_opportunities if opp['recommendation'] == 'BUY'][:8]
    
    if buy_opportunities:
        print("🟢 TOP BUY SIGNALS:")
        for i, opp in enumerate(buy_opportunities[:5], 1):
            asset_type = opp['type'].upper()
            print(f"  {i}. {opp['symbol']} ({asset_type}): ${opp['price']:,.2f} (Score: {opp['score']:.1f}/100)")
        print()
    
    # 4. EXECUTE SOME TRADES
    print("🎯 EXECUTING TRADES:")
    print("-" * 50)
    
    trades_executed = []
    
    # Execute top 3 buy signals if we have enough cash
    available_cash = portfolio.cash_balance
    
    if available_cash > 3000 and buy_opportunities:  # Need at least $3000 for diversified trades
        
        # Trade 1: Top stock opportunity
        top_stocks = [opp for opp in buy_opportunities if opp['type'] == 'stock'][:1]
        if top_stocks:
            stock_opp = top_stocks[0]
            trade_amount = min(1500, available_cash * 0.15)  # 15% of portfolio or $1500
            
            print(f"🟢 STOCK: Buying ${trade_amount:.0f} of {stock_opp['symbol']}...")
            result = portfolio.buy_stock(stock_opp['symbol'], trade_amount)
            
            if result['success']:
                print(f"✅ {result['message']}")
                trades_executed.append(result)
                available_cash -= result['cost']
            else:
                print(f"❌ {result['message']}")
        
        # Trade 2: Top crypto opportunity
        top_cryptos = [opp for opp in buy_opportunities if opp['type'] == 'crypto'][:1]
        if top_cryptos and available_cash > 1000:
            crypto_opp = top_cryptos[0]
            trade_amount = min(1000, available_cash * 0.1)  # 10% of portfolio or $1000
            
            crypto_name = crypto_opp['symbol'].replace('-USD', '')
            print(f"🪙 CRYPTO: Buying ${trade_amount:.0f} of {crypto_name}...")
            result = portfolio.buy_crypto(crypto_opp['symbol'], trade_amount)
            
            if result['success']:
                print(f"✅ {result['message']}")
                trades_executed.append(result)
                available_cash -= result['cost']
            else:
                print(f"❌ {result['message']}")
        
        # Trade 3: Second best overall opportunity
        remaining_opps = buy_opportunities[1:2]  # Second best
        if remaining_opps and available_cash > 500:
            second_opp = remaining_opps[0]
            trade_amount = min(800, available_cash * 0.08)  # 8% of portfolio or $800
            
            asset_type = "crypto" if second_opp['type'] == 'crypto' else "stock"
            print(f"🎲 DIVERSIFY: Buying ${trade_amount:.0f} of {second_opp['symbol']} ({asset_type})...")
            
            if second_opp['type'] == 'crypto':
                result = portfolio.buy_crypto(second_opp['symbol'], trade_amount)
            else:
                result = portfolio.buy_stock(second_opp['symbol'], trade_amount)
            
            if result['success']:
                print(f"✅ {result['message']}")
                trades_executed.append(result)
            else:
                print(f"❌ {result['message']}")
    
    else:
        print("💡 Insufficient cash for diversified trading (need $3000+ available)")
        print(f"Current available: ${available_cash:,.2f}")
    
    print()
    
    # 5. UPDATED PORTFOLIO STATUS
    print("📊 UPDATED PORTFOLIO STATUS:")
    print("-" * 50)
    
    # Save portfolio state
    portfolio.save_portfolio_data()
    
    # Get updated values
    new_portfolio_value = portfolio.get_portfolio_value()
    new_summary = portfolio.get_portfolio_summary()
    
    print(f"📈 Total Value: ${new_portfolio_value:,.2f}")
    print(f"💵 Cash: ${portfolio.cash_balance:,.2f}")
    print(f"📊 Invested: ${new_summary['invested_value']:,.2f}")
    print(f"📊 Total P&L: ${new_summary['total_pnl']:+.2f}")
    print(f"📊 Return: {new_summary['total_return_pct']:+.2f}%")
    
    if new_summary['total_pnl'] > 0:
        print("🟢 Status: NET POSITIVE! 🎉")
    elif new_summary['total_pnl'] < 0:
        print("🔴 Status: NET NEGATIVE")
    else:
        print("🟡 Status: BREAKEVEN")
    
    # Show new positions
    new_positions = portfolio.get_positions()
    if new_positions:
        print()
        print("📋 UPDATED POSITIONS:")
        print("-" * 50)
        for symbol, pos in new_positions.items():
            asset_type = "crypto" if '-USD' in symbol else "stock"
            shares_text = f"{pos['shares']:.6f}" if '-USD' in symbol else f"{int(pos['shares'])}"
            print(f"  {symbol} ({asset_type}): {shares_text} @ ${pos['avg_price']:.2f}")
            print(f"    Current: ${pos['current_price']:.2f} | P&L: ${pos['unrealized_pnl']:+.2f} ({pos['unrealized_pnl_pct']:+.2f}%)")
    
    print()
    
    # 6. TRADING SUMMARY
    print("📋 TRADING SESSION SUMMARY:")
    print("-" * 50)
    print(f"🎯 Trades Executed: {len(trades_executed)}")
    
    if trades_executed:
        total_invested = sum(trade['cost'] for trade in trades_executed)
        print(f"💰 Total Invested: ${total_invested:,.2f}")
        print(f"📊 Portfolio Change: ${new_portfolio_value - portfolio_value:+.2f}")
        
        print("\n🔥 Trades Made:")
        for trade in trades_executed:
            print(f"  • {trade['message']}")
    else:
        print("💡 No trades executed this session")
    
    print()
    print("✅ Combined stock + crypto trading session complete!")
    print(f"💰 Final Portfolio Value: ${new_portfolio_value:,.2f}")
    
    return {
        'portfolio_value': new_portfolio_value,
        'trades_executed': len(trades_executed),
        'pnl': new_summary['total_pnl'],
        'return_pct': new_summary['total_return_pct']
    }

if __name__ == "__main__":
    run_combined_trading_session()