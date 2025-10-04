#!/usr/bin/env python3
"""
Daily Paper Trading Runner
Execute daily trading operations with your $10,000 virtual portfolio
"""

import sys
from pathlib import Path
import argparse
from datetime import datetime

# Add the Trade_Bot directory to the path
trade_bot_dir = Path(__file__).parent
sys.path.append(str(trade_bot_dir))

from paper_trading_system import PaperTradingPortfolio, AutoTrader
from enhanced_trading_system import AdvancedMarketAnalyzer, EnhancedSwingAnalyzer
from performance_analytics import TradePerformanceAnalyzer
from email_notifications import TradingEmailNotifier

def run_daily_trading(send_email: bool = False, auto_execute: bool = False):
    """
    Run daily trading session
    """
    
    print("🚀 DAILY PAPER TRADING SESSION")
    print("=" * 70)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize systems
    portfolio = PaperTradingPortfolio()
    market_analyzer = AdvancedMarketAnalyzer()
    swing_analyzer = EnhancedSwingAnalyzer()
    auto_trader = AutoTrader(portfolio)
    analyzer = TradePerformanceAnalyzer()
    
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
            print(f"  {symbol}: {pos['shares']} shares @ ${pos['avg_price']:.2f}")
            print(f"    Current: ${pos['current_price']:.2f} | P&L: ${pos['unrealized_pnl']:+.2f} ({pos['unrealized_pnl_pct']:+.2f}%)")
        print()
    
    # Analyze market opportunities
    print("🔍 ANALYZING MARKET OPPORTUNITIES:")
    print("-" * 50)
    
    # Top stocks to analyze
    symbols_to_analyze = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'TSLA', 'META', 'AMD']
    
    opportunities = []
    
    for symbol in symbols_to_analyze:
        try:
            print(f"Analyzing {symbol}...", end=" ")
            
            # Get market context
            market_context = market_analyzer.get_market_regime()
            
            # Run comprehensive analysis
            analysis = swing_analyzer.comprehensive_analysis(symbol, market_context)
            
            opportunities.append({
                'symbol': symbol,
                'recommendation': analysis.get('action', 'HOLD'),
                'score': analysis.get('final_score', 50),
                'price': analysis.get('current_price', 0),
                'market_regime': market_context.get('regime', 'Unknown'),
                'analysis': analysis
            })
            
            print(f"{analysis.get('action', 'HOLD')} (Score: {analysis.get('final_score', 50):.1f})")
            
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    # Sort opportunities by score
    opportunities.sort(key=lambda x: x['score'], reverse=True)
    
    print()
    print("🎯 TOP TRADING OPPORTUNITIES:")
    print("-" * 50)
    
    buy_opportunities = [opp for opp in opportunities if opp['recommendation'] == 'BUY'][:5]
    sell_opportunities = [opp for opp in opportunities if opp['recommendation'] == 'SELL'][:3]
    
    if buy_opportunities:
        print("🟢 BUY Signals:")
        for opp in buy_opportunities:
            print(f"  {opp['symbol']}: ${opp['price']:.2f} (Score: {opp['score']:.1f}/100)")
    
    if sell_opportunities:
        print("🔴 SELL Signals:")
        for opp in sell_opportunities:
            print(f"  {opp['symbol']}: ${opp['price']:.2f} (Score: {opp['score']:.1f}/100)")
    
    print()
    
    # Auto-execute trades if enabled
    if auto_execute and (buy_opportunities or sell_opportunities):
        print("🤖 AUTO-EXECUTING TRADES:")
        print("-" * 50)
        
        # Execute top buy signal if we have cash
        if buy_opportunities and portfolio.cash_balance > 1000:
            top_buy = buy_opportunities[0]
            trade_amount = min(2000, portfolio.cash_balance * 0.1)  # 10% of cash or $2000, whichever is smaller
            
            print(f"🟢 Buying ${trade_amount:.0f} worth of {top_buy['symbol']}...")
            result = portfolio.buy_stock(top_buy['symbol'], trade_amount)
            
            if result['success']:
                print(f"✅ {result['message']}")
            else:
                print(f"❌ {result['message']}")
        
        # Execute sell signals for positions we own
        for sell_opp in sell_opportunities:
            if sell_opp['symbol'] in positions:
                shares_to_sell = positions[sell_opp['symbol']]['shares'] // 2  # Sell half
                if shares_to_sell > 0:
                    print(f"🔴 Selling {shares_to_sell} shares of {sell_opp['symbol']}...")
                    result = portfolio.sell_stock(sell_opp['symbol'], shares_to_sell)
                    
                    if result['success']:
                        print(f"✅ {result['message']}")
                    else:
                        print(f"❌ {result['message']}")
        
        print()
    
    # Save portfolio state
    portfolio.save_portfolio_data()
    
    # Generate performance report
    print("📊 PERFORMANCE ANALYSIS:")
    print("-" * 50)
    analyzer.print_quick_summary()
    
    # Email notifications if enabled
    if send_email:
        try:
            notifier = TradingEmailNotifier()
            
            # Prepare email content
            email_content = f"""
Daily Trading Report - {datetime.now().strftime('%Y-%m-%d')}

Portfolio Status:
• Total Value: ${portfolio_value:,.2f}
• Cash: ${portfolio.cash_balance:,.2f}
• Total P&L: ${summary['total_pnl']:+.2f} ({summary['total_return_pct']:+.2f}%)

Top Opportunities:
"""
            
            for opp in buy_opportunities[:3]:
                email_content += f"• BUY {opp['symbol']} @ ${opp['price']:.2f} (Score: {opp['score']:.1f})\n"
            
            # Send email
            notifier.send_daily_report("Daily Trading Report", email_content)
            print("📧 Daily report sent via email!")
            
        except Exception as e:
            print(f"📧 Email notification failed: {e}")
    
    print()
    print("✅ Daily trading session complete!")
    print(f"💰 Final Portfolio Value: ${portfolio.get_portfolio_value():,.2f}")
    print(f"📊 Day's P&L: ${summary['total_pnl']:+.2f}")

def show_portfolio_summary():
    """Show detailed portfolio summary"""
    
    portfolio = PaperTradingPortfolio()
    analyzer = TradePerformanceAnalyzer()
    
    print("💰 PORTFOLIO SUMMARY")
    print("=" * 50)
    
    # Basic stats
    portfolio.print_portfolio_status()
    
    print("\n📊 DETAILED PERFORMANCE REPORT:")
    print("-" * 50)
    
    report = analyzer.generate_performance_report()
    print(report)

def main():
    """Main function"""
    
    parser = argparse.ArgumentParser(description='Daily Paper Trading Runner')
    parser.add_argument('--email', action='store_true', help='Send email notifications')
    parser.add_argument('--auto', action='store_true', help='Auto-execute trades')
    parser.add_argument('--summary', action='store_true', help='Show portfolio summary only')
    
    args = parser.parse_args()
    
    if args.summary:
        show_portfolio_summary()
    else:
        run_daily_trading(send_email=args.email, auto_execute=args.auto)

if __name__ == "__main__":
    main()