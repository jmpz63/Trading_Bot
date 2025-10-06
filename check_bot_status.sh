#!/bin/bash
# Elite Trading Bot - Quick Status Commands

echo "🤖 ELITE TRADING BOT - STATUS COMMANDS"
echo "======================================"

echo -e "\n1️⃣ CHECK IF BOT IS RUNNING:"
echo "ps aux | grep elite_trading_bot | grep -v grep"

echo -e "\n2️⃣ SHOW BOT PROCESS ID & STATUS:"
echo "pgrep -f elite_trading_bot"

echo -e "\n3️⃣ LIVE LOG MONITORING:"
echo "tail -f elite_bot_24_7.log"

echo -e "\n4️⃣ RECENT LOG ENTRIES:"
echo "tail -20 elite_bot_24_7.log"

echo -e "\n5️⃣ LATEST TRADING DATA:"
echo "tail -5 data/logs/elite_bot_*.json | tail -1"

echo -e "\n6️⃣ COMPREHENSIVE STATUS:"
echo "python3 monitor_elite_bot.py"

echo -e "\n7️⃣ QUICK PORTFOLIO CHECK:"
echo "tail -1 data/logs/elite_bot_*.json | jq '.portfolio_value,.btc_balance,.cash_balance'"

echo -e "\n8️⃣ COUNT DATA POINTS TODAY:"
echo "wc -l data/logs/elite_bot_$(date +%Y%m%d)*.json"

echo -e "\n======================================"

# Execute the most important ones:
echo -e "\n🔍 CURRENT STATUS:"

echo -n "Bot Running: "
if pgrep -f elite_trading_bot > /dev/null; then
    echo "✅ YES (PID: $(pgrep -f elite_trading_bot))"
else
    echo "❌ NO"
fi

echo -n "Latest Data: "
if ls data/logs/elite_bot_*.json 1> /dev/null 2>&1; then
    echo "$(ls -t data/logs/elite_bot_*.json | head -1)"
else
    echo "No log files found"
fi

echo -n "Data Points: "
if ls data/logs/elite_bot_$(date +%Y%m%d)*.json 1> /dev/null 2>&1; then
    wc -l data/logs/elite_bot_$(date +%Y%m%d)*.json 2>/dev/null | head -1
else
    echo "No data today"
fi