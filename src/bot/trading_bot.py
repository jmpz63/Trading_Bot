"""
APM Trading Bot - Main Trading Bot Class
Advanced algorithmic trading bot with risk management and strategy execution
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import yaml
from pathlib import Path

from ..data.market_data import MarketDataManager
from ..strategies.base_strategy import BaseStrategy
from ..risk.risk_manager import RiskManager
from ..utils.logger import setup_logger

class TradingBot:
    """
    Main trading bot class that orchestrates all trading operations
    """
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize the trading bot with configuration"""
        self.config = self._load_config(config_path)
        self.logger = setup_logger(self.config['logging'])
        
        # Initialize components
        self.market_data = MarketDataManager(self.config)
        self.risk_manager = RiskManager(self.config)
        self.strategies: List[BaseStrategy] = []
        self.is_running = False
        self.portfolio_value = 0.0
        
        self.logger.info("Trading bot initialized")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            raise
    
    async def start(self):
        """Start the trading bot"""
        if self.is_running:
            self.logger.warning("Bot is already running")
            return
            
        self.logger.info("Starting trading bot...")
        self.is_running = True
        
        try:
            # Start market data feeds
            await self.market_data.start()
            
            # Initialize strategies
            await self._initialize_strategies()
            
            # Start main trading loop
            await self._main_loop()
            
        except Exception as e:
            self.logger.error(f"Error in trading bot: {e}")
            await self.stop()
    
    async def stop(self):
        """Stop the trading bot"""
        self.logger.info("Stopping trading bot...")
        self.is_running = False
        
        # Close all positions if configured
        if self.config['trading'].get('close_positions_on_stop', True):
            await self._close_all_positions()
        
        # Stop market data feeds
        await self.market_data.stop()
        
        self.logger.info("Trading bot stopped")
    
    async def _main_loop(self):
        """Main trading loop"""
        update_interval = self.config['data']['update_interval']
        
        while self.is_running:
            try:
                # Update market data
                await self.market_data.update()
                
                # Execute strategies
                for strategy in self.strategies:
                    if strategy.is_active:
                        signals = await strategy.generate_signals()
                        await self._process_signals(signals)
                
                # Update portfolio
                await self._update_portfolio()
                
                # Risk management check
                await self.risk_manager.check_portfolio_risk(self.portfolio_value)
                
                # Wait for next update
                await asyncio.sleep(update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(update_interval)
    
    async def _initialize_strategies(self):
        """Initialize trading strategies"""
        # This would load strategies from configuration
        # For now, we'll add them programmatically
        self.logger.info("Initializing trading strategies")
    
    async def _process_signals(self, signals: List[Dict]):
        """Process trading signals from strategies"""
        for signal in signals:
            # Risk check before executing
            if await self.risk_manager.validate_trade(signal):
                await self._execute_trade(signal)
            else:
                self.logger.warning(f"Trade rejected by risk manager: {signal}")
    
    async def _execute_trade(self, signal: Dict):
        """Execute a trade based on signal"""
        self.logger.info(f"Executing trade: {signal}")
        
        # This would interface with exchange API
        # For now, log the trade
        if self.config['trading']['paper_trading']:
            self.logger.info(f"Paper trade executed: {signal}")
        else:
            # Real trading implementation
            pass
    
    async def _update_portfolio(self):
        """Update portfolio value and positions"""
        # This would calculate current portfolio value
        # For now, use a placeholder
        self.portfolio_value = 10000.0  # Placeholder
    
    async def _close_all_positions(self):
        """Close all open positions"""
        self.logger.info("Closing all positions...")
        # Implementation to close positions
    
    def add_strategy(self, strategy: BaseStrategy):
        """Add a trading strategy"""
        self.strategies.append(strategy)
        self.logger.info(f"Added strategy: {strategy.__class__.__name__}")
    
    def get_status(self) -> Dict:
        """Get current bot status"""
        return {
            "is_running": self.is_running,
            "portfolio_value": self.portfolio_value,
            "active_strategies": len([s for s in self.strategies if s.is_active]),
            "timestamp": datetime.now().isoformat()
        }

async def main():
    """Main entry point for the trading bot"""
    bot = TradingBot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        print("\nShutdown signal received...")
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())