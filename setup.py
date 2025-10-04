#!/usr/bin/env python3
"""
Trading Bot Setup Script
Initialize the complete trading bot environment
"""

import os
import sys
import subprocess
from pathlib import Path

def create_virtual_environment():
    """Create Python virtual environment"""
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print("✅ Virtual environment created")

def install_dependencies():
    """Install required packages"""
    print("Installing dependencies...")
    
    # Determine pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = "venv/Scripts/pip"
    else:  # Unix/Linux/macOS
        pip_path = "venv/bin/pip"
    
    subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
    print("✅ Dependencies installed")

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    
    directories = [
        "data/historical",
        "data/real_time", 
        "data/logs",
        "backtesting/reports",
        "config/exchanges"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def create_example_files():
    """Create example configuration and script files"""
    print("Creating example files...")
    
    # Example exchange configuration
    exchange_config = """# Exchange API Configuration
# Copy this file and add your API credentials

binance:
  api_key: "your_api_key_here"
  secret: "your_secret_here"
  sandbox: true  # Set to false for live trading
  testnet: true  # Use testnet for testing

coinbase:
  api_key: "your_api_key_here"
  secret: "your_secret_here"
  passphrase: "your_passphrase_here"
  sandbox: true
"""
    
    with open("config/exchanges/example.yaml", "w") as f:
        f.write(exchange_config)
    
    # Example strategy configuration
    strategy_config = """# Trading Strategy Configuration

momentum_strategy:
  enabled: true
  timeframe: "1h"
  rsi_period: 14
  rsi_overbought: 70
  rsi_oversold: 30
  
mean_reversion_strategy:
  enabled: false
  timeframe: "15m" 
  bollinger_period: 20
  bollinger_std: 2
"""
    
    with open("config/strategies.yaml", "w") as f:
        f.write(strategy_config)
    
    print("✅ Example files created")

def setup_git_integration():
    """Setup git integration if in APM system"""
    apm_path = Path("../APM")
    if apm_path.exists():
        print("APM system detected - setting up integration...")
        
        # Create symbolic link or copy to APM Projects
        apm_projects = apm_path / "Projects" / "Active" / "Trade_Bot"
        if not apm_projects.exists():
            print(f"Consider adding this project to APM: {apm_projects}")
        
        print("✅ APM integration ready")

def main():
    """Main setup function"""
    print("🚀 Setting up Trading Bot Project...")
    print("=" * 50)
    
    try:
        create_directories()
        create_example_files()
        
        # Only create venv if it doesn't exist
        if not Path("venv").exists():
            create_virtual_environment()
            install_dependencies()
        else:
            print("Virtual environment already exists")
        
        setup_git_integration()
        
        print("\n" + "=" * 50)
        print("✅ Trading Bot setup complete!")
        print("\n📋 Next Steps:")
        print("1. Activate virtual environment:")
        if os.name == 'nt':
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("2. Edit config/settings.yaml with your preferences")
        print("3. Add exchange API keys to config/exchanges/")
        print("4. Run: python -m src.bot.trading_bot")
        print("\n🔒 Security Note:")
        print("   Never commit API keys to version control!")
        print("   Use environment variables or encrypted storage.")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()