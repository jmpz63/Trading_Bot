"""
Advanced Trade Tracking and Performance Analysis
Comprehensive tracking of trading performance with detailed analytics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Dict, List, Tuple
import yfinance as yf

class TradePerformanceAnalyzer:
    """
    Advanced performance analysis for paper trading
    """
    
    def __init__(self, data_dir: str = "data/paper_trading"):
        self.data_dir = Path(data_dir)
        self.trades_df = None
        self.daily_performance = None
        self.load_data()
    
    def load_data(self):
        """Load trade history and daily performance data"""
        
        # Load trades
        trades_file = self.data_dir / "trade_history.json"
        if trades_file.exists():
            with open(trades_file, 'r') as f:
                trades = json.load(f)
            
            if trades:
                self.trades_df = pd.DataFrame(trades)
                self.trades_df['timestamp'] = pd.to_datetime(self.trades_df['timestamp'])
                self.trades_df['date'] = self.trades_df['timestamp'].dt.date
        
        # Load daily performance
        daily_file = self.data_dir / "daily_performance.json"
        if daily_file.exists():
            with open(daily_file, 'r') as f:
                daily_data = json.load(f)
            
            if daily_data:
                self.daily_performance = pd.DataFrame(daily_data)
                self.daily_performance['date'] = pd.to_datetime(self.daily_performance['date'])
    
    def calculate_trade_statistics(self) -> Dict:
        """Calculate comprehensive trade statistics"""
        
        if self.trades_df is None or len(self.trades_df) == 0:
            return {'error': 'No trades to analyze'}
        
        # Separate buys and sells
        buys = self.trades_df[self.trades_df['action'] == 'BUY'].copy()
        sells = self.trades_df[self.trades_df['action'] == 'SELL'].copy()
        
        # Calculate realized P&L per trade
        realized_trades = []
        
        for _, sell in sells.iterrows():
            symbol = sell['symbol']
            sell_date = sell['timestamp']
            
            # Find corresponding buys for this symbol before sell date
            symbol_buys = buys[
                (buys['symbol'] == symbol) & 
                (buys['timestamp'] < sell_date)
            ].sort_values('timestamp')
            
            if not symbol_buys.empty:
                # Use FIFO (First In, First Out) accounting
                shares_to_sell = sell['shares']
                total_cost = 0
                
                for _, buy in symbol_buys.iterrows():
                    if shares_to_sell <= 0:
                        break
                    
                    shares_used = min(shares_to_sell, buy['shares'])
                    total_cost += shares_used * buy['price']
                    shares_to_sell -= shares_used
                
                if shares_to_sell == 0:  # Full match found
                    avg_buy_price = total_cost / sell['shares']
                    profit_loss = (sell['price'] - avg_buy_price) * sell['shares']
                    profit_loss_pct = (sell['price'] - avg_buy_price) / avg_buy_price * 100
                    
                    hold_days = (sell['timestamp'] - symbol_buys.iloc[0]['timestamp']).days
                    
                    realized_trades.append({
                        'symbol': symbol,
                        'sell_date': sell['timestamp'],
                        'shares': sell['shares'],
                        'avg_buy_price': avg_buy_price,
                        'sell_price': sell['price'],
                        'profit_loss': profit_loss,
                        'profit_loss_pct': profit_loss_pct,
                        'hold_days': hold_days,
                        'trade_value': sell['trade_value']
                    })
        
        if not realized_trades:
            return {'error': 'No completed trades to analyze'}
        
        realized_df = pd.DataFrame(realized_trades)
        
        # Calculate statistics
        total_trades = len(realized_df)
        winning_trades = len(realized_df[realized_df['profit_loss'] > 0])
        losing_trades = len(realized_df[realized_df['profit_loss'] < 0])
        breakeven_trades = total_trades - winning_trades - losing_trades
        
        win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0
        
        avg_win = realized_df[realized_df['profit_loss'] > 0]['profit_loss'].mean() if winning_trades > 0 else 0
        avg_loss = realized_df[realized_df['profit_loss'] < 0]['profit_loss'].mean() if losing_trades > 0 else 0
        
        avg_win_pct = realized_df[realized_df['profit_loss'] > 0]['profit_loss_pct'].mean() if winning_trades > 0 else 0
        avg_loss_pct = realized_df[realized_df['profit_loss'] < 0]['profit_loss_pct'].mean() if losing_trades > 0 else 0
        
        profit_factor = abs(avg_win * winning_trades / (avg_loss * losing_trades)) if losing_trades > 0 and avg_loss != 0 else float('inf')
        
        total_realized_pnl = realized_df['profit_loss'].sum()
        
        # Best and worst trades
        best_trade = realized_df.loc[realized_df['profit_loss'].idxmax()] if not realized_df.empty else None
        worst_trade = realized_df.loc[realized_df['profit_loss'].idxmin()] if not realized_df.empty else None
        
        # Average hold time
        avg_hold_days = realized_df['hold_days'].mean()
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'breakeven_trades': breakeven_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'avg_win_pct': avg_win_pct,
            'avg_loss_pct': avg_loss_pct,
            'profit_factor': profit_factor,
            'total_realized_pnl': total_realized_pnl,
            'avg_hold_days': avg_hold_days,
            'best_trade': best_trade.to_dict() if best_trade is not None else None,
            'worst_trade': worst_trade.to_dict() if worst_trade is not None else None,
            'realized_trades_df': realized_df
        }
    
    def calculate_portfolio_metrics(self) -> Dict:
        """Calculate portfolio-level performance metrics"""
        
        if self.daily_performance is None or len(self.daily_performance) == 0:
            return {'error': 'No daily performance data'}
        
        df = self.daily_performance.copy()
        df = df.sort_values('date')
        
        # Calculate daily returns
        df['daily_return'] = df['total_portfolio_value'].pct_change()
        df['cumulative_return'] = (df['total_portfolio_value'] / df['total_portfolio_value'].iloc[0] - 1) * 100
        
        # Performance metrics
        total_return = df['cumulative_return'].iloc[-1]
        daily_returns = df['daily_return'].dropna()
        
        # Volatility (annualized)
        volatility = daily_returns.std() * np.sqrt(252) * 100 if len(daily_returns) > 1 else 0
        
        # Sharpe ratio (assuming 0% risk-free rate)
        avg_daily_return = daily_returns.mean()
        sharpe_ratio = (avg_daily_return / daily_returns.std()) * np.sqrt(252) if daily_returns.std() > 0 else 0
        
        # Maximum drawdown
        running_max = df['total_portfolio_value'].expanding().max()
        drawdown = (df['total_portfolio_value'] - running_max) / running_max * 100
        max_drawdown = drawdown.min()
        
        # Win rate (positive return days)
        positive_days = len(daily_returns[daily_returns > 0])
        total_days = len(daily_returns)
        daily_win_rate = positive_days / total_days * 100 if total_days > 0 else 0
        
        # Best and worst days
        best_day = daily_returns.max() * 100 if not daily_returns.empty else 0
        worst_day = daily_returns.min() * 100 if not daily_returns.empty else 0
        
        return {
            'total_return': total_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'daily_win_rate': daily_win_rate,
            'best_day': best_day,
            'worst_day': worst_day,
            'total_trading_days': total_days,
            'current_value': df['total_portfolio_value'].iloc[-1],
            'starting_value': df['total_portfolio_value'].iloc[0]
        }
    
    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report"""
        
        trade_stats = self.calculate_trade_statistics()
        portfolio_metrics = self.calculate_portfolio_metrics()
        
        report = f"""
📊 COMPREHENSIVE TRADING PERFORMANCE REPORT
{'='*70}
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        # Portfolio Overview
        if 'error' not in portfolio_metrics:
            report += f"""
💰 PORTFOLIO PERFORMANCE:
{'-'*50}
🎯 Total Return: {portfolio_metrics['total_return']:+.2f}%
📈 Current Value: ${portfolio_metrics['current_value']:,.2f}
💵 Starting Value: ${portfolio_metrics['starting_value']:,.2f}
📊 Volatility (Annual): {portfolio_metrics['volatility']:.2f}%
⚡ Sharpe Ratio: {portfolio_metrics['sharpe_ratio']:.2f}
📉 Max Drawdown: {portfolio_metrics['max_drawdown']:.2f}%
🎪 Daily Win Rate: {portfolio_metrics['daily_win_rate']:.1f}%
📅 Trading Days: {portfolio_metrics['total_trading_days']}
🟢 Best Day: +{portfolio_metrics['best_day']:.2f}%
🔴 Worst Day: {portfolio_metrics['worst_day']:.2f}%

"""
        
        # Trade Statistics
        if 'error' not in trade_stats:
            report += f"""
🎯 TRADE STATISTICS:
{'-'*50}
🔢 Total Completed Trades: {trade_stats['total_trades']}
✅ Winning Trades: {trade_stats['winning_trades']}
❌ Losing Trades: {trade_stats['losing_trades']}
🟡 Breakeven Trades: {trade_stats['breakeven_trades']}
🎪 Win Rate: {trade_stats['win_rate']:.1f}%
💰 Average Win: ${trade_stats['avg_win']:,.2f} ({trade_stats['avg_win_pct']:+.2f}%)
💸 Average Loss: ${trade_stats['avg_loss']:,.2f} ({trade_stats['avg_loss_pct']:+.2f}%)
⚖️  Profit Factor: {trade_stats['profit_factor']:.2f}
💵 Total Realized P&L: ${trade_stats['total_realized_pnl']:,.2f}
⏰ Avg Hold Time: {trade_stats['avg_hold_days']:.1f} days

"""
            
            # Best and worst trades
            if trade_stats['best_trade']:
                best = trade_stats['best_trade']
                report += f"""
🏆 BEST TRADE:
{best['symbol']}: +${best['profit_loss']:,.2f} ({best['profit_loss_pct']:+.2f}%)
Bought @ ${best['avg_buy_price']:.2f}, Sold @ ${best['sell_price']:.2f}
Held for {best['hold_days']} days

"""
            
            if trade_stats['worst_trade']:
                worst = trade_stats['worst_trade']
                report += f"""
📉 WORST TRADE:
{worst['symbol']}: ${worst['profit_loss']:,.2f} ({worst['profit_loss_pct']:+.2f}%)
Bought @ ${worst['avg_buy_price']:.2f}, Sold @ ${worst['sell_price']:.2f}
Held for {worst['hold_days']} days

"""
        
        # Performance evaluation
        report += f"""
📈 PERFORMANCE EVALUATION:
{'-'*50}
"""
        
        if 'error' not in portfolio_metrics:
            total_return = portfolio_metrics['total_return']
            sharpe = portfolio_metrics['sharpe_ratio']
            win_rate = trade_stats.get('win_rate', 0)
            
            if total_return > 10:
                report += "🎉 EXCELLENT: Strong positive returns!\n"
            elif total_return > 0:
                report += "✅ GOOD: Profitable trading!\n"
            elif total_return > -5:
                report += "⚠️  OKAY: Minor losses, room for improvement\n"
            else:
                report += "❌ POOR: Significant losses, review strategy\n"
            
            if sharpe > 1.0:
                report += "🏆 EXCELLENT risk-adjusted returns (Sharpe > 1.0)\n"
            elif sharpe > 0.5:
                report += "✅ GOOD risk-adjusted returns\n"
            else:
                report += "⚠️  LOW risk-adjusted returns, high volatility\n"
            
            if win_rate > 60:
                report += "🎯 HIGH win rate - excellent trade selection\n"
            elif win_rate > 50:
                report += "✅ GOOD win rate - above average\n"
            else:
                report += "📊 MODERATE win rate - focus on trade quality\n"
        
        report += f"""

💡 RECOMMENDATIONS:
{'-'*50}
"""
        
        if 'error' not in trade_stats:
            profit_factor = trade_stats.get('profit_factor', 0)
            avg_hold = trade_stats.get('avg_hold_days', 0)
            
            if profit_factor < 1.5:
                report += "• Focus on cutting losses faster (tighter stop losses)\n"
                report += "• Look for higher probability setups\n"
            
            if avg_hold < 3:
                report += "• Consider holding winning trades longer\n"
                report += "• Avoid overtrading - be more selective\n"
            elif avg_hold > 30:
                report += "• Consider taking profits sooner\n"
                report += "• Review position sizing for longer holds\n"
        
        if 'error' not in portfolio_metrics:
            max_dd = portfolio_metrics.get('max_drawdown', 0)
            
            if max_dd < -10:
                report += "• Reduce position sizes to limit drawdowns\n"
                report += "• Implement better risk management\n"
        
        report += """
• Continue using systematic analysis
• Maintain detailed trade records
• Review and adapt strategy regularly

📊 Keep up the great work! Every trade is a learning opportunity.
"""
        
        return report
    
    def save_performance_report(self):
        """Save performance report to file"""
        report = self.generate_performance_report()
        
        report_file = self.data_dir / f"performance_report_{datetime.now().strftime('%Y%m%d')}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"📊 Performance report saved: {report_file}")
        return report_file
    
    def print_quick_summary(self):
        """Print quick performance summary"""
        
        portfolio_metrics = self.calculate_portfolio_metrics()
        trade_stats = self.calculate_trade_statistics()
        
        print("💰 QUICK PERFORMANCE SUMMARY")
        print("="*50)
        
        if 'error' not in portfolio_metrics:
            total_return = portfolio_metrics['total_return']
            current_value = portfolio_metrics['current_value']
            
            status_emoji = "🟢" if total_return > 0 else "🔴" if total_return < -1 else "🟡"
            print(f"{status_emoji} Portfolio: ${current_value:,.2f} ({total_return:+.2f}%)")
        
        if 'error' not in trade_stats:
            win_rate = trade_stats['win_rate']
            total_trades = trade_stats['total_trades']
            realized_pnl = trade_stats['total_realized_pnl']
            
            print(f"🎯 Trades: {total_trades} | Win Rate: {win_rate:.1f}%")
            print(f"💵 Realized P&L: ${realized_pnl:,.2f}")
        
        print("="*50)


def run_performance_analysis():
    """Run complete performance analysis"""
    
    print("📊 TRADING PERFORMANCE ANALYSIS")
    print("="*60)
    
    analyzer = TradePerformanceAnalyzer()
    
    # Quick summary
    analyzer.print_quick_summary()
    
    print("\n📈 Generating detailed report...")
    
    # Generate and display full report
    report = analyzer.generate_performance_report()
    print(report)
    
    # Save report
    analyzer.save_performance_report()
    
    return analyzer


if __name__ == "__main__":
    run_performance_analysis()