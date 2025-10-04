#!/usr/bin/env python3
"""
Daily Portfolio Tracker
Tracks portfolio performance daily and logs to APM system
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import json
import subprocess

# Add Trade_Bot to path
sys.path.append('/home/arm1/Trade_Bot')

from paper_trading_system import PaperTradingPortfolio

class DailyPortfolioTracker:
    def __init__(self):
        self.portfolio = PaperTradingPortfolio()
        self.apm_dir = Path("/home/arm1/APM")
        self.tracking_dir = self.apm_dir / "TRADING" / "portfolio_tracking"
        self.daily_logs_dir = self.tracking_dir / "daily_logs"
        
        # Ensure directories exist
        self.tracking_dir.mkdir(parents=True, exist_ok=True)
        self.daily_logs_dir.mkdir(parents=True, exist_ok=True)
    
    def get_portfolio_snapshot(self):
        """Get current portfolio snapshot"""
        
        positions = self.portfolio.get_positions()
        cash_balance = self.portfolio.cash_balance
        
        # Calculate portfolio metrics
        total_invested = 0
        position_data = {}
        
        for symbol, pos in positions.items():
            current_value = pos['shares'] * pos['current_price']
            cost_basis = pos['shares'] * pos['avg_price']
            pnl = current_value - cost_basis
            pnl_pct = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
            
            asset_type = 'crypto' if '-USD' in symbol else 'stock'
            
            position_data[symbol] = {
                'asset_type': asset_type,
                'shares': pos['shares'],
                'avg_cost': pos['avg_price'],
                'current_price': pos['current_price'],
                'current_value': current_value,
                'cost_basis': cost_basis,
                'unrealized_pnl': pnl,
                'unrealized_pnl_pct': pnl_pct
            }
            
            total_invested += current_value
        
        total_portfolio_value = cash_balance + total_invested
        total_return = total_portfolio_value - 10000
        total_return_pct = (total_return / 10000) * 100
        
        # Get trade count for today
        today = datetime.now().strftime('%Y-%m-%d')
        trades_today = [t for t in self.portfolio.trade_history 
                       if t['timestamp'].startswith(today)]
        
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'date': today,
            'portfolio_metrics': {
                'cash_balance': cash_balance,
                'total_invested': total_invested,
                'total_portfolio_value': total_portfolio_value,
                'total_return': total_return,
                'total_return_pct': total_return_pct,
                'cash_allocation_pct': (cash_balance / total_portfolio_value) * 100,
                'invested_allocation_pct': (total_invested / total_portfolio_value) * 100
            },
            'positions': position_data,
            'daily_stats': {
                'trades_today': len(trades_today),
                'total_positions': len(positions),
                'crypto_positions': len([p for p in positions if '-USD' in p]),
                'stock_positions': len([p for p in positions if '-USD' not in p])
            }
        }
        
        return snapshot
    
    def save_daily_log(self, snapshot):
        """Save daily snapshot to log file"""
        
        date_str = snapshot['date']
        log_file = self.daily_logs_dir / f"{date_str}_portfolio.json"
        
        with open(log_file, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        return log_file
    
    def update_apm_tracking(self, snapshot):
        """Update APM tracking files"""
        
        # Main tracking file
        tracking_file = self.tracking_dir / "portfolio_performance.md"
        
        # Create or update the tracking file
        if not tracking_file.exists():
            self.create_initial_tracking_file(tracking_file)
        
        # Append daily entry
        self.append_daily_entry(tracking_file, snapshot)
        
        # Update summary file
        self.update_summary_file(snapshot)
    
    def create_initial_tracking_file(self, tracking_file):
        """Create initial APM tracking file"""
        
        content = """# Portfolio Performance Tracking

## Overview
Daily tracking of $10K paper trading portfolio performance.

**Portfolio Started**: October 4, 2025
**Initial Balance**: $10,000.00
**Strategy**: Multi-asset (Stocks + Crypto) with automated categorization

## Trading Strategy Categories
- **Position Trading**: 2-8 week holds, medium-term trends
- **Swing Trading**: 2-10 day holds, short-term momentum
- **Momentum Trading**: Strong trend following
- **Long Term**: Buy and hold positions

---

## Daily Performance Log

"""
        
        with open(tracking_file, 'w') as f:
            f.write(content)
    
    def append_daily_entry(self, tracking_file, snapshot):
        """Append daily entry to tracking file"""
        
        date_str = snapshot['date']
        metrics = snapshot['portfolio_metrics']
        positions = snapshot['positions']
        stats = snapshot['daily_stats']
        
        # Format positions for display
        positions_text = ""
        if positions:
            positions_text = "\n**Current Positions:**\n"
            for symbol, pos in positions.items():
                asset_type = pos['asset_type'].upper()
                if pos['asset_type'] == 'crypto':
                    shares_text = f"{pos['shares']:.6f} coins"
                else:
                    shares_text = f"{int(pos['shares'])} shares"
                
                pnl_indicator = "🟢" if pos['unrealized_pnl'] > 0 else "🔴" if pos['unrealized_pnl'] < 0 else "⚪"
                
                positions_text += f"- **{symbol}** ({asset_type}): {shares_text} @ ${pos['current_price']:,.2f} "
                positions_text += f"| Value: ${pos['current_value']:,.2f} "
                positions_text += f"| P&L: ${pos['unrealized_pnl']:+,.2f} ({pos['unrealized_pnl_pct']:+.2f}%) {pnl_indicator}\n"
        
        # Performance indicator
        perf_indicator = "🟢" if metrics['total_return'] > 0 else "🔴" if metrics['total_return'] < 0 else "⚪"
        
        daily_entry = f"""
### {date_str} {perf_indicator}

**Portfolio Value**: ${metrics['total_portfolio_value']:,.2f} | **Return**: ${metrics['total_return']:+,.2f} ({metrics['total_return_pct']:+.2f}%)  
**Cash**: ${metrics['cash_balance']:,.2f} ({metrics['cash_allocation_pct']:.1f}%) | **Invested**: ${metrics['total_invested']:,.2f} ({metrics['invested_allocation_pct']:.1f}%)  
**Trades Today**: {stats['trades_today']} | **Total Positions**: {stats['total_positions']} ({stats['crypto_positions']} crypto, {stats['stock_positions']} stocks)

{positions_text}
---
"""
        
        with open(tracking_file, 'a') as f:
            f.write(daily_entry)
    
    def update_summary_file(self, snapshot):
        """Update portfolio summary file"""
        
        summary_file = self.tracking_dir / "portfolio_summary.md"
        date_str = snapshot['date']
        metrics = snapshot['portfolio_metrics']
        
        # Calculate days trading
        start_date = datetime(2025, 10, 4)  # Portfolio start date
        current_date = datetime.now()
        days_trading = (current_date - start_date).days + 1
        
        # Performance metrics
        annualized_return = (metrics['total_return_pct'] / days_trading) * 365 if days_trading > 0 else 0
        
        summary_content = f"""# Portfolio Summary

**Last Updated**: {snapshot['timestamp']}  
**Portfolio Start**: October 4, 2025  
**Days Trading**: {days_trading}

## Current Performance
- **Portfolio Value**: ${metrics['total_portfolio_value']:,.2f}
- **Total Return**: ${metrics['total_return']:+,.2f} ({metrics['total_return_pct']:+.2f}%)
- **Annualized Return**: {annualized_return:+.2f}%

## Current Allocation
- **Cash**: ${metrics['cash_balance']:,.2f} ({metrics['cash_allocation_pct']:.1f}%)
- **Invested**: ${metrics['total_invested']:,.2f} ({metrics['invested_allocation_pct']:.1f}%)

## Position Summary
- **Total Positions**: {len(snapshot['positions'])}
- **Crypto Positions**: {snapshot['daily_stats']['crypto_positions']}
- **Stock Positions**: {snapshot['daily_stats']['stock_positions']}

## Asset Breakdown
"""
        
        # Add individual positions
        if snapshot['positions']:
            for symbol, pos in snapshot['positions'].items():
                asset_type = pos['asset_type'].upper()
                value_pct = (pos['current_value'] / metrics['total_portfolio_value']) * 100
                pnl_indicator = "🟢" if pos['unrealized_pnl'] > 0 else "🔴" if pos['unrealized_pnl'] < 0 else "⚪"
                
                summary_content += f"- **{symbol}** ({asset_type}): ${pos['current_value']:,.2f} ({value_pct:.1f}%) "
                summary_content += f"| P&L: ${pos['unrealized_pnl']:+,.2f} ({pos['unrealized_pnl_pct']:+.2f}%) {pnl_indicator}\n"
        
        summary_content += f"""

## Strategy Analysis
Portfolio demonstrates **conservative approach** with high cash allocation, suitable for volatile market conditions.

**Last Daily Log**: [daily_logs/{date_str}_portfolio.json](daily_logs/{date_str}_portfolio.json)
"""
        
        with open(summary_file, 'w') as f:
            f.write(summary_content)
    
    def commit_to_git(self, snapshot):
        """Commit changes to git"""
        
        try:
            os.chdir(self.apm_dir)
            
            # Add files
            subprocess.run(['git', 'add', 'TRADING/'], check=True, capture_output=True)
            
            # Create commit message
            metrics = snapshot['portfolio_metrics']
            commit_msg = f"📊 Daily Portfolio Update {snapshot['date']}: ${metrics['total_portfolio_value']:,.2f} ({metrics['total_return_pct']:+.2f}%)"
            
            # Commit
            result = subprocess.run(['git', 'commit', '-m', commit_msg], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Committed to git: {commit_msg}")
                
                # Push to remote
                push_result = subprocess.run(['git', 'push'], capture_output=True, text=True)
                if push_result.returncode == 0:
                    print("✅ Pushed to remote repository")
                else:
                    print(f"⚠️ Failed to push: {push_result.stderr}")
                    
            else:
                print(f"ℹ️ No changes to commit: {result.stdout}")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Git error: {e}")
        except Exception as e:
            print(f"❌ Error with git operations: {e}")
    
    def run_daily_tracking(self):
        """Run complete daily tracking process"""
        
        print("📊 DAILY PORTFOLIO TRACKING")
        print("=" * 50)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # Get portfolio snapshot
            print("📋 Getting portfolio snapshot...")
            snapshot = self.get_portfolio_snapshot()
            
            # Save daily log
            print("💾 Saving daily log...")
            log_file = self.save_daily_log(snapshot)
            print(f"✅ Saved: {log_file}")
            
            # Update APM tracking
            print("📝 Updating APM tracking...")
            self.update_apm_tracking(snapshot)
            print("✅ APM files updated")
            
            # Display summary
            self.display_daily_summary(snapshot)
            
            # Commit to git
            print("📤 Committing to git...")
            self.commit_to_git(snapshot)
            
            print("\n✅ Daily portfolio tracking complete!")
            
        except Exception as e:
            print(f"❌ Error during tracking: {e}")
            raise
    
    def display_daily_summary(self, snapshot):
        """Display daily summary"""
        
        print(f"\n📊 DAILY SUMMARY - {snapshot['date']}")
        print("-" * 40)
        
        metrics = snapshot['portfolio_metrics']
        positions = snapshot['positions']
        
        # Portfolio metrics
        perf_indicator = "🟢" if metrics['total_return'] > 0 else "🔴" if metrics['total_return'] < 0 else "⚪"
        print(f"💰 Portfolio Value: ${metrics['total_portfolio_value']:,.2f} {perf_indicator}")
        print(f"📊 Total Return: ${metrics['total_return']:+,.2f} ({metrics['total_return_pct']:+.2f}%)")
        print(f"💵 Cash: ${metrics['cash_balance']:,.2f} ({metrics['cash_allocation_pct']:.1f}%)")
        print(f"📈 Invested: ${metrics['total_invested']:,.2f} ({metrics['invested_allocation_pct']:.1f}%)")
        
        # Positions summary
        if positions:
            print(f"\n📋 Positions ({len(positions)}):")
            for symbol, pos in positions.items():
                asset_type = pos['asset_type'].upper()
                pnl_indicator = "🟢" if pos['unrealized_pnl'] > 0 else "🔴" if pos['unrealized_pnl'] < 0 else "⚪"
                print(f"  {symbol} ({asset_type}): ${pos['current_value']:,.2f} | P&L: ${pos['unrealized_pnl']:+,.2f} {pnl_indicator}")
        
        # Daily stats
        stats = snapshot['daily_stats']
        if stats['trades_today'] > 0:
            print(f"\n🎯 Made {stats['trades_today']} trade(s) today")

def create_daily_cron_job():
    """Create cron job for daily tracking"""
    
    script_path = "/home/arm1/Trade_Bot/daily_portfolio_tracker.py"
    
    # Cron job to run at 6 PM daily
    cron_command = f"0 18 * * * cd /home/arm1/Trade_Bot && /usr/bin/python3 {script_path} >> /home/arm1/Trade_Bot/logs/daily_tracker.log 2>&1"
    
    print(f"📅 To set up daily tracking, add this cron job:")
    print(f"Run: crontab -e")
    print(f"Add: {cron_command}")
    print()
    print("This will run daily portfolio tracking at 6 PM every day.")

if __name__ == "__main__":
    # Create logs directory
    logs_dir = Path("/home/arm1/Trade_Bot/logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Run daily tracking
    tracker = DailyPortfolioTracker()
    tracker.run_daily_tracking()
    
    # Show cron setup instructions
    print()
    create_daily_cron_job()