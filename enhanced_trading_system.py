"""
Advanced Trading Decision Engine
Multi-timeframe analysis with market context, sentiment, and risk assessment
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional
import json

class AdvancedMarketAnalyzer:
    """
    Advanced market analysis combining multiple factors for better trading decisions
    """
    
    def __init__(self):
        self.market_indicators = {}
        self.sector_data = {}
        self.volatility_data = {}
    
    def get_market_regime(self) -> Dict:
        """Determine current market regime (bull, bear, sideways, volatile)"""
        try:
            # Get major market indices
            spy = yf.Ticker("SPY").history(period="6mo")
            vix = yf.Ticker("^VIX").history(period="1mo")
            
            # Calculate market trends
            spy_20sma = spy['Close'].rolling(20).mean().iloc[-1]
            spy_50sma = spy['Close'].rolling(50).mean().iloc[-1]
            spy_200sma = spy['Close'].rolling(200).mean().iloc[-1]
            spy_current = spy['Close'].iloc[-1]
            
            # Current VIX level
            current_vix = vix['Close'].iloc[-1] if not vix.empty else 20
            
            # Market performance
            month_return = (spy_current / spy['Close'].iloc[-20] - 1) * 100
            quarter_return = (spy_current / spy['Close'].iloc[-63] - 1) * 100
            
            # Determine regime
            regime_score = 0
            regime_factors = []
            
            if spy_current > spy_20sma > spy_50sma > spy_200sma:
                regime_score += 3
                regime_factors.append("Strong uptrend across all timeframes")
            elif spy_current > spy_20sma > spy_50sma:
                regime_score += 2  
                regime_factors.append("Medium-term uptrend")
            elif spy_current > spy_20sma:
                regime_score += 1
                regime_factors.append("Short-term uptrend")
            elif spy_current < spy_200sma:
                regime_score -= 2
                regime_factors.append("Long-term downtrend")
            
            # VIX assessment
            if current_vix < 15:
                regime_score += 1
                regime_factors.append("Low volatility (complacency)")
            elif current_vix > 30:
                regime_score -= 2
                regime_factors.append("High volatility (fear)")
            elif current_vix > 20:
                regime_score -= 1
                regime_factors.append("Elevated volatility")
            
            # Performance assessment
            if quarter_return > 10:
                regime_factors.append("Strong quarterly performance")
            elif quarter_return < -10:
                regime_score -= 1
                regime_factors.append("Weak quarterly performance")
            
            # Final regime determination
            if regime_score >= 3:
                regime = "STRONG_BULL"
                advice = "Favor long positions, momentum plays"
            elif regime_score >= 1:
                regime = "BULL"
                advice = "Moderately bullish, selective buying"
            elif regime_score <= -2:
                regime = "BEAR"
                advice = "Defensive mode, consider cash/shorts"
            elif regime_score == -1:
                regime = "WEAK"
                advice = "Cautious, reduce position sizes"
            else:
                regime = "SIDEWAYS"
                advice = "Range-bound, mean reversion plays"
            
            return {
                'regime': regime,
                'score': regime_score,
                'vix': current_vix,
                'spy_price': spy_current,
                'month_return': month_return,
                'quarter_return': quarter_return,
                'factors': regime_factors,
                'trading_advice': advice,
                'risk_level': 'LOW' if current_vix < 15 else 'HIGH' if current_vix > 25 else 'MEDIUM'
            }
            
        except Exception as e:
            return {'regime': 'UNKNOWN', 'error': str(e)}
    
    def analyze_sector_rotation(self) -> Dict:
        """Analyze which sectors are leading/lagging"""
        sector_etfs = {
            'Technology': 'XLK',
            'Healthcare': 'XLV', 
            'Financials': 'XLF',
            'Consumer_Disc': 'XLY',
            'Industrials': 'XLI',
            'Energy': 'XLE',
            'Materials': 'XLB',
            'Utilities': 'XLU',
            'Real_Estate': 'XLRE',
            'Consumer_Staples': 'XLP',
            'Communications': 'XLC'
        }
        
        sector_performance = {}
        
        for sector, etf in sector_etfs.items():
            try:
                data = yf.Ticker(etf).history(period="3mo")
                if not data.empty:
                    # Performance metrics
                    week_return = (data['Close'].iloc[-1] / data['Close'].iloc[-5] - 1) * 100
                    month_return = (data['Close'].iloc[-1] / data['Close'].iloc[-20] - 1) * 100
                    quarter_return = (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100
                    
                    # Relative strength vs SPY
                    spy_month = yf.Ticker("SPY").history(period="1mo")
                    spy_return = (spy_month['Close'].iloc[-1] / spy_month['Close'].iloc[0] - 1) * 100
                    relative_strength = month_return - spy_return
                    
                    sector_performance[sector] = {
                        'symbol': etf,
                        'week_return': week_return,
                        'month_return': month_return,
                        'quarter_return': quarter_return,
                        'relative_strength': relative_strength,
                        'current_price': data['Close'].iloc[-1]
                    }
            except:
                continue
        
        # Sort by relative strength
        sorted_sectors = sorted(sector_performance.items(), 
                              key=lambda x: x[1]['relative_strength'], 
                              reverse=True)
        
        leaders = sorted_sectors[:3]
        laggards = sorted_sectors[-3:]
        
        return {
            'sector_performance': sector_performance,
            'leaders': leaders,
            'laggards': laggards,
            'rotation_signal': 'GROWTH' if leaders[0][1]['relative_strength'] > 2 else 'DEFENSIVE'
        }
    
    def get_earnings_calendar(self, symbols: List[str]) -> Dict:
        """Get upcoming earnings for watchlist symbols"""
        # Simplified earnings check - in practice would use real earnings API
        earnings_coming = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Check if earnings date is available
                earnings_date = info.get('earningsDate', None)
                if earnings_date:
                    earnings_coming[symbol] = {
                        'earnings_date': str(earnings_date),
                        'warning': 'Earnings volatility expected'
                    }
            except:
                continue
        
        return earnings_coming
    
    def calculate_position_sizing(self, signal_strength: float, portfolio_value: float, 
                                market_regime: Dict, volatility: float) -> Dict:
        """Advanced position sizing based on Kelly Criterion and market conditions"""
        
        # Base position size (2-5% of portfolio)
        base_position = 0.03  # 3% base
        
        # Adjust for signal strength
        signal_multiplier = min(signal_strength / 100, 1.0)
        
        # Adjust for market regime
        regime_multiplier = {
            'STRONG_BULL': 1.5,
            'BULL': 1.2,
            'SIDEWAYS': 0.8,
            'WEAK': 0.5,
            'BEAR': 0.3
        }.get(market_regime.get('regime', 'SIDEWAYS'), 0.8)
        
        # Adjust for volatility (VIX)
        vix = market_regime.get('vix', 20)
        if vix < 15:
            vol_multiplier = 1.2  # Low vol = larger positions
        elif vix > 25:
            vol_multiplier = 0.6  # High vol = smaller positions
        else:
            vol_multiplier = 1.0
        
        # Final position size
        final_position_pct = base_position * signal_multiplier * regime_multiplier * vol_multiplier
        final_position_pct = max(0.01, min(final_position_pct, 0.08))  # 1-8% range
        
        position_value = portfolio_value * final_position_pct
        
        return {
            'position_percentage': final_position_pct * 100,
            'position_value': position_value,
            'rationale': f"Base:{base_position:.1%} × Signal:{signal_multiplier:.1%} × Regime:{regime_multiplier:.1f} × Vol:{vol_multiplier:.1f}",
            'risk_level': market_regime.get('risk_level', 'MEDIUM')
        }


class EnhancedSwingAnalyzer:
    """Enhanced swing trading analyzer with multi-factor decision making"""
    
    def __init__(self, portfolio_value: float = 100000):
        self.portfolio_value = portfolio_value
        self.market_analyzer = AdvancedMarketAnalyzer()
        
        # Enhanced watchlist with sectors
        self.watchlist = {
            'market_etfs': ['SPY', 'QQQ', 'IWM', 'VTI'],
            'sector_etfs': ['XLK', 'XLF', 'XLV', 'XLE', 'XLI'],
            'mega_caps': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'],
            'growth_stocks': ['TSLA', 'META', 'CRM', 'AMD', 'NFLX'],
            'value_stocks': ['JPM', 'BRK-B', 'JNJ', 'V', 'WMT'],
            'dividend_stocks': ['KO', 'PG', 'JNJ', 'VZ', 'PFE']
        }
    
    def comprehensive_analysis(self, symbol: str, market_context: Dict) -> Dict:
        """Comprehensive analysis combining technical, fundamental, and market factors"""
        
        try:
            # Get data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1y")
            info = ticker.info
            
            if data.empty:
                return {'symbol': symbol, 'error': 'No data available'}
            
            # Technical Analysis (enhanced)
            tech_analysis = self.advanced_technical_analysis(data)
            
            # Fundamental screening
            fund_analysis = self.fundamental_screening(info)
            
            # Market context integration
            context_score = self.integrate_market_context(tech_analysis, market_context, symbol)
            
            # Risk assessment
            risk_analysis = self.assess_risk(data, info, market_context)
            
            # Position sizing
            signal_strength = tech_analysis['overall_score']
            position_info = self.market_analyzer.calculate_position_sizing(
                signal_strength, self.portfolio_value, market_context, risk_analysis['volatility']
            )
            
            # Final recommendation
            final_score = (tech_analysis['overall_score'] + context_score + fund_analysis['score']) / 3
            
            recommendation = self.generate_recommendation(
                final_score, tech_analysis, fund_analysis, risk_analysis, position_info
            )
            
            return {
                'symbol': symbol,
                'current_price': data['Close'].iloc[-1],
                'technical': tech_analysis,
                'fundamental': fund_analysis,
                'risk': risk_analysis,
                'position_sizing': position_info,
                'recommendation': recommendation,
                'final_score': final_score,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'symbol': symbol, 'error': str(e)}
    
    def advanced_technical_analysis(self, data: pd.DataFrame) -> Dict:
        """Advanced technical analysis with multiple indicators"""
        
        df = data.copy()
        
        # Moving averages
        df['SMA_10'] = df['Close'].rolling(10).mean()
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        df['SMA_200'] = df['Close'].rolling(200).mean()
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # Get latest values
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Scoring system (0-100)
        score = 50  # Neutral starting point
        signals = []
        
        # Trend analysis (40 points possible)
        if latest['Close'] > latest['SMA_20'] > latest['SMA_50'] > latest['SMA_200']:
            score += 20
            signals.append("Strong multi-timeframe uptrend")
        elif latest['Close'] > latest['SMA_20'] > latest['SMA_50']:
            score += 15
            signals.append("Medium-term uptrend")
        elif latest['Close'] > latest['SMA_20']:
            score += 10
            signals.append("Short-term uptrend")
        elif latest['Close'] < latest['SMA_200']:
            score -= 15
            signals.append("Long-term downtrend")
        
        # MACD momentum (20 points possible)
        if latest['MACD'] > latest['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']:
            score += 15
            signals.append("MACD bullish crossover")
        elif latest['MACD'] > latest['MACD_Signal']:
            score += 10
            signals.append("MACD above signal line")
        elif latest['MACD'] < latest['MACD_Signal'] and prev['MACD'] >= prev['MACD_Signal']:
            score -= 15
            signals.append("MACD bearish crossover")
        
        # RSI analysis (20 points possible) 
        if 30 <= latest['RSI'] <= 45:
            score += 10
            signals.append(f"RSI oversold bounce zone ({latest['RSI']:.1f})")
        elif 55 <= latest['RSI'] <= 70:
            score += 5
            signals.append(f"RSI healthy momentum ({latest['RSI']:.1f})")
        elif latest['RSI'] > 75:
            score -= 10
            signals.append(f"RSI overbought ({latest['RSI']:.1f})")
        elif latest['RSI'] < 25:
            score -= 5
            signals.append(f"RSI extremely oversold ({latest['RSI']:.1f})")
        
        # Volume confirmation (10 points possible)
        if latest['Volume_Ratio'] > 1.5:
            score += 5
            signals.append("High volume confirmation")
        elif latest['Volume_Ratio'] < 0.7:
            score -= 5
            signals.append("Low volume concern")
        
        # Bollinger Bands (10 points possible)
        if latest['Close'] <= latest['BB_Lower']:
            score += 5
            signals.append("At lower Bollinger Band - potential bounce")
        elif latest['Close'] >= latest['BB_Upper']:
            score -= 5  
            signals.append("At upper Bollinger Band - potential resistance")
        
        return {
            'overall_score': max(0, min(100, score)),
            'signals': signals,
            'rsi': latest['RSI'],
            'macd_signal': 'BULLISH' if latest['MACD'] > latest['MACD_Signal'] else 'BEARISH',
            'trend_direction': 'UP' if latest['Close'] > latest['SMA_50'] else 'DOWN',
            'volume_confirmation': latest['Volume_Ratio'] > 1.2
        }
    
    def fundamental_screening(self, info: Dict) -> Dict:
        """Basic fundamental analysis screening"""
        score = 50
        factors = []
        
        try:
            # P/E ratio screening
            pe_ratio = info.get('trailingPE', None)
            if pe_ratio:
                if 10 <= pe_ratio <= 25:
                    score += 10
                    factors.append(f"Reasonable P/E ratio ({pe_ratio:.1f})")
                elif pe_ratio > 40:
                    score -= 10
                    factors.append(f"High P/E ratio ({pe_ratio:.1f})")
            
            # Market cap screening  
            market_cap = info.get('marketCap', 0)
            if market_cap > 100_000_000_000:  # >100B = mega cap
                score += 5
                factors.append("Mega-cap stability")
            elif market_cap > 10_000_000_000:  # >10B = large cap
                score += 3
                factors.append("Large-cap stock")
            
            # Profit margins
            profit_margin = info.get('profitMargins', None)
            if profit_margin and profit_margin > 0.15:
                score += 5
                factors.append(f"Strong profit margins ({profit_margin:.1%})")
            elif profit_margin and profit_margin < 0:
                score -= 15
                factors.append("Negative profit margins")
            
            # Revenue growth
            revenue_growth = info.get('revenueGrowth', None)
            if revenue_growth and revenue_growth > 0.1:
                score += 5
                factors.append(f"Strong revenue growth ({revenue_growth:.1%})")
            elif revenue_growth and revenue_growth < -0.05:
                score -= 10
                factors.append(f"Revenue decline ({revenue_growth:.1%})")
            
            # Debt to equity
            debt_to_equity = info.get('debtToEquity', None) 
            if debt_to_equity and debt_to_equity < 50:
                score += 5
                factors.append("Low debt levels")
            elif debt_to_equity and debt_to_equity > 100:
                score -= 5
                factors.append("High debt levels")
                
        except:
            factors.append("Limited fundamental data available")
        
        return {
            'score': max(0, min(100, score)),
            'factors': factors
        }
    
    def integrate_market_context(self, tech_analysis: Dict, market_context: Dict, symbol: str) -> float:
        """Integrate market regime and sector rotation into analysis"""
        score = 50
        
        regime = market_context.get('regime', 'SIDEWAYS')
        
        # Adjust based on market regime
        if regime == 'STRONG_BULL' and tech_analysis['overall_score'] > 60:
            score += 20  # Strong stocks in strong market
        elif regime == 'BULL' and tech_analysis['overall_score'] > 50:
            score += 10
        elif regime == 'BEAR' and tech_analysis['overall_score'] < 40:
            score += 10  # Weak stocks confirmed by weak market
        elif regime == 'BEAR' and tech_analysis['overall_score'] > 60:
            score -= 10  # Good stocks in bad market (risky)
        
        # Risk adjustment based on VIX
        vix = market_context.get('vix', 20)
        if vix > 25:  # High volatility
            score -= 10
        elif vix < 15:  # Low volatility
            score += 5
        
        return max(0, min(100, score))
    
    def assess_risk(self, data: pd.DataFrame, info: Dict, market_context: Dict) -> Dict:
        """Comprehensive risk assessment"""
        
        # Calculate volatility (30-day)
        returns = data['Close'].pct_change().dropna()
        volatility = returns.tail(30).std() * np.sqrt(252) * 100  # Annualized %
        
        # Beta calculation (vs SPY)
        try:
            spy_data = yf.Ticker("SPY").history(period="1y")
            spy_returns = spy_data['Close'].pct_change().dropna()
            
            # Align dates
            common_dates = returns.index.intersection(spy_returns.index)
            if len(common_dates) > 50:
                stock_returns_aligned = returns[common_dates]
                spy_returns_aligned = spy_returns[common_dates]
                beta = np.cov(stock_returns_aligned, spy_returns_aligned)[0][1] / np.var(spy_returns_aligned)
            else:
                beta = 1.0
        except:
            beta = 1.0
        
        # Risk categorization
        if volatility < 20:
            risk_level = "LOW"
        elif volatility < 35:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        # Market risk factor
        market_risk = market_context.get('risk_level', 'MEDIUM')
        
        return {
            'volatility': volatility,
            'beta': beta,
            'risk_level': risk_level,
            'market_risk': market_risk,
            'suggested_stop_loss': 8 if volatility > 30 else 5 if volatility > 20 else 3
        }
    
    def generate_recommendation(self, final_score: float, tech_analysis: Dict, 
                              fund_analysis: Dict, risk_analysis: Dict, 
                              position_info: Dict) -> Dict:
        """Generate final trading recommendation"""
        
        if final_score >= 75:
            action = "STRONG BUY"
            confidence = "HIGH"
        elif final_score >= 60:
            action = "BUY"
            confidence = "MEDIUM-HIGH"
        elif final_score >= 55:
            action = "WEAK BUY"
            confidence = "MEDIUM"
        elif final_score <= 25:
            action = "STRONG SELL"
            confidence = "HIGH"
        elif final_score <= 40:
            action = "SELL"
            confidence = "MEDIUM-HIGH"
        elif final_score <= 45:
            action = "WEAK SELL"
            confidence = "MEDIUM"
        else:
            action = "HOLD"
            confidence = "LOW"
        
        return {
            'action': action,
            'confidence': confidence,
            'final_score': final_score,
            'position_size_pct': position_info['position_percentage'],
            'stop_loss_pct': risk_analysis['suggested_stop_loss'],
            'risk_reward_ratio': 2.0,  # Target 2:1 reward/risk
            'hold_period': '2-6 weeks' if 'BUY' in action else '1-4 weeks',
            'key_reasons': tech_analysis['signals'][:3] + fund_analysis['factors'][:2]
        }


def run_enhanced_analysis():
    """Run the enhanced trading analysis"""
    print("🚀 ENHANCED TRADING DECISION SYSTEM")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Multi-factor analysis: Technical + Fundamental + Market Context")
    print()
    
    # Initialize analyzer
    analyzer = EnhancedSwingAnalyzer(portfolio_value=100000)  # $100k portfolio
    
    # Get market context
    print("📊 Analyzing market regime...")
    market_context = analyzer.market_analyzer.get_market_regime()
    
    print(f"Market Regime: {market_context.get('regime', 'UNKNOWN')}")
    print(f"VIX Level: {market_context.get('vix', 'N/A')}")
    print(f"Trading Advice: {market_context.get('trading_advice', 'N/A')}")
    print()
    
    # Sector rotation analysis
    print("🔄 Analyzing sector rotation...")
    sector_analysis = analyzer.market_analyzer.analyze_sector_rotation()
    
    if sector_analysis.get('leaders'):
        print("Leading Sectors:")
        for sector, data in sector_analysis['leaders']:
            print(f"  📈 {sector}: {data['relative_strength']:+.1f}% vs SPY")
    
    print()
    
    # Analyze top symbols
    top_symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'TSLA', 'GOOGL']
    
    print("🎯 Enhanced Stock Analysis:")
    print("-" * 60)
    
    results = []
    for symbol in top_symbols:
        print(f"Analyzing {symbol}...", end="")
        analysis = analyzer.comprehensive_analysis(symbol, market_context)
        
        if 'error' not in analysis:
            results.append(analysis)
            print(" ✅")
        else:
            print(" ❌")
    
    # Sort by final score
    results.sort(key=lambda x: x['final_score'], reverse=True)
    
    print("\n" + "=" * 80)
    print("📈 TOP OPPORTUNITIES")
    print("=" * 80)
    
    for result in results[:5]:  # Top 5
        rec = result['recommendation']
        risk = result['risk']
        
        print(f"\n🎯 {result['symbol']} - {rec['action']} ({rec['confidence']} confidence)")
        print(f"   💰 Price: ${result['current_price']:.2f}")
        print(f"   📊 Score: {result['final_score']:.1f}/100")
        print(f"   💼 Position Size: {rec['position_size_pct']:.1f}% of portfolio")
        print(f"   🛡️  Stop Loss: {rec['stop_loss_pct']}%")
        print(f"   ⚠️  Risk Level: {risk['risk_level']} (Vol: {risk['volatility']:.1f}%)")
        print(f"   ⏰ Hold Period: {rec['hold_period']}")
        
        print("   Key Reasons:")
        for reason in rec['key_reasons'][:3]:
            print(f"     • {reason}")
    
    print("\n" + "=" * 80)
    print("💡 ENHANCED TRADING INSIGHTS")
    print("=" * 80)
    print(f"🌍 Market Regime: {market_context.get('regime', 'UNKNOWN')}")
    print(f"📊 Risk Environment: {market_context.get('risk_level', 'MEDIUM')}")
    print(f"🎪 Sector Rotation: {sector_analysis.get('rotation_signal', 'NEUTRAL')}")
    print(f"📈 SPY Performance (Month): {market_context.get('month_return', 0):.1f}%")
    
    print("\n🎯 Action Items:")
    print("1. Review market regime before any trades")
    print("2. Use suggested position sizes (accounts for volatility)")
    print("3. Set stop losses based on individual stock risk")
    print("4. Monitor sector rotation for timing")
    print("5. Adjust strategy if market regime changes")


if __name__ == "__main__":
    run_enhanced_analysis()