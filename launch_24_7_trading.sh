#!/bin/bash
# 24/7 Elite Trading Bot Launcher
# Runs the elite bot for 7 days (10,080 minutes) with APM workflow

echo "🚀 LAUNCHING 24/7 ELITE TRADING BOT"
echo "Duration: 7 days (10,080 minutes)"
echo "APM Workflow: ENABLED"
echo "Data Logging: ENABLED"
echo "Git Auto-Commit: ENABLED"

cd /home/arm1/Trade_Bot

# Run for 7 days (10080 minutes)
echo "10080" | python3 scripts/elite_trading_bot.py

echo "✅ 24/7 Trading session completed!"