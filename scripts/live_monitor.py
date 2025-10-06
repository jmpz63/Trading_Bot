"""
Live Trading Monitor - Watch Your Paper Trading Bot Performance
Run this in a separate terminal to monitor your bot's performance
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import os
import time

class LiveTradingMonitor:
    """
    Real-time monitor for paper trading bot performance
    """
    
    def __init__(self):
        self.session_start = datetime.now()
        self.price_history = []
        self.last_price = 0
        
    async def start_monitoring(self):
        """Start live monitoring dashboard"""
        
        print("📊 LIVE TRADING MONITOR DASHBOARD")
        print("="*60)
        print("📡 Fetching live BTC prices from Kraken...")
        print("💡 This shows the same data your paper trading bot sees")
        print("="*60)
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            try:
                while True:
                    # Fetch current market data
                    market_data = await self._fetch_market_data()
                    
                    if market_data:
                        # Display current values
                        self._display_live_dashboard(market_data)
                        
                        # Store price history
                        self.price_history.append({
                            'time': datetime.now(),
                            'price': market_data['price'],
                            'spread': market_data['spread_pct']
                        })
                        
                        # Keep only last 20 data points
                        if len(self.price_history) > 20:
                            self.price_history = self.price_history[-20:]
                    
                    # Wait 10 seconds (same as trading bot)
                    await asyncio.sleep(10)
                    
            except KeyboardInterrupt:
                print(f"\n⏹️  Monitoring stopped")
                self._show_session_summary()
            except Exception as e:
                print(f"\n❌ Monitor error: {e}")
    
    async def _fetch_market_data(self):
        """Fetch current market data from Kraken"""
        
        try:
            url = "https://api.kraken.com/0/public/Ticker?pair=XBTUSD"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'result' in data and 'XXBTZUSD' in data['result']:
                        ticker = data['result']['XXBTZUSD']
                        
                        ask = float(ticker['a'][0])
                        bid = float(ticker['b'][0])
                        price = (ask + bid) / 2
                        spread_pct = (ask - bid) / bid
                        
                        return {
                            'price': price,
                            'bid': bid,
                            'ask': ask,
                            'spread_pct': spread_pct,
                            'high_24h': float(ticker['h'][1]),
                            'low_24h': float(ticker['l'][1]),
                            'volume_24h': float(ticker['v'][1]),
                            'last_price': float(ticker['c'][0])
                        }
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
        
        return None
    
    def _display_live_dashboard(self, data):
        """Display live trading dashboard"""
        
        # Clear screen for live updates
        os.system('clear' if os.name == 'posix' else 'cls')
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print("📊 LIVE BTC/USD MARKET DASHBOARD")
        print("="*60)
        print(f"🕐 Time: {current_time}")
        print(f"📡 Data Source: Kraken Exchange (Real-time)")
        print("="*60)
        
        # Current price info
        price_change = data['price'] - self.last_price if self.last_price > 0 else 0
        change_symbol = "📈" if price_change > 0 else "📉" if price_change < 0 else "➡️"
        
        print(f"\n💰 CURRENT PRICE:")
        print(f"  {change_symbol} BTC/USD: ${data['price']:,.2f}")
        print(f"  📊 Bid: ${data['bid']:,.2f}")
        print(f"  📊 Ask: ${data['ask']:,.2f}")
        print(f"  📏 Spread: {data['spread_pct']:.4f} ({data['spread_pct']*100:.2f}%)")
        
        if price_change != 0:
            print(f"  📊 Change: ${price_change:+.2f}")
        
        # 24h stats
        print(f"\n📈 24H STATISTICS:")
        print(f"  📊 High: ${data['high_24h']:,.2f}")
        print(f"  📊 Low: ${data['low_24h']:,.2f}")
        print(f"  📊 Volume: {data['volume_24h']:,.0f} BTC")
        
        daily_range = data['high_24h'] - data['low_24h']
        current_position = (data['price'] - data['low_24h']) / daily_range
        
        print(f"  📍 Range Position: {current_position:.1%}")
        
        # Trading conditions analysis
        print(f"\n🎯 TRADING CONDITIONS:")
        
        spread_status = "✅ GOOD" if data['spread_pct'] < 0.0008 else "⚠️ WIDE" if data['spread_pct'] < 0.0015 else "❌ TOO WIDE"
        print(f"  📊 Spread Quality: {spread_status}")
        
        volatility = (data['high_24h'] - data['low_24h']) / data['price']
        vol_status = "🔥 HIGH" if volatility > 0.05 else "📊 NORMAL" if volatility > 0.02 else "😴 LOW"
        print(f"  📊 Volatility: {vol_status} ({volatility:.1%})")
        
        # Price trend (if we have history)
        if len(self.price_history) >= 3:
            recent_prices = [p['price'] for p in self.price_history[-3:]]
            if recent_prices[-1] > recent_prices[0]:
                trend = "📈 RISING"
            elif recent_prices[-1] < recent_prices[0]:
                trend = "📉 FALLING"
            else:
                trend = "➡️ SIDEWAYS"
            
            trend_change = (recent_prices[-1] / recent_prices[0] - 1) * 100
            print(f"  📊 Short Trend: {trend} ({trend_change:+.2f}%)")
        
        # Paper trading simulation
        print(f"\n💼 PAPER TRADING SIMULATION ($1000):")
        
        # Simulate what different position sizes would be worth
        positions = [0.001, 0.005, 0.01, 0.02]  # Different BTC amounts
        
        for btc_amount in positions:
            usd_value = btc_amount * data['price']
            position_pct = (usd_value / 1000) * 100
            
            print(f"  ₿ {btc_amount:.3f} BTC = ${usd_value:.2f} ({position_pct:.1f}% of portfolio)")
        
        # Show recent price history mini-chart
        if len(self.price_history) >= 5:
            print(f"\n📊 RECENT PRICE MOVEMENT:")
            
            for i, entry in enumerate(self.price_history[-5:]):
                time_str = entry['time'].strftime('%H:%M:%S')
                price = entry['price']
                
                if i > 0:
                    prev_price = self.price_history[len(self.price_history)-5+i-1]['price']
                    change = price - prev_price
                    symbol = "↗️" if change > 0 else "↘️" if change < 0 else "➡️"
                else:
                    symbol = "📊"
                
                print(f"    {time_str}: {symbol} ${price:,.2f}")
        
        # Instructions
        print(f"\n💡 INSTRUCTIONS:")
        print(f"  🔄 Updates every 10 seconds (same as your trading bot)")
        print(f"  ⏹️  Press Ctrl+C to stop monitoring")
        print(f"  📊 This shows exactly what your paper trading bot sees")
        
        # Update last price
        self.last_price = data['price']
    
    def _show_session_summary(self):
        """Show session summary when monitoring stops"""
        
        if len(self.price_history) >= 2:
            start_price = self.price_history[0]['price']
            end_price = self.price_history[-1]['price']
            total_change = end_price - start_price
            change_pct = (total_change / start_price) * 100
            
            session_duration = datetime.now() - self.session_start
            
            print(f"\n📊 MONITORING SESSION SUMMARY:")
            print(f"⏱️  Duration: {session_duration}")
            print(f"📈 Price Movement: ${start_price:,.2f} → ${end_price:,.2f}")
            print(f"📊 Total Change: ${total_change:+.2f} ({change_pct:+.2f}%)")
            
            # Calculate average spread
            avg_spread = sum(p['spread'] for p in self.price_history) / len(self.price_history)
            print(f"📊 Average Spread: {avg_spread:.4f} ({avg_spread*100:.2f}%)")

async def main():
    """Main function"""
    
    print("🚀 Starting Live Trading Monitor...")
    print("📊 This will show real-time market data that your paper trading bot uses")
    
    monitor = LiveTradingMonitor()
    await monitor.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())