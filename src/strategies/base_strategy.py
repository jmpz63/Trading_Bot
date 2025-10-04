"""
Base Strategy Class for Trading Bot
All trading strategies should inherit from this class
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies
    """
    
    def __init__(self, name: str, config: Dict):
        """Initialize the strategy"""
        self.name = name
        self.config = config
        self.is_active = True
        self.positions = {}
        self.performance_metrics = {}
        
    @abstractmethod
    async def generate_signals(self) -> List[Dict]:
        """
        Generate trading signals based on market data
        
        Returns:
            List of signal dictionaries with format:
            {
                'symbol': 'BTCUSDT',
                'action': 'BUY' or 'SELL',
                'quantity': float,
                'price': float,
                'timestamp': datetime,
                'confidence': float (0-1),
                'strategy': str
            }
        """
        pass
    
    @abstractmethod
    async def update_data(self, market_data: pd.DataFrame):
        """Update strategy with new market data"""
        pass
    
    def activate(self):
        """Activate the strategy"""
        self.is_active = True
    
    def deactivate(self):
        """Deactivate the strategy"""
        self.is_active = False
    
    def get_performance(self) -> Dict:
        """Get strategy performance metrics"""
        return self.performance_metrics
    
    def get_positions(self) -> Dict:
        """Get current strategy positions"""
        return self.positions