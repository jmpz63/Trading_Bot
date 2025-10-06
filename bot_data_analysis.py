#!/usr/bin/env python3
"""
Trading Bot Data Collection & Performance Analysis System
Comprehensive data gathering and testing framework to improve bot performance
"""

import json
import time
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
import requests

class TradingBotDataCollector:
    def __init__(self):
        self.data_dir = Path("data")
        self.logs_dir = Path("logs")
        
        # Create data structure
        self.setup_data_directories()
        
        print("📊 TRADING BOT DATA COLLECTION & ANALYSIS SYSTEM")
        print("=" * 60)
        
    def setup_data_directories(self):
        """Setup comprehensive data collection structure"""
        directories = [
            "data/historical/btc_price_data",
            "data/historical/market_indicators", 
            "data/historical/volatility_patterns",
            "data/real_time/tick_data",
            "data/real_time/order_book",
            "data/backtesting/scenarios",
            "data/backtesting/results",
            "data/performance/trade_analysis",
            "data/performance/strategy_metrics",
            "logs/trading_sessions",
            "logs/error_analysis",
            "logs/optimization_tests"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def collect_historical_btc_data(self, days=365):
        """Collect comprehensive Bitcoin historical data"""
        print(f"📈 Collecting {days} days of Bitcoin historical data...")
        
        try:
            # Get Bitcoin data from multiple timeframes
            timeframes = {
                '1d': f"{days}d",    # Daily data
                '1h': "30d",         # Hourly data (last 30 days)
                '5m': "7d"           # 5-minute data (last 7 days)
            }
            
            historical_data = {}
            
            for interval, period in timeframes.items():
                print(f"  Fetching {interval} data for {period}...")
                
                btc = yf.Ticker("BTC-USD")
                data = btc.history(period=period, interval=interval)
                
                if not data.empty:
                    # Calculate additional metrics
                    data['Returns'] = data['Close'].pct_change()
                    data['Volatility'] = data['Returns'].rolling(20).std() * np.sqrt(252)
                    data['SMA_20'] = data['Close'].rolling(20).mean()
                    data['SMA_50'] = data['Close'].rolling(50).mean()
                    data['RSI'] = self.calculate_rsi(data['Close'])
                    data['MACD'], data['MACD_Signal'] = self.calculate_macd(data['Close'])
                    
                    historical_data[interval] = data
                    
                    # Save to file
                    filename = f"data/historical/btc_price_data/btc_{interval}_{period}.csv"
                    data.to_csv(filename)
                    print(f"    ✅ Saved {len(data)} records to {filename}")
            
            return historical_data
            
        except Exception as e:
            print(f"❌ Error collecting historical data: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        return macd, signal_line
    
    def collect_market_indicators(self):
        """Collect broader market indicators for context"""
        print("📊 Collecting market indicators...")
        
        indicators = {
            'SPY': 'S&P 500',
            'QQQ': 'NASDAQ',
            'VIX': 'Volatility Index',
            'DXY': 'Dollar Index',
            'GOLD': 'Gold',
            'TLT': '20+ Year Treasury'
        }
        
        market_data = {}
        
        for symbol, name in indicators.items():
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="1y")
                
                if not data.empty:
                    market_data[symbol] = {
                        'name': name,
                        'current_price': data['Close'].iloc[-1],
                        'weekly_return': (data['Close'].iloc[-1] / data['Close'].iloc[-5] - 1) * 100,
                        'monthly_return': (data['Close'].iloc[-1] / data['Close'].iloc[-20] - 1) * 100,
                        'yearly_return': (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100,
                        'volatility': data['Close'].pct_change().std() * np.sqrt(252) * 100
                    }
                    
                print(f"  ✅ {name}: {data['Close'].iloc[-1]:.2f}")
                
            except Exception as e:
                print(f"  ❌ Error fetching {symbol}: {e}")
        
        # Save market indicators
        with open("data/historical/market_indicators/market_context.json", 'w') as f:
            json.dump(market_data, f, indent=2)
        
        return market_data
    
    def analyze_volatility_patterns(self, btc_data):
        """Analyze Bitcoin volatility patterns by time of day/week"""
        print("🔍 Analyzing volatility patterns...")
        
        if not btc_data or '1h' not in btc_data:
            print("  ⚠️ No hourly data available for volatility analysis")
            return None
        
        hourly_data = btc_data['1h'].copy()
        hourly_data.index = pd.to_datetime(hourly_data.index)
        
        # Add time features
        hourly_data['Hour'] = hourly_data.index.hour
        hourly_data['DayOfWeek'] = hourly_data.index.dayofweek
        hourly_data['HourlyReturn'] = hourly_data['Close'].pct_change()
        hourly_data['HourlyVolatility'] = abs(hourly_data['HourlyReturn'])
        
        # Analyze patterns
        patterns = {
            'hourly_avg_volatility': hourly_data.groupby('Hour')['HourlyVolatility'].mean().to_dict(),
            'daily_avg_volatility': hourly_data.groupby('DayOfWeek')['HourlyVolatility'].mean().to_dict(),
            'best_trading_hours': hourly_data.groupby('Hour')['HourlyVolatility'].mean().nlargest(5).index.tolist(),
            'worst_trading_hours': hourly_data.groupby('Hour')['HourlyVolatility'].mean().nsmallest(5).index.tolist()
        }
        
        # Save volatility analysis
        with open("data/historical/volatility_patterns/volatility_analysis.json", 'w') as f:
            json.dump(patterns, f, indent=2)
        
        print(f"  ✅ Best trading hours: {patterns['best_trading_hours']}")
        print(f"  ✅ Worst trading hours: {patterns['worst_trading_hours']}")
        
        return patterns
    
    def backtest_strategy_scenarios(self):
        """Backtest different trading scenarios"""
        print("🧪 Running backtest scenarios...")
        
        # Define test scenarios
        scenarios = {
            'aggressive_10pct': {'trade_size': 0.10, 'stop_loss': 0.02, 'take_profit': 0.015},
            'moderate_5pct': {'trade_size': 0.05, 'stop_loss': 0.015, 'take_profit': 0.01}, 
            'conservative_2pct': {'trade_size': 0.02, 'stop_loss': 0.01, 'take_profit': 0.008},
            'high_frequency': {'trade_size': 0.03, 'stop_loss': 0.005, 'take_profit': 0.003}
        }
        
        backtest_results = {}
        
        for scenario_name, params in scenarios.items():
            print(f"  Testing {scenario_name}...")
            
            # Simulate trading with parameters
            result = self.simulate_trading_scenario(params)
            backtest_results[scenario_name] = result
            
            print(f"    Return: {result['total_return']:.2%}")
            print(f"    Win Rate: {result['win_rate']:.1%}")
            print(f"    Max Drawdown: {result['max_drawdown']:.2%}")
        
        # Save backtest results
        with open("data/backtesting/results/scenario_comparison.json", 'w') as f:
            json.dump(backtest_results, f, indent=2)
        
        return backtest_results
    
    def simulate_trading_scenario(self, params):
        """Simulate trading with given parameters"""
        # Simplified backtest simulation
        np.random.seed(42)  # Reproducible results
        
        num_trades = 1000
        starting_capital = 1000
        capital = starting_capital
        
        trades = []
        peak_capital = starting_capital
        max_drawdown = 0
        
        for i in range(num_trades):
            # Simulate trade outcome based on realistic Bitcoin volatility
            trade_amount = capital * params['trade_size']
            
            # Random price movement (Bitcoin-like volatility)
            price_change = np.random.normal(0.002, 0.015)  # 0.2% avg, 1.5% volatility
            
            # Apply stop loss and take profit
            if price_change <= -params['stop_loss']:
                profit_pct = -params['stop_loss']
            elif price_change >= params['take_profit']:
                profit_pct = params['take_profit']
            else:
                profit_pct = price_change
            
            profit = trade_amount * profit_pct
            capital += profit
            
            trades.append({
                'trade_num': i + 1,
                'profit_pct': profit_pct,
                'profit_amount': profit,
                'capital': capital
            })
            
            # Track max drawdown
            if capital > peak_capital:
                peak_capital = capital
            
            drawdown = (peak_capital - capital) / peak_capital
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Calculate results
        winning_trades = [t for t in trades if t['profit_amount'] > 0]
        total_return = (capital - starting_capital) / starting_capital
        win_rate = len(winning_trades) / len(trades)
        
        return {
            'total_return': total_return,
            'final_capital': capital,
            'win_rate': win_rate,
            'max_drawdown': max_drawdown,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'avg_trade_return': np.mean([t['profit_pct'] for t in trades])
        }
    
    def generate_improvement_recommendations(self, backtest_results, volatility_patterns):
        """Generate specific recommendations for bot improvement"""
        print("\n🎯 GENERATING IMPROVEMENT RECOMMENDATIONS...")
        
        recommendations = {
            'timestamp': datetime.now().isoformat(),
            'data_analysis': {},
            'strategy_optimization': {},
            'timing_optimization': {},
            'risk_management': {},
            'implementation_priority': []
        }
        
        # Strategy optimization based on backtest results
        if backtest_results:
            best_scenario = max(backtest_results.items(), key=lambda x: x[1]['total_return'])
            recommendations['strategy_optimization'] = {
                'best_performing_strategy': best_scenario[0],
                'recommended_trade_size': best_scenario[1].get('trade_size', 0.05),
                'optimal_return': best_scenario[1]['total_return'],
                'recommended_win_rate_target': best_scenario[1]['win_rate']
            }
        
        # Timing optimization based on volatility patterns  
        if volatility_patterns:
            recommendations['timing_optimization'] = {
                'optimal_trading_hours': volatility_patterns['best_trading_hours'],
                'avoid_trading_hours': volatility_patterns['worst_trading_hours'],
                'peak_volatility_strategy': 'Increase trade frequency during high volatility hours',
                'low_volatility_strategy': 'Reduce trade size during low volatility periods'
            }
        
        # Priority implementation list
        recommendations['implementation_priority'] = [
            "1. Implement time-based trading (focus on high-volatility hours)",
            "2. Optimize trade size based on backtest results",
            "3. Add dynamic stop-loss based on current volatility",
            "4. Implement market regime detection (bull/bear/sideways)",
            "5. Add correlation analysis with major market indicators",
            "6. Implement adaptive position sizing based on recent performance",
            "7. Add multi-timeframe analysis for entry/exit signals",
            "8. Implement risk-adjusted performance metrics",
        ]
        
        # Data collection needs
        recommendations['data_analysis'] = {
            'required_data_points_per_day': 1440,  # 1-minute data
            'minimum_backtest_period': '1 year',
            'key_indicators_to_track': ['RSI', 'MACD', 'Bollinger Bands', 'Volume Profile'],
            'market_correlation_assets': ['SPY', 'QQQ', 'VIX', 'DXY'],
            'recommended_data_retention': '2 years for optimization, 6 months for real-time'
        }
        
        # Save recommendations
        with open("data/performance/strategy_metrics/improvement_recommendations.json", 'w') as f:
            json.dump(recommendations, f, indent=2)
        
        return recommendations
    
    def run_comprehensive_analysis(self):
        """Run complete data collection and analysis"""
        print("🚀 STARTING COMPREHENSIVE TRADING BOT ANALYSIS")
        print("=" * 70)
        
        # Step 1: Collect historical data
        btc_data = self.collect_historical_btc_data(days=365)
        
        # Step 2: Collect market context
        market_data = self.collect_market_indicators()
        
        # Step 3: Analyze volatility patterns
        volatility_patterns = self.analyze_volatility_patterns(btc_data)
        
        # Step 4: Run backtests
        backtest_results = self.backtest_strategy_scenarios()
        
        # Step 5: Generate recommendations
        recommendations = self.generate_improvement_recommendations(backtest_results, volatility_patterns)
        
        # Summary report
        print(f"\n📊 ANALYSIS COMPLETE - SUMMARY:")
        print("=" * 50)
        print(f"✅ Historical Data: {len(btc_data) if btc_data else 0} timeframes collected")
        print(f"✅ Market Indicators: {len(market_data)} assets analyzed")
        print(f"✅ Volatility Patterns: {'Analyzed' if volatility_patterns else 'Skipped'}")
        print(f"✅ Backtest Scenarios: {len(backtest_results)} strategies tested")
        print(f"✅ Recommendations: {len(recommendations['implementation_priority'])} improvements identified")
        
        if backtest_results:
            best_strategy = max(backtest_results.items(), key=lambda x: x[1]['total_return'])
            print(f"\n🏆 BEST PERFORMING STRATEGY: {best_strategy[0]}")
            print(f"   Return: {best_strategy[1]['total_return']:.2%}")
            print(f"   Win Rate: {best_strategy[1]['win_rate']:.1%}")
        
        print(f"\n📁 All data saved to /data/ and /logs/ directories")
        print(f"🎯 Next: Implement top 3 recommendations for immediate improvement")
        
        return {
            'btc_data': btc_data,
            'market_data': market_data,
            'volatility_patterns': volatility_patterns,
            'backtest_results': backtest_results,
            'recommendations': recommendations
        }

if __name__ == "__main__":
    collector = TradingBotDataCollector()
    results = collector.run_comprehensive_analysis()
    
    print("\n" + "="*70)
    print("🎯 READY TO IMPROVE AGGRESSIVE TRADING BOT WITH DATA-DRIVEN INSIGHTS!")
    print("="*70)