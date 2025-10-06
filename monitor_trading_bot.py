#!/usr/bin/env python3
"""
Real-time Trading Bot Monitor & Optimizer
Monitors the 24/7 trading bot and provides optimization recommendations
"""

import time
import json
import subprocess
import psutil
import os
from datetime import datetime, timedelta
from pathlib import Path

class TradingBotMonitor:
    def __init__(self):
        self.bot_pid = None
        self.start_time = datetime.now()
        self.log_file = Path("logs/monitor.log")
        self.log_file.parent.mkdir(exist_ok=True)
        
        print("🔍 Trading Bot Monitor & Optimizer Started")
        print("=" * 60)
        
    def find_trading_bot_process(self):
        """Find the trading bot process"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python' or proc.info['name'] == 'python3':
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'btc_24_7_trader.py' in cmdline:
                        self.bot_pid = proc.info['pid']
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
        
    def get_system_stats(self):
        """Get system performance statistics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'memory_available': memory.available / (1024**3),  # GB
            'disk_usage': disk.percent,
            'disk_free': disk.free / (1024**3)  # GB
        }
        
    def get_bot_performance(self):
        """Get trading bot specific performance metrics"""
        if not self.bot_pid:
            return None
            
        try:
            proc = psutil.Process(self.bot_pid)
            cpu_percent = proc.cpu_percent()
            memory_mb = proc.memory_info().rss / (1024**2)
            
            return {
                'bot_cpu': cpu_percent,
                'bot_memory_mb': memory_mb,
                'bot_status': proc.status(),
                'bot_threads': proc.num_threads()
            }
        except psutil.NoSuchProcess:
            print("⚠️  Trading bot process not found!")
            return None
            
    def analyze_logs(self):
        """Analyze recent trading logs for performance insights"""
        log_files = [
            "logs/specialized_bots_session.json",
            "logs/pdf_enhanced_session.json",
            "logs/live_data_confirmation.json"
        ]
        
        recent_activity = {}
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        data = json.load(f)
                        recent_activity[log_file] = data
                except Exception as e:
                    print(f"Error reading {log_file}: {e}")
                    
        return recent_activity
        
    def optimization_recommendations(self, system_stats, bot_stats):
        """Provide optimization recommendations"""
        recommendations = []
        
        if system_stats['cpu_usage'] > 80:
            recommendations.append("🔥 HIGH CPU: Consider reducing trade frequency")
            
        if system_stats['memory_usage'] > 85:
            recommendations.append("💾 HIGH MEMORY: Bot may need memory optimization")
            
        if bot_stats and bot_stats['bot_cpu'] > 50:
            recommendations.append("�� BOT HIGH CPU: Consider optimizing trading algorithms")
            
        if system_stats['disk_free'] < 5:
            recommendations.append("💿 LOW DISK: Clean up old log files")
            
        if not recommendations:
            recommendations.append("✅ System running optimally")
            
        return recommendations
        
    def display_dashboard(self):
        """Display real-time monitoring dashboard"""
        os.system('clear')  # Clear screen
        
        print("🚀 CRYPTO TRADING BOT - 24/7 MONITORING DASHBOARD")
        print("=" * 70)
        print(f"📅 Monitor Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Uptime: {datetime.now() - self.start_time}")
        print()
        
        # Check if bot is running
        if not self.find_trading_bot_process():
            print("❌ TRADING BOT NOT RUNNING!")
            print("   Run: screen -dmS trading_bot python btc_24_7_trader.py")
            return
            
        print(f"✅ Trading Bot Running (PID: {self.bot_pid})")
        print()
        
        # System Statistics
        system_stats = self.get_system_stats()
        print("📊 SYSTEM PERFORMANCE:")
        print(f"   CPU Usage: {system_stats['cpu_usage']:.1f}%")
        print(f"   Memory Usage: {system_stats['memory_usage']:.1f}% ({system_stats['memory_available']:.1f}GB free)")
        print(f"   Disk Usage: {system_stats['disk_usage']:.1f}% ({system_stats['disk_free']:.1f}GB free)")
        print()
        
        # Bot Statistics
        bot_stats = self.get_bot_performance()
        if bot_stats:
            print("🤖 BOT PERFORMANCE:")
            print(f"   Bot CPU: {bot_stats['bot_cpu']:.1f}%")
            print(f"   Bot Memory: {bot_stats['bot_memory_mb']:.1f}MB")
            print(f"   Bot Status: {bot_stats['bot_status']}")
            print(f"   Bot Threads: {bot_stats['bot_threads']}")
            print()
            
        # Recent Activity
        recent_logs = self.analyze_logs()
        if recent_logs:
            print("📈 RECENT TRADING ACTIVITY:")
            for log_file, data in recent_logs.items():
                print(f"   {os.path.basename(log_file)}: {len(str(data))} chars")
            print()
            
        # Optimization Recommendations
        recommendations = self.optimization_recommendations(system_stats, bot_stats)
        print("💡 OPTIMIZATION RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"   {rec}")
        print()
        
        print("🔄 Press Ctrl+C to exit monitoring")
        print("=" * 70)
        
    def run_monitor(self):
        """Main monitoring loop"""
        try:
            while True:
                self.display_dashboard()
                time.sleep(10)  # Update every 10 seconds
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped. Trading bot continues running.")
            print("To stop trading bot: screen -r trading_bot, then Ctrl+C")

if __name__ == "__main__":
    monitor = TradingBotMonitor()
    monitor.run_monitor()
