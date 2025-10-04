"""
Swing Trading Signal Generator and Notification System
Analyzes S&P 500 for swing trading opportunities and sends alerts
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class SwingTradingAnalyzer:
    """
    Analyzes markets for swing trading opportunities (2-30 day holds)
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.watchlist = config.get('watchlist', [
            'SPY', 'QQQ', 'IWM',  # Market ETFs
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',  # Mega caps
            'NVDA', 'META', 'JPM', 'JNJ', 'V'  # More blue chips
        ])
        
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate swing trading technical indicators"""
        df = data.copy()
        
        # Moving averages for trend direction
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # MACD for momentum
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # RSI for overbought/oversold
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands for support/resistance
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        
        # Volume analysis
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # Price position in recent range
        df['High_52W'] = df['High'].rolling(window=252).max()  # 52 weeks
        df['Low_52W'] = df['Low'].rolling(window=252).min()
        df['Price_Position'] = (df['Close'] - df['Low_52W']) / (df['High_52W'] - df['Low_52W'])
        
        return df
    
    def generate_swing_signals(self, symbol: str) -> Dict:
        """Generate swing trading signals for a symbol"""
        try:
            # Get 1 year of data for proper technical analysis
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1y")
            
            if data.empty:
                return {'symbol': symbol, 'error': 'No data available'}
            
            # Calculate indicators
            df = self.calculate_technical_indicators(data)
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Current price and basic info
            current_price = latest['Close']
            daily_change = (current_price - prev['Close']) / prev['Close'] * 100
            
            # Signal analysis
            signals = {
                'symbol': symbol,
                'current_price': current_price,
                'daily_change': daily_change,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'signals': [],
                'overall_signal': 'HOLD',
                'confidence': 0,
                'target_price': 0,
                'stop_loss': 0,
                'hold_period': '2-4 weeks'
            }
            
            # Trend Analysis
            trend_score = 0
            if latest['Close'] > latest['SMA_20'] > latest['SMA_50']:
                trend_score += 2
                signals['signals'].append("Strong uptrend (above 20 & 50 SMA)")
            elif latest['Close'] > latest['SMA_20']:
                trend_score += 1
                signals['signals'].append("Mild uptrend (above 20 SMA)")
            elif latest['Close'] < latest['SMA_50']:
                trend_score -= 2
                signals['signals'].append("Downtrend (below 50 SMA)")
            
            # MACD Analysis
            if latest['MACD'] > latest['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']:
                trend_score += 2
                signals['signals'].append("MACD bullish crossover - momentum building")
            elif latest['MACD'] < latest['MACD_Signal'] and prev['MACD'] >= prev['MACD_Signal']:
                trend_score -= 2
                signals['signals'].append("MACD bearish crossover - momentum weakening")
            
            # RSI Analysis (swing trading sweet spots)
            if 30 <= latest['RSI'] <= 40:
                trend_score += 1
                signals['signals'].append(f"RSI oversold area ({latest['RSI']:.1f}) - potential bounce")
            elif 60 <= latest['RSI'] <= 70:
                trend_score -= 1
                signals['signals'].append(f"RSI overbought area ({latest['RSI']:.1f}) - potential pullback")
            elif latest['RSI'] < 30:
                signals['signals'].append(f"RSI very oversold ({latest['RSI']:.1f}) - high risk/reward")
            elif latest['RSI'] > 70:
                signals['signals'].append(f"RSI very overbought ({latest['RSI']:.1f}) - consider taking profits")
            
            # Bollinger Bands (mean reversion)
            if latest['Close'] <= latest['BB_Lower']:
                trend_score += 1
                signals['signals'].append("Price at lower Bollinger Band - oversold")
            elif latest['Close'] >= latest['BB_Upper']:
                trend_score -= 1
                signals['signals'].append("Price at upper Bollinger Band - overbought")
            
            # Volume confirmation
            if latest['Volume_Ratio'] > 1.5:
                signals['signals'].append("High volume confirms move")
            elif latest['Volume_Ratio'] < 0.7:
                signals['signals'].append("Low volume - weak conviction")
            
            # 52-week position
            position_52w = latest['Price_Position'] * 100
            if position_52w > 80:
                signals['signals'].append(f"Near 52-week high ({position_52w:.1f}%) - momentum play")
            elif position_52w < 20:
                signals['signals'].append(f"Near 52-week low ({position_52w:.1f}%) - value opportunity")
            
            # Generate overall signal
            if trend_score >= 3:
                signals['overall_signal'] = 'STRONG BUY'
                signals['confidence'] = min(trend_score * 15, 95)
                signals['target_price'] = current_price * 1.15  # 15% target
                signals['stop_loss'] = current_price * 0.93     # 7% stop
                signals['hold_period'] = '2-6 weeks'
            elif trend_score >= 1:
                signals['overall_signal'] = 'BUY'
                signals['confidence'] = min(trend_score * 20, 80)
                signals['target_price'] = current_price * 1.10  # 10% target
                signals['stop_loss'] = current_price * 0.95     # 5% stop
                signals['hold_period'] = '3-8 weeks'
            elif trend_score <= -3:
                signals['overall_signal'] = 'STRONG SELL'
                signals['confidence'] = min(abs(trend_score) * 15, 95)
                signals['target_price'] = current_price * 0.85  # 15% down target (short)
                signals['stop_loss'] = current_price * 1.07     # 7% stop (short)
                signals['hold_period'] = '2-6 weeks'
            elif trend_score <= -1:
                signals['overall_signal'] = 'SELL'
                signals['confidence'] = min(abs(trend_score) * 20, 80)
                signals['target_price'] = current_price * 0.90  # 10% down target
                signals['stop_loss'] = current_price * 1.05     # 5% stop
                signals['hold_period'] = '3-8 weeks'
            else:
                signals['overall_signal'] = 'HOLD'
                signals['confidence'] = 30
                signals['target_price'] = current_price
                signals['stop_loss'] = current_price * 0.95
                signals['hold_period'] = 'Wait for clearer signal'
            
            return signals
            
        except Exception as e:
            return {'symbol': symbol, 'error': str(e)}
    
    def scan_watchlist(self) -> List[Dict]:
        """Scan entire watchlist for swing trading opportunities"""
        print("🔍 Scanning watchlist for swing trading opportunities...")
        
        all_signals = []
        for symbol in self.watchlist:
            print(f"  Analyzing {symbol}...")
            signals = self.generate_swing_signals(symbol)
            
            if 'error' not in signals:
                all_signals.append(signals)
        
        # Sort by confidence and signal strength
        buy_signals = [s for s in all_signals if 'BUY' in s['overall_signal']]
        sell_signals = [s for s in all_signals if 'SELL' in s['overall_signal']]
        
        buy_signals.sort(key=lambda x: x['confidence'], reverse=True)
        sell_signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'buy_opportunities': buy_signals,
            'sell_opportunities': sell_signals,
            'hold_positions': [s for s in all_signals if s['overall_signal'] == 'HOLD'],
            'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


class SwingTradingNotifier:
    """
    Sends notifications for swing trading opportunities
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.notification_methods = config.get('notifications', {})
    
    def format_signal_message(self, signal: Dict) -> str:
        """Format trading signal into readable message"""
        symbol = signal['symbol']
        action = signal['overall_signal']
        price = signal['current_price']
        confidence = signal['confidence']
        target = signal.get('target_price', 0)
        stop = signal.get('stop_loss', 0)
        period = signal.get('hold_period', 'TBD')
        
        emoji = "🟢" if 'BUY' in action else "🔴" if 'SELL' in action else "🟡"
        
        message = f"""
{emoji} {action} SIGNAL: {symbol}
Current Price: ${price:.2f}
Confidence: {confidence}%
Target: ${target:.2f} ({((target/price-1)*100):+.1f}%)
Stop Loss: ${stop:.2f} ({((stop/price-1)*100):+.1f}%)
Hold Period: {period}

Key Reasons:
"""
        
        for reason in signal.get('signals', [])[:3]:  # Top 3 reasons
            message += f"• {reason}\n"
        
        return message
    
    def print_daily_report(self, scan_results: Dict):
        """Print daily swing trading report to console"""
        print("\n" + "="*60)
        print(f"📊 SWING TRADING DAILY REPORT - {scan_results['scan_time']}")
        print("="*60)
        
        # Buy opportunities
        buy_ops = scan_results['buy_opportunities']
        if buy_ops:
            print(f"\n🟢 BUY OPPORTUNITIES ({len(buy_ops)}):")
            print("-" * 40)
            
            for signal in buy_ops[:5]:  # Top 5
                conf = signal['confidence']
                price = signal['current_price']
                target = signal['target_price']
                potential = ((target/price-1)*100)
                
                print(f"  {signal['symbol']:<6} ${price:>7.2f} → ${target:>7.2f} "
                      f"({potential:+5.1f}%) Conf: {conf}%")
                print(f"         {signal['overall_signal']} - {signal['hold_period']}")
                if signal['signals']:
                    print(f"         Key: {signal['signals'][0]}")
                print()
        else:
            print("\n🟢 No strong buy opportunities found today")
        
        # Sell opportunities  
        sell_ops = scan_results['sell_opportunities']
        if sell_ops:
            print(f"\n🔴 SELL/SHORT OPPORTUNITIES ({len(sell_ops)}):")
            print("-" * 40)
            
            for signal in sell_ops[:3]:  # Top 3
                conf = signal['confidence']
                price = signal['current_price']
                target = signal['target_price']
                potential = ((target/price-1)*100)
                
                print(f"  {signal['symbol']:<6} ${price:>7.2f} → ${target:>7.2f} "
                      f"({potential:+5.1f}%) Conf: {conf}%")
                print(f"         {signal['overall_signal']} - {signal['hold_period']}")
                if signal['signals']:
                    print(f"         Key: {signal['signals'][0]}")
                print()
        else:
            print("\n🔴 No strong sell opportunities found today")
        
        print("\n" + "="*60)
        print("💡 NEXT STEPS:")
        print("1. Review opportunities above")
        print("2. Do your own research (earnings, news, etc.)")
        print("3. Check your current positions")  
        print("4. Place trades during market hours (9:30-4:00 ET)")
        print("5. Set stop losses and target prices")
        print("="*60)
    
    def send_notifications(self, scan_results: Dict):
        """Send notifications via configured methods"""
        # For now, just print to console
        self.print_daily_report(scan_results)
        
        # TODO: Add email, SMS, Slack notifications
        # if self.notification_methods.get('email'):
        #     self.send_email_alert(scan_results)


# Example usage
def main():
    """Main swing trading analysis"""
    config = {
        'watchlist': [
            'SPY', 'QQQ', 'IWM',  # Market ETFs
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
            'NVDA', 'META', 'JPM', 'JNJ', 'V', 'WMT', 'PG'
        ],
        'notifications': {
            'console': True,
            'email': False
        }
    }
    
    analyzer = SwingTradingAnalyzer(config)
    notifier = SwingTradingNotifier(config)
    
    # Scan for opportunities
    results = analyzer.scan_watchlist()
    
    # Send notifications
    notifier.send_notifications(results)

if __name__ == "__main__":
    main()