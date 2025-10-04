#!/usr/bin/env python3
"""
Quick Portfolio Status Check
Shows current portfolio and recent performance from APM tracking
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

def show_portfolio_status():
    """Show current portfolio status from APM tracking"""
    
    apm_dir = Path("/home/arm1/APM")
    tracking_dir = apm_dir / "TRADING" / "portfolio_tracking"
    
    print("📊 PORTFOLIO STATUS FROM APM TRACKING")
    print("=" * 55)
    
    # Show summary file
    summary_file = tracking_dir / "portfolio_summary.md"
    
    if summary_file.exists():
        print("📋 CURRENT SUMMARY:")
        print("-" * 40)
        
        with open(summary_file, 'r') as f:
            lines = f.readlines()
        
        # Extract key metrics
        for line in lines:
            if "**Last Updated**:" in line or \
               "**Portfolio Value**:" in line or \
               "**Total Return**:" in line or \
               "**Cash**:" in line or \
               "**Invested**:" in line:
                print(line.strip())
        
        print()
    
    # Show recent daily logs
    daily_logs_dir = tracking_dir / "daily_logs"
    
    if daily_logs_dir.exists():
        print("📅 RECENT DAILY PERFORMANCE:")
        print("-" * 40)
        
        # Get last 7 days of logs
        log_files = sorted(daily_logs_dir.glob("*.json"), reverse=True)[:7]
        
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    data = json.load(f)
                
                date = data['date']
                metrics = data['portfolio_metrics']
                
                # Performance indicator
                perf_icon = "🟢" if metrics['total_return'] > 0 else "🔴" if metrics['total_return'] < 0 else "⚪"
                
                print(f"{date} {perf_icon} | ${metrics['total_portfolio_value']:,.2f} | "
                      f"{metrics['total_return_pct']:+.2f}% | "
                      f"Cash: {metrics['cash_allocation_pct']:.1f}% | "
                      f"Trades: {data['daily_stats']['trades_today']}")
                
            except Exception as e:
                print(f"Error reading {log_file.name}: {e}")
        
        print()
    
    # Show APM file locations
    print("📁 APM TRACKING FILES:")
    print("-" * 40)
    print(f"📊 Portfolio Performance: {tracking_dir}/portfolio_performance.md")
    print(f"📋 Portfolio Summary: {tracking_dir}/portfolio_summary.md")
    print(f"📅 Daily Logs: {tracking_dir}/daily_logs/")
    print()
    
    # Show git status
    print("📤 GIT STATUS:")
    print("-" * 40)
    
    import subprocess
    import os
    
    try:
        os.chdir(apm_dir)
        result = subprocess.run(['git', 'log', '--oneline', '-5'], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Recent commits:")
            for line in result.stdout.strip().split('\n')[:3]:
                if '📊' in line:  # Portfolio commits
                    print(f"  {line}")
        else:
            print("No git history available")
            
    except Exception as e:
        print(f"Error checking git status: {e}")

if __name__ == "__main__":
    show_portfolio_status()