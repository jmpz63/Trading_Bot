"""
Paper Trading Portfolio Manager
Tracks trades, performance, and P&L with $10,000 starting capital
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import yfinance as yf

class PaperTradingPortfolio:
    """
    Complete paper trading portfolio management system
    """
    
    def __init__(self, starting_capital: float = 10000, data_dir: str = "data/paper_trading"):
        self.starting_capital = starting_capital
        self.current_cash = starting_capital
        self.positions = {}  # symbol: {shares, avg_price, entry_date, current_value}
        self.trade_history = []
        self.daily_performance = []
        
        # Setup data directory
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing data if available
        self.load_portfolio_data()
    
    @property
    def cash_balance(self):
        """Get current cash balance"""
        return self.current_cash
    
    def place_trade(self, symbol: str, action: str, shares: int, price: float, 
                   signal_info: Dict = None) -> Dict:
        """
        Place a paper trade (BUY or SELL)
        """
        trade_value = shares * price
        commission = 0  # Assume commission-free trading
        
        trade_id = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if action.upper() == 'BUY':
            if trade_value > self.current_cash:
                return {
                    'status': 'FAILED',
                    'reason': f'Insufficient cash. Need ${trade_value:,.2f}, have ${self.current_cash:,.2f}'
                }
            
            # Execute buy
            self.current_cash -= trade_value
            
            if symbol in self.positions:
                # Add to existing position (average down/up)
                old_shares = self.positions[symbol]['shares']
                old_avg_price = self.positions[symbol]['avg_price']
                
                new_total_shares = old_shares + shares
                new_avg_price = ((old_shares * old_avg_price) + (shares * price)) / new_total_shares
                
                self.positions[symbol]['shares'] = new_total_shares
                self.positions[symbol]['avg_price'] = new_avg_price
            else:
                # New position
                self.positions[symbol] = {
                    'shares': shares,
                    'avg_price': price,
                    'entry_date': datetime.now().isoformat(),
                    'entry_reason': signal_info.get('reason', 'Manual trade') if signal_info else 'Manual trade'
                }
        
        elif action.upper() == 'SELL':
            if symbol not in self.positions or self.positions[symbol]['shares'] < shares:
                available_shares = self.positions.get(symbol, {}).get('shares', 0)
                return {
                    'status': 'FAILED',
                    'reason': f'Insufficient shares. Need {shares}, have {available_shares}'
                }
            
            # Execute sell
            self.current_cash += trade_value
            self.positions[symbol]['shares'] -= shares
            
            # Remove position if fully sold
            if self.positions[symbol]['shares'] == 0:
                del self.positions[symbol]
        
        # Record trade
        trade_record = {
            'trade_id': trade_id,
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'action': action.upper(),
            'shares': shares,
            'price': price,
            'trade_value': trade_value,
            'commission': commission,
            'cash_after': self.current_cash,
            'signal_info': signal_info or {}
        }
        
        self.trade_history.append(trade_record)
        
        return {
            'status': 'SUCCESS',
            'trade_id': trade_id,
            'trade_record': trade_record
        }
    
    def get_portfolio_value(self) -> float:
        """Get total portfolio value (cash + positions)"""
        return self.get_current_portfolio_value()['total_portfolio_value']
    
    def get_positions(self) -> Dict:
        """Get current positions with real-time P&L"""
        positions = {}
        
        for symbol, pos in self.positions.items():
            try:
                # Get current price
                ticker = yf.Ticker(symbol)
                current_price = ticker.history(period="1d")['Close'].iloc[-1]
                
                # Calculate P&L
                unrealized_pnl = (current_price - pos['avg_price']) * pos['shares']
                unrealized_pnl_pct = ((current_price - pos['avg_price']) / pos['avg_price']) * 100
                
                positions[symbol] = {
                    'shares': pos['shares'],
                    'avg_price': pos['avg_price'],
                    'current_price': current_price,
                    'market_value': current_price * pos['shares'],
                    'unrealized_pnl': unrealized_pnl,
                    'unrealized_pnl_pct': unrealized_pnl_pct,
                    'entry_date': pos['entry_date']
                }
            except Exception as e:
                print(f"Error getting current price for {symbol}: {e}")
                positions[symbol] = {
                    'shares': pos['shares'],
                    'avg_price': pos['avg_price'],
                    'current_price': pos['avg_price'],
                    'market_value': pos['avg_price'] * pos['shares'],
                    'unrealized_pnl': 0,
                    'unrealized_pnl_pct': 0,
                    'entry_date': pos['entry_date']
                }
        
        return positions
    
    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary"""
        portfolio_data = self.get_current_portfolio_value()
        
        return {
            'total_value': portfolio_data['total_portfolio_value'],
            'cash_balance': self.current_cash,
            'invested_value': portfolio_data['stock_value'],
            'total_pnl': portfolio_data['total_portfolio_value'] - self.starting_capital,
            'total_return_pct': ((portfolio_data['total_portfolio_value'] / self.starting_capital) - 1) * 100,
            'num_positions': len(self.positions)
        }
    
    def buy_stock(self, symbol: str, dollar_amount: float) -> Dict:
        """Buy stock with specified dollar amount"""
        try:
            # Get current price
            ticker = yf.Ticker(symbol)
            current_price = ticker.history(period="1d")['Close'].iloc[-1]
            
            # Calculate shares (no fractional shares)
            shares = int(dollar_amount / current_price)
            actual_cost = shares * current_price
            
            if actual_cost > self.current_cash:
                return {
                    'success': False,
                    'message': f'Insufficient funds. Need ${actual_cost:,.2f}, have ${self.current_cash:,.2f}'
                }
            
            # Execute trade
            trade_result = self.place_trade(symbol, 'BUY', shares, current_price)
            
            if trade_result['status'] == 'SUCCESS':
                return {
                    'success': True,
                    'message': f'Bought {shares} shares of {symbol} @ ${current_price:.2f}',
                    'shares': shares,
                    'price': current_price,
                    'cost': actual_cost
                }
            else:
                return {
                    'success': False,
                    'message': trade_result.get('reason', 'Trade failed')
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error buying {symbol}: {e}'
            }
    
    def sell_stock(self, symbol: str, shares: int) -> Dict:
        """Sell specified shares of stock"""
        try:
            if symbol not in self.positions:
                return {
                    'success': False,
                    'message': f'No position in {symbol}'
                }
            
            if shares > self.positions[symbol]['shares']:
                return {
                    'success': False,
                    'message': f'Insufficient shares. Have {self.positions[symbol]["shares"]}, trying to sell {shares}'
                }
            
            # Get current price
            ticker = yf.Ticker(symbol)
            current_price = ticker.history(period="1d")['Close'].iloc[-1]
            
            # Execute trade
            trade_result = self.place_trade(symbol, 'SELL', shares, current_price)
            
            if trade_result['status'] == 'SUCCESS':
                return {
                    'success': True,
                    'message': f'Sold {shares} shares of {symbol} @ ${current_price:.2f}',
                    'shares': shares,
                    'price': current_price,
                    'proceeds': shares * current_price
                }
            else:
                return {
                    'success': False,
                    'message': trade_result.get('reason', 'Trade failed')
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error selling {symbol}: {e}'
            }
    
    def calculate_daily_pnl(self) -> float:
        """Calculate daily P&L (simplified version)"""
        # This is a basic implementation - in a real system you'd track daily snapshots
        current_value = self.get_portfolio_value()
        return current_value - 10000  # Assuming we started today
    
    def get_current_portfolio_value(self) -> Dict:
        """Calculate current portfolio value with real-time prices"""
        total_stock_value = 0
        position_values = {}
        
        for symbol, position in self.positions.items():
            try:
                # Get current price
                ticker = yf.Ticker(symbol)
                current_price = ticker.history(period="1d")['Close'].iloc[-1]
                
                position_value = position['shares'] * current_price
                total_stock_value += position_value
                
                # Calculate P&L for this position
                cost_basis = position['shares'] * position['avg_price']
                unrealized_pnl = position_value - cost_basis
                unrealized_pnl_pct = (unrealized_pnl / cost_basis) * 100
                
                position_values[symbol] = {
                    'shares': position['shares'],
                    'avg_price': position['avg_price'],
                    'current_price': current_price,
                    'cost_basis': cost_basis,
                    'current_value': position_value,
                    'unrealized_pnl': unrealized_pnl,
                    'unrealized_pnl_pct': unrealized_pnl_pct,
                    'entry_date': position['entry_date'],
                    'days_held': (datetime.now() - datetime.fromisoformat(position['entry_date'])).days
                }
            except:
                # If can't get current price, use last known price
                position_values[symbol] = {
                    'shares': position['shares'],
                    'avg_price': position['avg_price'],
                    'current_price': position['avg_price'],  # Fallback
                    'cost_basis': position['shares'] * position['avg_price'],
                    'current_value': position['shares'] * position['avg_price'],
                    'unrealized_pnl': 0,
                    'unrealized_pnl_pct': 0,
                    'entry_date': position['entry_date'],
                    'days_held': (datetime.now() - datetime.fromisoformat(position['entry_date'])).days
                }
        
        total_portfolio_value = self.current_cash + total_stock_value
        total_pnl = total_portfolio_value - self.starting_capital
        total_pnl_pct = (total_pnl / self.starting_capital) * 100
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cash': self.current_cash,
            'stock_value': total_stock_value,
            'total_portfolio_value': total_portfolio_value,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'positions': position_values,
            'starting_capital': self.starting_capital
        }
    
    def calculate_daily_performance(self) -> Dict:
        """Calculate performance metrics"""
        portfolio_value = self.get_current_portfolio_value()
        
        # Calculate realized P&L from trade history
        realized_pnl = 0
        for trade in self.trade_history:
            if trade['action'] == 'SELL':
                # Find corresponding buy(s) - simplified calculation
                symbol = trade['symbol']
                sell_value = trade['trade_value']
                
                # Get average cost basis for this position
                buy_trades = [t for t in self.trade_history 
                            if t['symbol'] == symbol and t['action'] == 'BUY' 
                            and t['timestamp'] <= trade['timestamp']]
                
                if buy_trades:
                    total_buy_cost = sum(t['trade_value'] for t in buy_trades)
                    total_buy_shares = sum(t['shares'] for t in buy_trades)
                    avg_cost_per_share = total_buy_cost / total_buy_shares if total_buy_shares > 0 else 0
                    
                    realized_pnl += sell_value - (trade['shares'] * avg_cost_per_share)
        
        # Win rate calculation
        profitable_trades = 0
        total_closed_trades = len([t for t in self.trade_history if t['action'] == 'SELL'])
        
        if total_closed_trades > 0:
            # Simplified win rate - would need more sophisticated tracking for accuracy
            win_rate = profitable_trades / total_closed_trades * 100
        else:
            win_rate = 0
        
        return {
            **portfolio_value,
            'realized_pnl': realized_pnl,
            'unrealized_pnl': portfolio_value['total_pnl'] - realized_pnl,
            'total_trades': len(self.trade_history),
            'open_positions': len(self.positions),
            'win_rate': win_rate,
            'cash_utilization': (1 - (self.current_cash / self.starting_capital)) * 100
        }
    
    def get_performance_summary(self, period: str = 'all') -> Dict:
        """Get performance summary for different time periods"""
        now = datetime.now()
        
        if period == 'day':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        else:
            start_date = datetime.min
        
        # Filter trades by period
        period_trades = [t for t in self.trade_history 
                        if datetime.fromisoformat(t['timestamp']) >= start_date]
        
        # Calculate period performance
        current_performance = self.calculate_daily_performance()
        
        return {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': now.isoformat(),
            'trades_in_period': len(period_trades),
            'current_performance': current_performance,
            'period_trades': period_trades
        }
    
    def save_portfolio_data(self):
        """Save portfolio data to files"""
        # Portfolio state
        portfolio_file = self.data_dir / "portfolio_state.json"
        portfolio_data = {
            'starting_capital': self.starting_capital,
            'current_cash': self.current_cash,
            'positions': self.positions,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(portfolio_file, 'w') as f:
            json.dump(portfolio_data, f, indent=2)
        
        # Trade history
        trades_file = self.data_dir / "trade_history.json"
        with open(trades_file, 'w') as f:
            json.dump(self.trade_history, f, indent=2)
        
        # Daily performance snapshot
        performance = self.calculate_daily_performance()
        daily_file = self.data_dir / "daily_performance.json"
        
        # Load existing daily data
        if daily_file.exists():
            with open(daily_file, 'r') as f:
                daily_data = json.load(f)
        else:
            daily_data = []
        
        # Add today's performance (or update if already exists)
        today = datetime.now().date().isoformat()
        performance['date'] = today
        
        # Remove existing entry for today if exists
        daily_data = [d for d in daily_data if d.get('date') != today]
        daily_data.append(performance)
        
        with open(daily_file, 'w') as f:
            json.dump(daily_data, f, indent=2)
    
    def load_portfolio_data(self):
        """Load existing portfolio data"""
        portfolio_file = self.data_dir / "portfolio_state.json"
        trades_file = self.data_dir / "trade_history.json"
        
        if portfolio_file.exists():
            with open(portfolio_file, 'r') as f:
                data = json.load(f)
                self.starting_capital = data.get('starting_capital', 10000)
                self.current_cash = data.get('current_cash', 10000)
                self.positions = data.get('positions', {})
        
        if trades_file.exists():
            with open(trades_file, 'r') as f:
                self.trade_history = json.load(f)
    
    def print_portfolio_status(self):
        """Print detailed portfolio status"""
        performance = self.calculate_daily_performance()
        
        print("💰 PAPER TRADING PORTFOLIO STATUS")
        print("=" * 60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💵 Starting Capital: ${self.starting_capital:,.2f}")
        print(f"💰 Current Cash: ${performance['cash']:,.2f}")
        print(f"📊 Stock Value: ${performance['stock_value']:,.2f}")
        print(f"🎯 Total Portfolio: ${performance['total_portfolio_value']:,.2f}")
        print(f"📈 Total P&L: ${performance['total_pnl']:,.2f} ({performance['total_pnl_pct']:+.2f}%)")
        print(f"🔢 Total Trades: {performance['total_trades']}")
        print(f"📋 Open Positions: {performance['open_positions']}")
        print(f"💼 Cash Utilization: {performance['cash_utilization']:.1f}%")
        
        if self.positions:
            print(f"\n📊 CURRENT POSITIONS:")
            print("-" * 60)
            
            for symbol, pos_data in performance['positions'].items():
                pnl_emoji = "🟢" if pos_data['unrealized_pnl'] > 0 else "🔴" if pos_data['unrealized_pnl'] < 0 else "🟡"
                print(f"{pnl_emoji} {symbol}")
                print(f"   Shares: {pos_data['shares']:,}")
                print(f"   Avg Price: ${pos_data['avg_price']:.2f}")
                print(f"   Current: ${pos_data['current_price']:.2f}")
                print(f"   Value: ${pos_data['current_value']:,.2f}")
                print(f"   P&L: ${pos_data['unrealized_pnl']:,.2f} ({pos_data['unrealized_pnl_pct']:+.2f}%)")
                print(f"   Held: {pos_data['days_held']} days")
                print()
        else:
            print("\n📭 No open positions")
        
        # Recent trades
        if self.trade_history:
            print("📋 RECENT TRADES (Last 5):")
            print("-" * 60)
            
            for trade in self.trade_history[-5:]:
                action_emoji = "🟢" if trade['action'] == 'BUY' else "🔴"
                print(f"{action_emoji} {trade['timestamp'][:19]} | {trade['symbol']} | "
                      f"{trade['action']} {trade['shares']} @ ${trade['price']:.2f} | "
                      f"Value: ${trade['trade_value']:,.2f}")
        
        print("=" * 60)


class AutoTrader:
    """
    Automated paper trading based on enhanced trading system signals
    """
    
    def __init__(self, portfolio: PaperTradingPortfolio):
        self.portfolio = portfolio
    
    def execute_signals_from_analysis(self, analysis_results: List[Dict], 
                                    auto_execute: bool = False) -> List[Dict]:
        """
        Execute trades based on enhanced trading system analysis
        """
        executed_trades = []
        
        for result in analysis_results:
            if 'error' in result:
                continue
                
            symbol = result['symbol']
            recommendation = result['recommendation']
            action = recommendation['action']
            
            # Only execute strong signals
            if 'STRONG' in action or (auto_execute and 'BUY' in action):
                # Calculate position size
                position_value = self.portfolio.starting_capital * (recommendation['position_size_pct'] / 100)
                current_price = result['current_price']
                shares = int(position_value / current_price)
                
                if shares > 0:
                    signal_info = {
                        'signal_source': 'enhanced_trading_system',
                        'final_score': result['final_score'],
                        'confidence': recommendation['confidence'],
                        'key_reasons': recommendation['key_reasons'],
                        'suggested_stop_loss': recommendation['stop_loss_pct'],
                        'target_hold_period': recommendation['hold_period']
                    }
                    
                    if 'BUY' in action:
                        trade_result = self.portfolio.place_trade(
                            symbol=symbol,
                            action='BUY',
                            shares=shares,
                            price=current_price,
                            signal_info=signal_info
                        )
                        executed_trades.append(trade_result)
                    
                    elif 'SELL' in action and symbol in self.portfolio.positions:
                        # Sell existing position
                        current_shares = self.portfolio.positions[symbol]['shares']
                        trade_result = self.portfolio.place_trade(
                            symbol=symbol,
                            action='SELL',
                            shares=current_shares,
                            price=current_price,
                            signal_info=signal_info
                        )
                        executed_trades.append(trade_result)
        
        return executed_trades


def run_daily_paper_trading():
    """Run daily paper trading with enhanced analysis"""
    print("🎯 DAILY PAPER TRADING SYSTEM")
    print("=" * 60)
    print(f"💰 Starting with $10,000 paper money")
    print()
    
    # Initialize portfolio
    portfolio = PaperTradingPortfolio(starting_capital=10000)
    auto_trader = AutoTrader(portfolio)
    
    # Load enhanced trading system
    import sys
    sys.path.append('.')
    
    try:
        from enhanced_trading_system import EnhancedSwingAnalyzer
        
        # Get enhanced analysis
        analyzer = EnhancedSwingAnalyzer(portfolio_value=10000)
        market_context = analyzer.market_analyzer.get_market_regime()
        
        print(f"📊 Market Regime: {market_context.get('regime', 'UNKNOWN')}")
        print(f"📈 Market Advice: {market_context.get('trading_advice', 'N/A')}")
        print()
        
        # Analyze top opportunities
        top_symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'TSLA', 'GOOGL', 'AMZN']
        
        results = []
        for symbol in top_symbols:
            analysis = analyzer.comprehensive_analysis(symbol, market_context)
            if 'error' not in analysis:
                results.append(analysis)
        
        # Sort by score
        results.sort(key=lambda x: x['final_score'], reverse=True)
        
        print("🎯 TOP TRADING OPPORTUNITIES:")
        print("-" * 60)
        
        for i, result in enumerate(results[:5], 1):
            rec = result['recommendation']
            print(f"{i}. {result['symbol']} - {rec['action']} (Score: {result['final_score']:.1f})")
            print(f"   Price: ${result['current_price']:.2f} | Size: {rec['position_size_pct']:.1f}%")
            print(f"   Confidence: {rec['confidence']} | Stop: {rec['stop_loss_pct']}%")
            print()
        
        # Ask user for trading decisions
        print("💡 TRADING DECISIONS:")
        print("1. 🤖 Auto-execute top 3 BUY signals")
        print("2. 👤 Manual trade selection")
        print("3. 📊 Portfolio status only (no trades)")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            # Auto-execute top signals
            print("\n🤖 Auto-executing top BUY signals...")
            buy_signals = [r for r in results if 'BUY' in r['recommendation']['action']]
            executed = auto_trader.execute_signals_from_analysis(buy_signals[:3], auto_execute=True)
            
            print(f"✅ Executed {len(executed)} trades")
            for trade in executed:
                if trade['status'] == 'SUCCESS':
                    t = trade['trade_record']
                    print(f"   🟢 {t['action']} {t['shares']} {t['symbol']} @ ${t['price']:.2f}")
                else:
                    print(f"   ❌ {trade['reason']}")
        
        elif choice == '2':
            # Manual trading interface
            print("\n👤 Manual Trading Interface:")
            print("Available symbols:", [r['symbol'] for r in results])
            
            while True:
                symbol = input("Enter symbol (or 'done'): ").upper().strip()
                if symbol == 'DONE':
                    break
                
                if symbol in [r['symbol'] for r in results]:
                    action = input("BUY or SELL: ").upper().strip()
                    shares = int(input("Number of shares: ").strip())
                    
                    # Get current price
                    result = next(r for r in results if r['symbol'] == symbol)
                    price = result['current_price']
                    
                    trade_result = portfolio.place_trade(symbol, action, shares, price)
                    
                    if trade_result['status'] == 'SUCCESS':
                        print(f"✅ Trade executed: {action} {shares} {symbol} @ ${price:.2f}")
                    else:
                        print(f"❌ Trade failed: {trade_result['reason']}")
                else:
                    print(f"❌ Symbol {symbol} not in analysis results")
    
    except ImportError:
        print("⚠️  Enhanced trading system not available, using portfolio status only")
    
    # Show portfolio status
    print("\n" + "="*60)
    portfolio.print_portfolio_status()
    
    # Save data
    portfolio.save_portfolio_data()
    print("\n💾 Portfolio data saved!")
    
    # Performance summaries
    print("\n📈 PERFORMANCE SUMMARIES:")
    print("-" * 60)
    
    day_perf = portfolio.get_performance_summary('day')
    week_perf = portfolio.get_performance_summary('week')  
    month_perf = portfolio.get_performance_summary('month')
    
    current = day_perf['current_performance']
    
    print(f"📅 Today: {day_perf['trades_in_period']} trades")
    print(f"📅 Week:  {week_perf['trades_in_period']} trades")
    print(f"📅 Month: {month_perf['trades_in_period']} trades")
    print()
    print(f"💰 Current P&L: ${current['total_pnl']:,.2f} ({current['total_pnl_pct']:+.2f}%)")
    
    if current['total_pnl'] > 0:
        print("🎉 NET POSITIVE! You're making money! 💰")
    elif current['total_pnl'] < 0:
        print("⚠️  NET NEGATIVE. Review strategy and risk management. 📉")
    else:
        print("➡️  BREAK EVEN. Keep analyzing and trading! 📊")
    
    return portfolio


if __name__ == "__main__":
    portfolio = run_daily_paper_trading()