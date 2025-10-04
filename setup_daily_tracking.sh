#!/bin/bash
# Setup Daily Portfolio Tracking Automation

echo "🔧 Setting up automated daily portfolio tracking..."

# Create cron job for daily portfolio tracking
CRON_JOB="0 18 * * * cd /home/arm1/Trade_Bot && /usr/bin/python3 /home/arm1/Trade_Bot/daily_portfolio_tracker.py >> /home/arm1/Trade_Bot/logs/daily_tracker.log 2>&1"

# Add to crontab (avoiding duplicates)
(crontab -l 2>/dev/null | grep -v "daily_portfolio_tracker.py"; echo "$CRON_JOB") | crontab -

echo "✅ Daily portfolio tracking cron job added!"
echo "📅 Will run daily at 6:00 PM"
echo ""

# Show current cron jobs
echo "📋 Current cron jobs:"
crontab -l | grep -E "(daily_portfolio|Trade_Bot)" || echo "No trading-related cron jobs found"

echo ""
echo "📊 Portfolio tracking setup complete!"
echo ""
echo "📁 Files created:"
echo "  • /home/arm1/Trade_Bot/daily_portfolio_tracker.py - Main tracker"
echo "  • /home/arm1/Trade_Bot/check_portfolio_apm.py - Status checker"
echo "  • /home/arm1/APM/TRADING/portfolio_tracking/ - APM tracking files"
echo ""
echo "🎯 Commands available:"
echo "  python3 daily_portfolio_tracker.py  - Run tracking manually"
echo "  python3 check_portfolio_apm.py      - Check current status"