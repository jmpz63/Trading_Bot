"""
Setup script for Trading Bot Dashboard
Install required packages and run the dashboard
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages for the dashboard"""
    
    requirements = [
        'streamlit',
        'plotly',
        'yfinance',
        'pandas',
        'numpy',
        'requests'
    ]
    
    print("📦 Installing dashboard requirements...")
    
    for package in requirements:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing {package}: {e}")
            return False
    
    return True

def create_dashboard_launcher():
    """Create dashboard launcher script"""
    
    launcher_content = '''#!/bin/bash
# Trading Dashboard Launcher

echo "🚀 Starting Trading Dashboard..."
echo "📊 Dashboard will open in your browser at http://localhost:8501"
echo ""

cd "$(dirname "$0")"

# Activate Python environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Install requirements if needed
python setup_dashboard.py --install-only

# Launch dashboard
streamlit run trading_dashboard.py --server.port 8501 --server.address 0.0.0.0

echo "📊 Dashboard stopped"
'''
    
    launcher_file = Path("launch_dashboard.sh")
    
    with open(launcher_file, 'w') as f:
        f.write(launcher_content)
    
    # Make executable
    os.chmod(launcher_file, 0o755)
    
    print(f"📄 Created launcher: {launcher_file}")
    return launcher_file

def main():
    """Main setup function"""
    
    print("🎯 TRADING BOT DASHBOARD SETUP")
    print("=" * 50)
    
    # Check if we're just installing
    if len(sys.argv) > 1 and sys.argv[1] == "--install-only":
        install_requirements()
        return
    
    # Full setup
    print("Setting up Trading Dashboard...")
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        return
    
    # Create launcher
    launcher = create_dashboard_launcher()
    
    print("\n✅ Dashboard setup complete!")
    print("\n📋 To start the dashboard:")
    print(f"   ./launch_dashboard.sh")
    print("   OR")
    print("   streamlit run trading_dashboard.py")
    print("\n🌐 Dashboard will be available at: http://localhost:8501")
    print("\n🎯 Features:")
    print("   • Real-time portfolio monitoring")
    print("   • Interactive trading interface")
    print("   • Performance analytics")
    print("   • Market signals and analysis")
    print("   • Trade history and P&L tracking")

if __name__ == "__main__":
    main()