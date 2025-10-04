"""
Email Notification System for Trading Bot
Sends alerts for high-confidence trading signals and portfolio updates
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List
import os

class TradingEmailNotifier:
    """
    Email notification system for trading alerts
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize email notifier
        
        config should contain:
        - smtp_server: Gmail SMTP server (smtp.gmail.com)
        - smtp_port: 587 for TLS
        - sender_email: Your Gmail address
        - sender_password: App password (not regular Gmail password)
        - recipient_email: Where to send alerts
        """
        
        self.config = config or {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': os.getenv('TRADING_EMAIL', ''),
            'sender_password': os.getenv('TRADING_EMAIL_PASSWORD', ''),
            'recipient_email': os.getenv('TRADING_RECIPIENT_EMAIL', '')
        }
        
        self.enabled = all([
            self.config['sender_email'],
            self.config['sender_password'],
            self.config['recipient_email']
        ])
    
    def send_daily_signals_email(self, signals: List[Dict], market_context: Dict):
        """Send daily trading signals email"""
        
        if not self.enabled:
            print("📧 Email not configured - skipping email notification")
            return False
        
        subject = f"🎯 Daily Trading Signals - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Build email content
        body = f"""
🎯 DAILY TRADING SIGNALS REPORT
{'='*50}
📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌍 Market Regime: {market_context.get('regime', 'UNKNOWN')}
📊 VIX Level: {market_context.get('vix', 'N/A')}
💡 Trading Advice: {market_context.get('trading_advice', 'N/A')}

"""
        
        # Strong buy signals
        buy_signals = [s for s in signals if 'BUY' in s['recommendation']['action']]
        if buy_signals:
            body += "🟢 TOP BUY OPPORTUNITIES:\n"
            body += "-" * 40 + "\n"
            
            for signal in buy_signals[:3]:  # Top 3
                rec = signal['recommendation']
                body += f"📈 {signal['symbol']} - {rec['action']}\n"
                body += f"   💰 Price: ${signal['current_price']:.2f}\n"
                body += f"   📊 Score: {signal['final_score']:.1f}/100\n"
                body += f"   💼 Position: {rec['position_size_pct']:.1f}% of portfolio\n"
                body += f"   🛡️  Stop Loss: {rec['stop_loss_pct']}%\n"
                body += f"   ⏰ Hold: {rec['hold_period']}\n"
                body += f"   📝 Key Reason: {rec['key_reasons'][0] if rec['key_reasons'] else 'N/A'}\n\n"
        
        # Sell signals
        sell_signals = [s for s in signals if 'SELL' in s['recommendation']['action']]
        if sell_signals:
            body += "🔴 SELL/AVOID ALERTS:\n"
            body += "-" * 40 + "\n"
            
            for signal in sell_signals[:2]:  # Top 2
                rec = signal['recommendation']
                body += f"📉 {signal['symbol']} - {rec['action']}\n"
                body += f"   💰 Price: ${signal['current_price']:.2f}\n"
                body += f"   📊 Score: {signal['final_score']:.1f}/100\n"
                body += f"   📝 Reason: {rec['key_reasons'][0] if rec['key_reasons'] else 'N/A'}\n\n"
        
        body += """
💡 REMINDER: This is paper trading analysis only!
📋 Always do your own research before trading
🛡️  Risk management is crucial - use stop losses
⏰ Check market news and earnings before trading

Happy Trading! 🚀
"""
        
        return self._send_email(subject, body)
    
    def send_portfolio_update(self, portfolio_status: Dict):
        """Send portfolio performance update"""
        
        if not self.enabled:
            return False
        
        perf = portfolio_status
        subject = f"💰 Portfolio Update - {perf['total_pnl_pct']:+.2f}%"
        
        pnl_emoji = "🟢" if perf['total_pnl'] > 0 else "🔴" if perf['total_pnl'] < 0 else "🟡"
        
        body = f"""
💰 PAPER TRADING PORTFOLIO UPDATE
{'='*50}
📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💵 Starting Capital: ${perf['starting_capital']:,.2f}
💰 Current Cash: ${perf['cash']:,.2f}
📊 Stock Value: ${perf['stock_value']:,.2f}
🎯 Total Portfolio: ${perf['total_portfolio_value']:,.2f}

{pnl_emoji} Total P&L: ${perf['total_pnl']:,.2f} ({perf['total_pnl_pct']:+.2f}%)

📊 Portfolio Stats:
- 🔢 Total Trades: {perf['total_trades']}
- 📋 Open Positions: {perf['open_positions']}
- 💼 Cash Utilization: {perf['cash_utilization']:.1f}%

"""
        
        # Add position details if any
        if perf.get('positions'):
            body += "📊 CURRENT POSITIONS:\n"
            body += "-" * 30 + "\n"
            
            for symbol, pos in perf['positions'].items():
                pos_emoji = "🟢" if pos['unrealized_pnl'] > 0 else "🔴" if pos['unrealized_pnl'] < 0 else "🟡"
                body += f"{pos_emoji} {symbol}: ${pos['current_value']:,.2f} "
                body += f"({pos['unrealized_pnl_pct']:+.2f}%) - {pos['days_held']} days\n"
        
        body += "\nKeep up the great work! 🎯"
        
        return self._send_email(subject, body)
    
    def send_trade_alert(self, trade_record: Dict):
        """Send immediate trade execution alert"""
        
        if not self.enabled:
            return False
        
        trade = trade_record
        action_emoji = "🟢" if trade['action'] == 'BUY' else "🔴"
        
        subject = f"{action_emoji} Trade Alert: {trade['action']} {trade['symbol']}"
        
        body = f"""
{action_emoji} TRADE EXECUTED
{'='*30}
📅 {trade['timestamp'][:19]}

📈 Symbol: {trade['symbol']}
🎯 Action: {trade['action']}
📊 Shares: {trade['shares']:,}
💰 Price: ${trade['price']:.2f}
💵 Value: ${trade['trade_value']:,.2f}
💰 Cash After: ${trade['cash_after']:,.2f}

📝 Signal Info:
{trade.get('signal_info', {}).get('reason', 'Manual trade')}

Good luck! 🚀
"""
        
        return self._send_email(subject, body)
    
    def _send_email(self, subject: str, body: str) -> bool:
        """Send email using Gmail SMTP"""
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.config['sender_email']
            message["To"] = self.config['recipient_email']
            
            # Convert to plain text
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            # Create secure connection and send
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls(context=context)
                server.login(self.config['sender_email'], self.config['sender_password'])
                server.sendmail(
                    self.config['sender_email'],
                    self.config['recipient_email'],
                    message.as_string()
                )
            
            print(f"📧 Email sent successfully: {subject}")
            return True
            
        except Exception as e:
            print(f"📧 Email failed: {e}")
            return False


# Email setup instructions
def setup_email_instructions():
    """Print instructions for setting up email notifications"""
    
    print("""
📧 EMAIL NOTIFICATION SETUP INSTRUCTIONS
='*50}

To receive trading alerts via email, follow these steps:

1️⃣ ENABLE 2-FACTOR AUTHENTICATION on your Gmail account
   - Go to myaccount.google.com
   - Security → 2-Step Verification → Turn On

2️⃣ CREATE APP PASSWORD for the trading bot
   - Go to myaccount.google.com
   - Security → App passwords
   - Select app: Other (custom name) → "Trading Bot"
   - Copy the 16-character password (save it!)

3️⃣ SET ENVIRONMENT VARIABLES
   Add these to your ~/.bashrc or ~/.profile:
   
   export TRADING_EMAIL="your.email@gmail.com"
   export TRADING_EMAIL_PASSWORD="your-16-char-app-password"
   export TRADING_RECIPIENT_EMAIL="where-to-send-alerts@gmail.com"

4️⃣ RESTART TERMINAL or run:
   source ~/.bashrc

5️⃣ TEST EMAIL SETUP:
   python -c "from email_notifications import TradingEmailNotifier; 
              notifier = TradingEmailNotifier(); 
              print('Email enabled:', notifier.enabled)"

✅ If email enabled = True, you're ready!
❌ If False, check your environment variables

📧 You'll receive:
- 🌅 Daily trading signals (morning)
- 💰 Portfolio updates (evening) 
- ⚡ Immediate trade alerts
- 📊 Weekly/monthly summaries

Security Note: App passwords are safer than your main Gmail password!
""")

if __name__ == "__main__":
    setup_email_instructions()