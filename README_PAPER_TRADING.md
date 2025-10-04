# 🎯 Trading Bot Paper Trading System

Complete algorithmic trading system with **$10,000 virtual money** for risk-free strategy testing!

## 🚀 Quick Start

```bash
# Basic paper trading
python daily_trading.py

# With email notifications
python daily_trading.py --email

# Auto-execute trades
python daily_trading.py --auto

# Portfolio summary only
python daily_trading.py --summary
```

## 💰 What You Get

### 📊 Paper Trading Portfolio
- Start with **$10,000 virtual money**
- Real-time stock prices via Yahoo Finance
- Track every trade with timestamp, price, P&L
- **Shows if you're NET POSITIVE or NEGATIVE** daily/weekly/monthly
- Complete trade history and performance analytics

### 🎯 Advanced Analysis Engine
- **68.3/100 scores** for top opportunities
- Multi-factor analysis: Technical + Fundamental + Market Regime
- MACD, RSI, Bollinger Bands, Moving Averages
- Kelly Criterion position sizing
- Market regime detection (Bull/Bear/Sideways)

### 📈 Real-Time Tracking
- Current portfolio value
- Cash vs invested allocation
- Unrealized P&L for each position
- Daily/weekly/monthly performance reports
- Win rate, profit factor, Sharpe ratio

## 🔧 System Components

### Core Files
- `daily_trading.py` - Main trading runner
- `paper_trading_system.py` - Portfolio management ($10K virtual money)
- `enhanced_trading_system.py` - Advanced market analysis
- `performance_analytics.py` - Comprehensive trade tracking
- `email_notifications.py` - Gmail alerts setup

### Market Integration
- **S&P 500**: SPY, QQQ, major stocks via Yahoo Finance
- **Crypto**: 100+ exchanges via CCXT (Bitcoin, Ethereum, etc.)
- **Real-time data**: Live prices and market data

## 📊 Daily Workflow

1. **Market Analysis** - System analyzes 10+ stocks automatically
2. **Signal Generation** - BUY/SELL recommendations with confidence scores
3. **Risk Management** - Position sizing based on volatility and portfolio size
4. **Trade Execution** - Paper trades with real-time prices
5. **Performance Tracking** - Updated P&L, portfolio value, statistics
6. **Reporting** - Shows if you're profitable (NET POSITIVE/NEGATIVE)

## 📈 Performance Metrics

The system tracks everything you requested:
- **Total Portfolio Value**: Current worth vs $10,000 starting capital
- **Daily P&L**: Today's gains/losses
- **Total Return**: Percentage return since start
- **Win Rate**: Percentage of profitable trades
- **Realized P&L**: Actual profits from completed trades
- **Unrealized P&L**: Paper profits from open positions

## 🎯 Example Output

```
💰 CURRENT PORTFOLIO STATUS:
📈 Total Value: $10,247.83
💵 Cash: $4,567.21
📊 Invested: $5,680.62
📊 Total P&L: $+247.83
📊 Return: +2.48%
🟢 Status: NET POSITIVE! 🎉

📋 CURRENT POSITIONS:
SPY: 5 shares @ $669.21
  Current: $672.45 | P&L: $+16.20 (+0.48%)
AAPL: 10 shares @ $258.02
  Current: $261.33 | P&L: $+33.10 (+1.28%)
```

## 🎛️ Dashboard (Optional)

```bash
# Install dashboard requirements
python setup_dashboard.py

# Launch web dashboard
./launch_dashboard.sh
```

Access at http://localhost:8501 for:
- Interactive portfolio charts
- Real-time position monitoring
- Quick trading interface
- Performance visualizations

## 📧 Email Notifications

Set up Gmail notifications:

1. Enable 2FA on Gmail
2. Generate app password
3. Set environment variables:
```bash
export GMAIL_USER="your.email@gmail.com"
export GMAIL_PASSWORD="your_app_password"
```

## 🎯 Trading Strategies Supported

- **Swing Trading** (2-6 weeks) - Primary focus
- **Position Trading** (1-3 months) - Medium-term trends
- **Buy & Hold** (3+ months) - Long-term investing

## 📊 Risk Management Features

- **Position Sizing**: Kelly Criterion with volatility adjustment
- **Stop Losses**: Dynamic based on ATR and volatility
- **Portfolio Limits**: Maximum position sizes and exposure
- **Cash Management**: Maintains minimum cash reserves

## 🔍 Analysis Scoring

Each stock gets scored 0-100 based on:
- **Technical Analysis** (40%): MACD, RSI, Moving Averages, Bollinger Bands
- **Fundamental Screening** (30%): P/E, Growth, Financial Health
- **Market Context** (20%): Market regime, sector rotation, VIX
- **Risk Assessment** (10%): Volatility, beta, drawdown risk

## 📈 Performance Reports

Generate detailed reports:

```bash
python -c "
from performance_analytics import TradePerformanceAnalyzer
analyzer = TradePerformanceAnalyzer()
print(analyzer.generate_performance_report())
"
```

Shows:
- Win rate and profit factor
- Best/worst trades
- Sharpe ratio and volatility
- Maximum drawdown
- Monthly/weekly performance
- **Tells you if you're NET POSITIVE or NEGATIVE!**

## 🎯 Key Benefits

✅ **Risk-Free Learning** - $10,000 virtual money  
✅ **Real Market Data** - Live prices and conditions  
✅ **Complete Tracking** - Every trade recorded with P&L  
✅ **Professional Analysis** - Multi-factor scoring system  
✅ **Performance Monitoring** - Know if you're profitable!  
✅ **Email Alerts** - Never miss opportunities  
✅ **Extensible** - Easy to add new strategies  

## 🚀 Next Steps

1. **Start Trading**: Run `python daily_trading.py` to begin
2. **Monitor Performance**: Check if you're NET POSITIVE daily
3. **Analyze Results**: Use performance reports to improve
4. **Scale Up**: Apply successful strategies with real money (when ready!)

## 💡 Pro Tips

- **Focus on Quality**: Better to make fewer, higher-confidence trades
- **Risk Management**: Never risk more than 2-5% per trade
- **Track Everything**: The system logs all trades for analysis
- **Stay Disciplined**: Follow the signals and stick to your strategy
- **Review Regularly**: Use performance reports to identify patterns

---

## Installation & Setup

```bash
# Clone repository
git clone https://github.com/jmpz63/Trading_Bot.git
cd Trading_Bot

# Install dependencies
pip install -r requirements.txt

# Start paper trading
python daily_trading.py
```

## Configuration

### Optional API Keys
Add to `.env` file:
```env
# Email notifications (optional)  
GMAIL_USER=your.email@gmail.com
GMAIL_PASSWORD=your_app_password

# Cryptocurrency exchanges (optional)
BINANCE_API_KEY=your_key
BINANCE_SECRET=your_secret
```

## Disclaimer

This software is for educational purposes. Past performance doesn't guarantee future results. Always do your own research before making investment decisions.

---

**Remember**: This system tracks your $10,000 virtual portfolio and shows you exactly whether you're NET POSITIVE or NEGATIVE at any time. Perfect for learning trading strategies without financial risk!

🎯 **Your Goal**: Turn that $10,000 into $12,000+ while maintaining good risk management!