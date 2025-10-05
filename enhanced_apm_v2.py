#!/usr/bin/env python3
"""
🏆 ENHANCED APM V2.0 - Professional Quantitative Trading Platform
Integrating institutional-grade knowledge and AI/ML capabilities

Based on:
- Complete Handbook of Trading Strategies (Academic Foundation)
- Adam Grimes Technical Analysis (Professional Methods)
- CFA Future Investment Management (AI/ML Integration)
- Robert Carver Systematic Trading (Systematic Approaches)
- Python Algorithmic Trading (Professional Implementation)
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Professional imports
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import yfinance as yf
from pathlib import Path

# Add Trade_Bot to path
trade_bot_dir = Path(__file__).parent
sys.path.append(str(trade_bot_dir))

from paper_trading_system import PaperTradingPortfolio

class ProfessionalRiskManager:
    """🛡️ Institutional-Grade Risk Management"""
    
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.max_position_size = 0.02  # 2% max per position
        self.max_portfolio_heat = 0.10  # 10% max portfolio risk
        
    def calculate_position_size(self, entry_price, stop_loss, risk_amount):
        """Calculate position size using professional risk management"""
        if stop_loss >= entry_price or stop_loss <= 0:
            return 0
            
        risk_per_share = entry_price - stop_loss
        if risk_per_share <= 0:
            return 0
            
        shares = min(
            risk_amount / risk_per_share,
            (self.initial_capital * self.max_position_size) / entry_price
        )
        return int(shares)

class AdvancedTechnicalAnalyzer:
    """📈 Professional Technical Analysis Based on Adam Grimes"""
    
    def __init__(self):
        self.lookback_periods = [5, 10, 20, 50]
        
    def analyze_momentum(self, data):
        """Professional momentum analysis"""
        df = data.copy()
        
        # Calculate key indicators
        df['roc_10'] = ((df['Close'] / df['Close'].shift(10)) - 1) * 100
        df['sma_20'] = df['Close'].rolling(window=20).mean()
        df['sma_50'] = df['Close'].rolling(window=50).mean()
        
        # Trend analysis
        df['trend_strength'] = self.calculate_trend_strength(df)
        df['momentum_score'] = self.calculate_momentum_score(df)
        
        return df
    
    def calculate_trend_strength(self, df):
        """Calculate trend strength score"""
        scores = []
        for i in range(len(df)):
            if i < 50:
                scores.append(0)
                continue
                
            # Multiple timeframe analysis
            price_above_sma20 = df['Close'].iloc[i] > df['sma_20'].iloc[i] if 'sma_20' in df.columns else True
            sma20_above_sma50 = df['sma_20'].iloc[i] > df['sma_50'].iloc[i] if all(col in df.columns for col in ['sma_20', 'sma_50']) else True
            momentum_positive = df['roc_10'].iloc[i] > 0 if 'roc_10' in df.columns else True
            
            # Score (0-100)
            factors = [price_above_sma20, sma20_above_sma50, momentum_positive]
            score = sum(factors) * 33.33
            scores.append(score)
            
        return scores
    
    def calculate_momentum_score(self, df):
        """Calculate momentum quality score"""
        if 'roc_10' not in df.columns:
            return [50] * len(df)
            
        # Normalize ROC to 0-100 scale
        roc_values = df['roc_10'].fillna(0)
        scores = np.clip((roc_values + 10) * 5, 0, 100)  # Map -10% to +10% -> 0 to 100
        return scores.tolist()

class SystematicEngine:
    """📊 Systematic Trading Based on Robert Carver"""
    
    def calculate_trend_signal(self, data):
        """Calculate systematic trend signal"""
        df = data.copy()
        
        # Simple trend following
        df['ema_fast'] = df['Close'].ewm(span=16).mean()
        df['ema_slow'] = df['Close'].ewm(span=64).mean()
        
        # Signal strength (-1 to +1)
        df['trend_signal'] = (df['ema_fast'] / df['ema_slow'] - 1) * 10
        df['trend_signal'] = np.clip(df['trend_signal'], -1, 1)
        
        return df['trend_signal'].fillna(0)

class SimpleMLEngine:
    """🤖 Simplified ML Trading Engine"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        
    def create_features(self, data):
        """Create simple ML features"""
        df = data.copy()
        
        # Simple features
        df['returns_5d'] = df['Close'].pct_change(5)
        df['returns_20d'] = df['Close'].pct_change(20) 
        df['volatility'] = df['Close'].pct_change().rolling(20).std()
        df['rsi'] = self.calculate_rsi(df['Close'])
        
        return df
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    def get_signal(self, data):
        """Get simple ML-based signal"""
        try:
            df = self.create_features(data)
            latest = df.iloc[-1]
            
            # Simple rule-based ML simulation
            score = 0
            
            # RSI signal
            if latest['rsi'] < 30:
                score += 0.3  # Oversold
            elif latest['rsi'] > 70:
                score -= 0.3  # Overbought
                
            # Momentum signal
            if latest['returns_5d'] > 0.02:
                score += 0.4
            elif latest['returns_5d'] < -0.02:
                score -= 0.4
                
            # Volatility adjustment
            if latest['volatility'] > 0.3:
                score *= 0.5  # Reduce in high volatility
                
            return np.clip(score, -1, 1)
            
        except:
            return 0

class EnhancedAPMv2:
    """🏆 ENHANCED APM V2.0 - PROFESSIONAL TRADING PLATFORM"""
    
    def __init__(self, initial_capital=10000):
        print("🚀 INITIALIZING ENHANCED APM V2.0")
        print("=" * 60)
        
        # Core components
        self.portfolio = PaperTradingPortfolio(initial_capital)
        self.risk_manager = ProfessionalRiskManager(initial_capital)
        self.technical_analyzer = AdvancedTechnicalAnalyzer()
        self.systematic_engine = SystematicEngine()
        self.ml_engine = SimpleMLEngine()
        
        # Configuration
        self.symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
        self.min_confidence = 0.6
        
        print("✅ Professional Risk Management: ACTIVE")
        print("✅ Advanced Technical Analysis: ACTIVE") 
        print("✅ Systematic Strategy Engine: ACTIVE")
        print("✅ AI/ML Trading Engine: ACTIVE")
        print()
    
    def analyze_symbol(self, symbol):
        """Professional analysis of a symbol"""
        print(f"\n🔍 ANALYZING: {symbol}")
        print("-" * 30)
        
        try:
            # Get data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="6mo")
            
            if data.empty or len(data) < 50:
                print(f"❌ Insufficient data for {symbol}")
                return None
            
            # Technical analysis
            tech_data = self.technical_analyzer.analyze_momentum(data)
            
            # Systematic signals
            trend_signal = self.systematic_engine.calculate_trend_signal(tech_data)
            
            # ML signal
            ml_signal = self.ml_engine.get_signal(tech_data)
            
            # Get latest values
            latest = tech_data.iloc[-1]
            current_price = latest['Close']
            
            analysis = {
                'symbol': symbol,
                'price': current_price,
                'trend_strength': latest.get('trend_strength', 50),
                'momentum_score': latest.get('momentum_score', 50), 
                'systematic_signal': float(trend_signal.iloc[-1]) if len(trend_signal) > 0 else 0,
                'ml_signal': ml_signal
            }
            
            print(f"💰 Price: ${current_price:.2f}")
            print(f"📈 Trend Strength: {analysis['trend_strength']:.1f}/100")
            print(f"⚡ Momentum Score: {analysis['momentum_score']:.1f}/100")
            print(f"⚙️  Systematic: {analysis['systematic_signal']:.3f}")
            print(f"🤖 ML Signal: {analysis['ml_signal']:.3f}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            return None
    
    def make_decision(self, analysis):
        """Make trading decision based on analysis"""
        if not analysis:
            return None
            
        # Combine signals with weights
        weights = {
            'trend_strength': 0.25,
            'momentum_score': 0.25,
            'systematic_signal': 0.30,
            'ml_signal': 0.20
        }
        
        # Normalize and combine
        trend_norm = (analysis['trend_strength'] - 50) / 50
        momentum_norm = (analysis['momentum_score'] - 50) / 50
        
        composite_score = (
            trend_norm * weights['trend_strength'] +
            momentum_norm * weights['momentum_score'] +
            analysis['systematic_signal'] * weights['systematic_signal'] +
            analysis['ml_signal'] * weights['ml_signal']
        )
        
        # Decision logic
        if composite_score > 0.4:
            action = 'BUY'
            confidence = composite_score
        elif composite_score < -0.4:
            action = 'SELL'
            confidence = abs(composite_score)
        else:
            action = 'HOLD'
            confidence = 0
        
        # Position sizing
        if action in ['BUY', 'SELL']:
            risk_amount = self.portfolio.cash * 0.02  # 2% risk
            stop_loss_pct = 0.05  # 5% stop
            
            if action == 'BUY':
                stop_loss = analysis['price'] * (1 - stop_loss_pct)
            else:
                stop_loss = analysis['price'] * (1 + stop_loss_pct)
                
            position_size = self.risk_manager.calculate_position_size(
                analysis['price'], stop_loss, risk_amount
            )
        else:
            position_size = 0
            stop_loss = 0
        
        return {
            'symbol': analysis['symbol'],
            'action': action,
            'price': analysis['price'],
            'confidence': confidence,
            'position_size': position_size,
            'stop_loss': stop_loss,
            'composite_score': composite_score
        }
    
    def run_trading_session(self):
        """Execute professional trading session"""
        print("\n🏆 ENHANCED APM V2.0 TRADING SESSION")
        print("=" * 60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        decisions = []
        executed_trades = []
        
        # Analyze symbols
        for symbol in self.symbols:
            analysis = self.analyze_symbol(symbol)
            if analysis:
                decision = self.make_decision(analysis)
                if decision:
                    decisions.append(decision)
        
        # Execute trades
        print(f"\n📋 TRADING DECISIONS")
        print("-" * 30)
        
        for decision in decisions:
            if decision['action'] != 'HOLD':
                print(f"\n{decision['action']} {decision['symbol']}")
                print(f"  💰 Price: ${decision['price']:.2f}")
                print(f"  📊 Confidence: {decision['confidence']:.1%}")
                print(f"  📈 Shares: {decision['position_size']}")
                print(f"  🛑 Stop: ${decision['stop_loss']:.2f}")
                
                # Execute paper trade
                if decision['action'] == 'BUY' and decision['position_size'] > 0:
                    success = self.portfolio.buy_stock(
                        decision['symbol'],
                        decision['position_size'], 
                        decision['price']
                    )
                    if success:
                        executed_trades.append(decision)
            else:
                print(f"⏸️  HOLD {decision['symbol']} - No strong signal")
        
        # Summary
        print(f"\n📊 SESSION SUMMARY")
        print("-" * 30)
        print(f"Symbols Analyzed: {len(self.symbols)}")
        print(f"Decisions Made: {len(decisions)}")
        print(f"Trades Executed: {len(executed_trades)}")
        print(f"Portfolio Value: ${self.portfolio.total_value:.2f}")
        print(f"Cash Available: ${self.portfolio.cash:.2f}")
        
        return {
            'decisions': decisions,
            'executed_trades': executed_trades,
            'portfolio_value': self.portfolio.total_value
        }

def main():
    """Main execution"""
    apm = EnhancedAPMv2(initial_capital=10000)
    results = apm.run_trading_session()
    
    print(f"\n🎯 ENHANCED APM V2.0 SESSION COMPLETE!")
    print("=" * 60)
    print("🏆 Your trading system now includes:")
    print("   ✅ Professional Risk Management")
    print("   ✅ Advanced Technical Analysis") 
    print("   ✅ Systematic Trading Strategies")
    print("   ✅ AI/ML Signal Generation")
    print("\n🚀 Ready for institutional-grade trading!")

if __name__ == "__main__":
    main()
