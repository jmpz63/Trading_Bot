"""
Cryptocurrency Trading Integration
Add crypto trading capabilities to the paper trading system
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Dict, List
import requests
import json

class CryptoAnalyzer:
    """
    Cryptocurrency market analysis and trading signals
    """
    
    def __init__(self):
        self.major_cryptos = [
            'BTC-USD',   # Bitcoin
            'ETH-USD',   # Ethereum  
            'BNB-USD',   # Binance Coin
            'XRP-USD',   # XRP
            'ADA-USD',   # Cardano
            'SOL-USD',   # Solana
            'DOGE-USD',  # Dogecoin
            'AVAX-USD',  # Avalanche
            'DOT-USD',   # Polkadot
            'MATIC-USD'  # Polygon
        ]
    
    def get_crypto_data(self, symbol: str, period: str = "30d") -> Dict:
        """Get crypto data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            info = ticker.info
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            
            # Calculate basic metrics
            change_24h = current_price - prev_close
            change_pct_24h = (change_24h / prev_close) * 100 if prev_close > 0 else 0
            
            # Calculate volatility (30-day)
            returns = hist['Close'].pct_change().dropna()
            volatility_30d = returns.std() * (365**0.5) * 100  # Annualized volatility
            
            # Calculate moving averages
            ma_7 = hist['Close'].tail(7).mean()
            ma_30 = hist['Close'].tail(30).mean()
            
            # Volume analysis
            avg_volume = hist['Volume'].mean()
            current_volume = hist['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            return {
                'symbol': symbol,
                'current_price': float(current_price),
                'change_24h': float(change_24h),
                'change_pct_24h': float(change_pct_24h),
                'volatility_30d': float(volatility_30d),
                'ma_7': float(ma_7),
                'ma_30': float(ma_30),
                'volume_ratio': float(volume_ratio),
                'market_cap': info.get('marketCap', 0),
                'name': info.get('longName', symbol.replace('-USD', ''))
            }
            
        except Exception as e:
            print(f"Error getting data for {symbol}: {e}")
            return None
    
    def analyze_crypto_trend(self, data: Dict) -> Dict:
        """Analyze crypto trend and momentum"""
        
        score = 50  # Base score
        signals = []
        
        # Price vs Moving Averages (40% weight)
        if data['current_price'] > data['ma_7']:
            score += 8
            signals.append("Price above 7-day MA")
        else:
            score -= 8
            signals.append("Price below 7-day MA")
        
        if data['current_price'] > data['ma_30']:
            score += 12
            signals.append("Price above 30-day MA")
        else:
            score -= 12
            signals.append("Price below 30-day MA")
        
        if data['ma_7'] > data['ma_30']:
            score += 10
            signals.append("Short-term trend positive")
        else:
            score -= 10
            signals.append("Short-term trend negative")
        
        # Momentum (30% weight)
        if data['change_pct_24h'] > 5:
            score += 15
            signals.append("Strong 24h momentum (+5%)")
        elif data['change_pct_24h'] > 1:
            score += 8
            signals.append("Positive 24h momentum")
        elif data['change_pct_24h'] < -5:
            score -= 15
            signals.append("Weak 24h momentum (-5%)")
        elif data['change_pct_24h'] < -1:
            score -= 8
            signals.append("Negative 24h momentum")
        
        # Volume Analysis (20% weight)
        if data['volume_ratio'] > 1.5:
            score += 10
            signals.append("High volume (1.5x average)")
        elif data['volume_ratio'] > 1.2:
            score += 5
            signals.append("Above average volume")
        elif data['volume_ratio'] < 0.8:
            score -= 5
            signals.append("Below average volume")
        
        # Volatility Assessment (10% weight)
        if data['volatility_30d'] > 100:  # Very high volatility
            score -= 5
            signals.append("High volatility risk")
        elif data['volatility_30d'] < 50:  # Low volatility for crypto
            score += 5
            signals.append("Relatively stable")
        
        # Determine recommendation
        if score >= 70:
            recommendation = "BUY"
            confidence = "HIGH"
        elif score >= 60:
            recommendation = "BUY"
            confidence = "MEDIUM"
        elif score <= 30:
            recommendation = "SELL"
            confidence = "HIGH"
        elif score <= 40:
            recommendation = "SELL"
            confidence = "MEDIUM"
        else:
            recommendation = "HOLD"
            confidence = "LOW"
        
        return {
            'symbol': data['symbol'],
            'recommendation': recommendation,
            'confidence': confidence,
            'score': min(100, max(0, score)),
            'signals': signals,
            'current_price': data['current_price'],
            'change_pct_24h': data['change_pct_24h'],
            'volatility': data['volatility_30d'],
            'volume_ratio': data['volume_ratio']
        }
    
    def scan_crypto_opportunities(self) -> List[Dict]:
        """Scan all major cryptocurrencies for opportunities"""
        
        opportunities = []
        
        print("🔍 Analyzing Cryptocurrency Markets...")
        print("-" * 50)
        
        for symbol in self.major_cryptos:
            print(f"Analyzing {symbol.replace('-USD', '')}...", end=" ")
            
            data = self.get_crypto_data(symbol)
            if data:
                analysis = self.analyze_crypto_trend(data)
                opportunities.append(analysis)
                
                print(f"{analysis['recommendation']} (Score: {analysis['score']:.1f})")
            else:
                print("Error")
        
        # Sort by score
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        return opportunities
    
    def get_crypto_market_summary(self) -> Dict:
        """Get overall crypto market summary"""
        
        try:
            # Get Bitcoin dominance and market overview
            btc_data = self.get_crypto_data('BTC-USD')
            eth_data = self.get_crypto_data('ETH-USD')
            
            if not btc_data or not eth_data:
                return {'error': 'Unable to fetch market data'}
            
            # Simple market sentiment based on major cryptos
            btc_trend = "Bullish" if btc_data['change_pct_24h'] > 0 else "Bearish"
            eth_trend = "Bullish" if eth_data['change_pct_24h'] > 0 else "Bearish"
            
            # Overall market sentiment
            if btc_data['change_pct_24h'] > 0 and eth_data['change_pct_24h'] > 0:
                market_sentiment = "BULLISH"
            elif btc_data['change_pct_24h'] < -2 and eth_data['change_pct_24h'] < -2:
                market_sentiment = "BEARISH"
            else:
                market_sentiment = "MIXED"
            
            return {
                'market_sentiment': market_sentiment,
                'btc_price': btc_data['current_price'],
                'btc_change_24h': btc_data['change_pct_24h'],
                'btc_trend': btc_trend,
                'eth_price': eth_data['current_price'],
                'eth_change_24h': eth_data['change_pct_24h'], 
                'eth_trend': eth_trend,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Market summary failed: {e}'}


def run_crypto_analysis():
    """Run cryptocurrency market analysis"""
    
    print("🪙 CRYPTOCURRENCY MARKET ANALYSIS")
    print("=" * 60)
    
    analyzer = CryptoAnalyzer()
    
    # Get market summary
    market_summary = analyzer.get_crypto_market_summary()
    
    if 'error' not in market_summary:
        print("📊 CRYPTO MARKET OVERVIEW:")
        print("-" * 50)
        print(f"🔹 Market Sentiment: {market_summary['market_sentiment']}")
        print(f"₿ Bitcoin: ${market_summary['btc_price']:,.2f} ({market_summary['btc_change_24h']:+.2f}%)")
        print(f"Ξ Ethereum: ${market_summary['eth_price']:,.2f} ({market_summary['eth_change_24h']:+.2f}%)")
        print()
    
    # Scan opportunities
    opportunities = analyzer.scan_crypto_opportunities()
    
    print()
    print("🎯 TOP CRYPTO OPPORTUNITIES:")
    print("-" * 50)
    
    # Show top opportunities
    buy_opportunities = [opp for opp in opportunities if opp['recommendation'] == 'BUY'][:5]
    sell_opportunities = [opp for opp in opportunities if opp['recommendation'] == 'SELL'][:3]
    
    if buy_opportunities:
        print("🟢 BUY Signals:")
        for opp in buy_opportunities:
            crypto_name = opp['symbol'].replace('-USD', '')
            print(f"  {crypto_name}: ${opp['current_price']:,.2f} (Score: {opp['score']:.1f}/100)")
            print(f"    24h: {opp['change_pct_24h']:+.2f}% | Vol: {opp['volatility']:.1f}%")
    
    if sell_opportunities:
        print("\n🔴 SELL Signals:")
        for opp in sell_opportunities:
            crypto_name = opp['symbol'].replace('-USD', '')
            print(f"  {crypto_name}: ${opp['current_price']:,.2f} (Score: {opp['score']:.1f}/100)")
            print(f"    24h: {opp['change_pct_24h']:+.2f}% | Vol: {opp['volatility']:.1f}%")
    
    print()
    print("💡 CRYPTO TRADING INSIGHTS:")
    print("-" * 50)
    
    if market_summary.get('market_sentiment') == 'BULLISH':
        print("🟢 Crypto market showing bullish momentum")
        print("💡 Consider BUY positions on strong altcoins")
    elif market_summary.get('market_sentiment') == 'BEARISH':
        print("🔴 Crypto market under pressure")
        print("💡 Consider defensive positioning or wait for bounce")
    else:
        print("🟡 Mixed crypto market signals")
        print("💡 Focus on individual coin strength rather than market direction")
    
    return opportunities


if __name__ == "__main__":
    run_crypto_analysis()