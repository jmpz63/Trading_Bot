"""
Improved Momentum Strategy for Trading Bot
Addresses spread issues and implements better entry/exit logic
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .base_strategy import BaseStrategy

class ImprovedMomentumStrategy(BaseStrategy):
    """
    Momentum strategy with spread awareness and better risk management
    """
    
    def __init__(self, name: str, config: Dict):
        super().__init__(name, config)
        
        # Strategy parameters
        self.rsi_oversold = config.get('rsi_oversold', 30)
        self.rsi_overbought = config.get('rsi_overbought', 70)
        self.min_spread_threshold = config.get('min_spread_threshold', 0.001)  # 0.1%
        self.momentum_period = config.get('momentum_period', 14)
        self.volume_threshold = config.get('volume_threshold', 1.2)
        
        # Data storage
        self.price_data = pd.DataFrame()
        self.last_signal_time = None
        self.cooldown_period = timedelta(minutes=config.get('cooldown_minutes', 5))
        
    async def generate_signals(self) -> List[Dict]:
        """
        Generate improved momentum signals with spread awareness
        """
        if len(self.price_data) < 20:  # Need minimum data
            return []
        
        # Check cooldown to prevent overtrading
        if self.last_signal_time and datetime.now() - self.last_signal_time < self.cooldown_period:
            return []
        
        signals = []
        latest = self.price_data.iloc[-1]
        
        # Calculate current spread
        bid = latest.get('bid', latest['close'])
        ask = latest.get('ask', latest['close'])
        spread_pct = (ask - bid) / bid if bid > 0 else 0
        
        # Only trade if spread is reasonable
        if spread_pct > self.min_spread_threshold:
            return []  # Skip high spread periods
        
        # Generate signal based on multiple conditions
        signal = self._analyze_conditions(latest)
        
        if signal['action'] != 'HOLD':
            signal.update({
                'symbol': 'BTCUSD',
                'timestamp': datetime.now(),
                'strategy': self.name,
                'spread_pct': spread_pct,
                'bid': bid,
                'ask': ask
            })
            signals.append(signal)
            self.last_signal_time = datetime.now()
        
        return signals
    
    def _analyze_conditions(self, latest: pd.Series) -> Dict:
        """Analyze market conditions for trading signals"""
        
        # Get technical indicators
        rsi = latest.get('rsi', 50)
        macd = latest.get('macd', 0)
        macd_signal = latest.get('macd_signal', 0)
        bb_position = latest.get('bb_position', 0.5)
        volume_ratio = latest.get('volume_ratio', 1.0)
        momentum = latest.get('momentum', 0)
        
        # Initialize signal
        signal = {
            'action': 'HOLD',
            'confidence': 0.0,
            'quantity': 0.0,
            'price': latest['close'],
            'reasoning': []
        }
        
        # Bull signal conditions
        bull_conditions = []
        if rsi < self.rsi_oversold:
            bull_conditions.append('RSI_OVERSOLD')
        if macd > macd_signal and macd > 0:
            bull_conditions.append('MACD_BULLISH')
        if bb_position < 0.2:  # Near lower Bollinger Band
            bull_conditions.append('BB_SUPPORT')
        if volume_ratio > self.volume_threshold:
            bull_conditions.append('HIGH_VOLUME')
        if momentum > 0:
            bull_conditions.append('POSITIVE_MOMENTUM')
        
        # Bear signal conditions
        bear_conditions = []
        if rsi > self.rsi_overbought:
            bear_conditions.append('RSI_OVERBOUGHT')
        if macd < macd_signal and macd < 0:
            bear_conditions.append('MACD_BEARISH')
        if bb_position > 0.8:  # Near upper Bollinger Band
            bear_conditions.append('BB_RESISTANCE')
        if volume_ratio > self.volume_threshold:
            bear_conditions.append('HIGH_VOLUME')
        if momentum < 0:
            bear_conditions.append('NEGATIVE_MOMENTUM')
        
        # Determine signal strength
        if len(bull_conditions) >= 3:
            signal['action'] = 'BUY'
            signal['confidence'] = min(len(bull_conditions) / 5.0, 1.0)
            signal['reasoning'] = bull_conditions
        elif len(bear_conditions) >= 3:
            signal['action'] = 'SELL'
            signal['confidence'] = min(len(bear_conditions) / 5.0, 1.0)
            signal['reasoning'] = bear_conditions
        
        return signal
    
    async def update_data(self, market_data: pd.DataFrame):
        """Update strategy with new market data and calculate indicators"""
        
        # Update price data
        self.price_data = market_data.copy()
        
        if len(self.price_data) > 0:
            # Calculate technical indicators
            self._calculate_rsi()
            self._calculate_macd()
            self._calculate_bollinger_bands()
            self._calculate_volume_indicators()
            self._calculate_momentum()
    
    def _calculate_rsi(self, period: int = 14):
        """Calculate Relative Strength Index"""
        if len(self.price_data) < period + 1:
            return
        
        delta = self.price_data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        self.price_data['rsi'] = 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD indicator"""
        if len(self.price_data) < slow:
            return
        
        ema_fast = self.price_data['close'].ewm(span=fast).mean()
        ema_slow = self.price_data['close'].ewm(span=slow).mean()
        
        self.price_data['macd'] = ema_fast - ema_slow
        self.price_data['macd_signal'] = self.price_data['macd'].ewm(span=signal).mean()
    
    def _calculate_bollinger_bands(self, period: int = 20, std_dev: int = 2):
        """Calculate Bollinger Bands and position"""
        if len(self.price_data) < period:
            return
        
        sma = self.price_data['close'].rolling(window=period).mean()
        std = self.price_data['close'].rolling(window=period).std()
        
        self.price_data['bb_upper'] = sma + (std * std_dev)
        self.price_data['bb_lower'] = sma - (std * std_dev)
        self.price_data['bb_middle'] = sma
        
        # Calculate position within bands (0 = lower band, 1 = upper band)
        bb_range = self.price_data['bb_upper'] - self.price_data['bb_lower']
        self.price_data['bb_position'] = (
            (self.price_data['close'] - self.price_data['bb_lower']) / bb_range
        ).fillna(0.5)
    
    def _calculate_volume_indicators(self):
        """Calculate volume-based indicators"""
        if 'volume' not in self.price_data.columns:
            self.price_data['volume_ratio'] = 1.0
            return
        
        volume_sma = self.price_data['volume'].rolling(window=20).mean()
        self.price_data['volume_ratio'] = self.price_data['volume'] / volume_sma
    
    def _calculate_momentum(self, period: int = 14):
        """Calculate price momentum"""
        if len(self.price_data) < period:
            return
        
        self.price_data['momentum'] = (
            self.price_data['close'] / self.price_data['close'].shift(period) - 1
        ) * 100
    
    def get_strategy_info(self) -> Dict:
        """Return strategy information and current state"""
        return {
            'name': self.name,
            'type': 'Improved Momentum',
            'parameters': {
                'rsi_oversold': self.rsi_oversold,
                'rsi_overbought': self.rsi_overbought,
                'min_spread_threshold': self.min_spread_threshold,
                'momentum_period': self.momentum_period,
                'cooldown_minutes': self.cooldown_period.total_seconds() / 60
            },
            'data_points': len(self.price_data),
            'last_signal': self.last_signal_time,
            'is_active': self.is_active
        }