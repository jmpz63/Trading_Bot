#!/usr/bin/env python3
"""
🤖 BOT MANAGER - Prevent Multiple Bot Conflicts
Manages single bot instance and prevents dangerous overlaps
"""

import os
import signal
import subprocess
import time
import psutil

class BotManager:
    def __init__(self):
        self.bot_process = None
        self.bot_script = "aggressive_trader_2_0.py"
    
    def is_bot_running(self):
        """Check if any trading bot is currently running"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any(self.bot_script in arg for arg in proc.info['cmdline']):
                    return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def kill_existing_bots(self):
        """Safely terminate any existing trading bots"""
        existing_pid = self.is_bot_running()
        if existing_pid:
            print(f"🛑 STOPPING existing bot (PID: {existing_pid})")
            try:
                os.kill(existing_pid, signal.SIGTERM)
                time.sleep(2)  # Give it time to clean up
                
                # Force kill if still running
                if self.is_bot_running():
                    os.kill(existing_pid, signal.SIGKILL)
                    print("🔥 Force terminated existing bot")
                else:
                    print("✅ Existing bot stopped gracefully")
            except ProcessLookupError:
                print("✅ Bot already stopped")
        else:
            print("✅ No existing bots found")
    
    def start_single_bot(self):
        """Start a single bot instance safely"""
        # First, ensure no other bots are running
        self.kill_existing_bots()
        
        print("🚀 STARTING SINGLE BOT INSTANCE...")
        print("⚠️  SAFE MODE: Only one bot will run at a time")
        print("=" * 50)
        
        # Start the bot
        try:
            self.bot_process = subprocess.Popen(
                ["python3", self.bot_script],
                cwd="/home/arm1/Trade_Bot"
            )
            
            print(f"✅ Bot started successfully (PID: {self.bot_process.pid})")
            print("🔍 Bot Status: ACTIVE")
            
            # Monitor the bot
            self.bot_process.wait()
            
        except KeyboardInterrupt:
            print("\n👋 Bot manager interrupted")
            if self.bot_process:
                self.bot_process.terminate()
        except Exception as e:
            print(f"❌ Error starting bot: {e}")
    
    def get_bot_status(self):
        """Get current bot status"""
        existing_pid = self.is_bot_running()
        
        if existing_pid:
            print(f"🟢 BOT STATUS: RUNNING (PID: {existing_pid})")
            print("⚠️  To start another bot, use 'stop' first")
        else:
            print("🔴 BOT STATUS: NOT RUNNING")
            print("✅ Safe to start new bot")

def main():
    manager = BotManager()
    
    print("🤖 AGGRESSIVE TRADER BOT MANAGER")
    print("=" * 40)
    print("🛡️  Prevents dangerous multi-bot conflicts")
    print()
    
    # Check current status
    manager.get_bot_status()
    print()
    
    while True:
        choice = input("Choose: [s]tart, [k]ill, [c]heck, [q]uit: ").lower()
        
        if choice == 's' or choice == 'start':
            manager.start_single_bot()
            break
        elif choice == 'k' or choice == 'kill':
            manager.kill_existing_bots()
        elif choice == 'c' or choice == 'check':
            manager.get_bot_status()
        elif choice == 'q' or choice == 'quit':
            print("👋 Bot manager exiting")
            break
        else:
            print("Invalid choice. Use s/k/c/q")

if __name__ == "__main__":
    main()