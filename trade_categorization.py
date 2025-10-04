"""
Trading Strategy Categorization System
Classify trades by strategy type and time horizon
"""

from datetime import datetime, timedelta
from typing import Dict, List
from enum import Enum

class TradeStrategy(Enum):
    """Trading strategy categories"""
    DAY_TRADING = "Day Trading"           # Same day entry/exit
    SWING_TRADING = "Swing Trading"       # 2-10 days hold
    POSITION_TRADING = "Position Trading" # 2-8 weeks hold
    LONG_TERM = "Long Term"              # 2+ months hold
    SCALPING = "Scalping"                # Minutes to hours
    MOMENTUM = "Momentum"                # Trend following
    MEAN_REVERSION = "Mean Reversion"    # Counter-trend
    BREAKOUT = "Breakout"                # Support/resistance breaks
    
class TradeCategorizer:
    """
    Categorize trades by strategy type and characteristics
    """
    
    def __init__(self):
        self.strategy_definitions = {
            TradeStrategy.DAY_TRADING: {
                'hold_period_hours': (0, 24),
                'typical_profit_target': 0.5,  # 0.5%
                'risk_tolerance': 'Low',
                'market_focus': 'Intraday momentum',
                'description': 'Same-day entry and exit, capitalize on intraday price movements'
            },
            TradeStrategy.SWING_TRADING: {
                'hold_period_days': (2, 10), 
                'typical_profit_target': 3.0,  # 3%
                'risk_tolerance': 'Medium',
                'market_focus': 'Multi-day trends',
                'description': 'Hold 2-10 days, capture short-term price swings'
            },
            TradeStrategy.POSITION_TRADING: {
                'hold_period_weeks': (2, 8),
                'typical_profit_target': 10.0,  # 10%
                'risk_tolerance': 'Medium-High', 
                'market_focus': 'Medium-term trends',
                'description': 'Hold 2-8 weeks, ride intermediate trends'
            },
            TradeStrategy.LONG_TERM: {
                'hold_period_months': (2, 24),
                'typical_profit_target': 25.0,  # 25%
                'risk_tolerance': 'High',
                'market_focus': 'Long-term growth',
                'description': 'Hold 2+ months, fundamental value investing'
            },
            TradeStrategy.MOMENTUM: {
                'hold_period_days': (1, 30),
                'typical_profit_target': 8.0,  # 8%
                'risk_tolerance': 'High',
                'market_focus': 'Strong trends',
                'description': 'Follow strong momentum in price and volume'
            }
        }
    
    def categorize_trade_intent(self, symbol: str, analysis: Dict, market_context: Dict) -> Dict:
        """
        Categorize a trade based on analysis signals and market conditions
        """
        
        # Default strategy
        primary_strategy = TradeStrategy.SWING_TRADING
        secondary_strategies = []
        
        # Determine primary strategy based on analysis
        score = analysis.get('final_score', analysis.get('score', 50))
        confidence = analysis.get('confidence', 'MEDIUM')
        
        # Asset type considerations
        is_crypto = '-USD' in symbol
        is_etf = symbol in ['SPY', 'QQQ', 'DIA', 'IWM']
        is_tech_stock = symbol in ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA']
        
        # Strategy classification logic
        if is_crypto:
            # Crypto tends to be more volatile - shorter holds
            if score >= 80:
                primary_strategy = TradeStrategy.MOMENTUM
                secondary_strategies = [TradeStrategy.SWING_TRADING]
            elif score >= 70:
                primary_strategy = TradeStrategy.SWING_TRADING
            else:
                primary_strategy = TradeStrategy.POSITION_TRADING
                
        elif is_etf:
            # ETFs good for longer holds and trends
            if market_context.get('regime') == 'BULL':
                primary_strategy = TradeStrategy.POSITION_TRADING
                secondary_strategies = [TradeStrategy.LONG_TERM]
            else:
                primary_strategy = TradeStrategy.SWING_TRADING
                
        elif is_tech_stock:
            # Tech stocks - momentum and swing trading
            if score >= 75 and confidence == 'HIGH':
                primary_strategy = TradeStrategy.MOMENTUM
                secondary_strategies = [TradeStrategy.SWING_TRADING]
            else:
                primary_strategy = TradeStrategy.SWING_TRADING
                
        else:
            # Regular stocks - swing and position trading
            if score >= 70:
                primary_strategy = TradeStrategy.SWING_TRADING
            else:
                primary_strategy = TradeStrategy.POSITION_TRADING
        
        # Determine hold period and targets
        strategy_info = self.strategy_definitions[primary_strategy]
        
        # Calculate expected hold period
        if 'hold_period_days' in strategy_info:
            min_days, max_days = strategy_info['hold_period_days']
            expected_hold_days = (min_days + max_days) // 2
        elif 'hold_period_weeks' in strategy_info:
            min_weeks, max_weeks = strategy_info['hold_period_weeks']
            expected_hold_days = ((min_weeks + max_weeks) // 2) * 7
        elif 'hold_period_months' in strategy_info:
            min_months, max_months = strategy_info['hold_period_months']
            expected_hold_days = ((min_months + max_months) // 2) * 30
        else:
            expected_hold_days = 7  # Default 1 week
        
        # Adjust based on volatility and score
        if is_crypto and score >= 80:
            expected_hold_days = max(2, expected_hold_days // 2)  # Shorter for high-score crypto
        elif score >= 75:
            expected_hold_days = int(expected_hold_days * 1.2)  # Slightly longer for high conviction
        elif score < 60:
            expected_hold_days = max(1, expected_hold_days // 2)  # Shorter for lower conviction
        
        # Calculate profit target
        base_target = strategy_info['typical_profit_target']
        
        if is_crypto:
            profit_target = base_target * 1.5  # Higher targets for crypto
        elif score >= 80:
            profit_target = base_target * 1.3  # Higher targets for strong signals
        else:
            profit_target = base_target
        
        # Calculate stop loss
        if is_crypto:
            stop_loss = -profit_target * 0.6  # Wider stops for crypto
        else:
            stop_loss = -profit_target * 0.5  # 2:1 risk/reward ratio
        
        return {
            'primary_strategy': primary_strategy.value,
            'secondary_strategies': [s.value for s in secondary_strategies],
            'expected_hold_days': expected_hold_days,
            'expected_hold_period': self.format_hold_period(expected_hold_days),
            'profit_target_pct': profit_target,
            'stop_loss_pct': stop_loss,
            'risk_tolerance': strategy_info['risk_tolerance'],
            'market_focus': strategy_info['market_focus'],
            'strategy_description': strategy_info['description'],
            'rationale': self.generate_rationale(symbol, analysis, primary_strategy, is_crypto, is_etf, is_tech_stock)
        }
    
    def format_hold_period(self, days: int) -> str:
        """Format hold period in human readable format"""
        if days < 1:
            return "Intraday"
        elif days == 1:
            return "1 day"
        elif days < 7:
            return f"{days} days"
        elif days < 30:
            weeks = days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''}"
        else:
            months = days // 30
            return f"{months} month{'s' if months > 1 else ''}"
    
    def generate_rationale(self, symbol: str, analysis: Dict, strategy: TradeStrategy, 
                          is_crypto: bool, is_etf: bool, is_tech: bool) -> str:
        """Generate explanation for strategy choice"""
        
        score = analysis.get('final_score', analysis.get('score', 50))
        
        rationales = []
        
        if is_crypto:
            rationales.append("Cryptocurrency - high volatility asset class")
        elif is_etf:
            rationales.append("ETF - diversified, lower volatility")
        elif is_tech:
            rationales.append("Technology stock - growth-oriented")
        else:
            rationales.append("Individual stock - medium risk profile")
        
        if score >= 80:
            rationales.append(f"Very strong signal (Score: {score:.1f}) - high conviction trade")
        elif score >= 70:
            rationales.append(f"Strong signal (Score: {score:.1f}) - good setup")
        elif score >= 60:
            rationales.append(f"Moderate signal (Score: {score:.1f}) - cautious approach")
        else:
            rationales.append(f"Weak signal (Score: {score:.1f}) - defensive positioning")
        
        if strategy == TradeStrategy.MOMENTUM:
            rationales.append("Strong momentum detected - ride the trend")
        elif strategy == TradeStrategy.SWING_TRADING:
            rationales.append("Multi-day price pattern - capture swing moves")
        elif strategy == TradeStrategy.POSITION_TRADING:
            rationales.append("Medium-term trend - ride intermediate moves")
        elif strategy == TradeStrategy.LONG_TERM:
            rationales.append("Fundamental strength - long-term value play")
        
        return " | ".join(rationales)
    
    def categorize_existing_trade(self, trade_record: Dict) -> Dict:
        """
        Categorize an existing trade based on actual hold time and performance
        """
        
        entry_time = datetime.fromisoformat(trade_record['timestamp'])
        current_time = datetime.now()
        hold_time = current_time - entry_time
        hold_days = hold_time.days
        hold_hours = hold_time.total_seconds() / 3600
        
        # Determine actual strategy based on hold time
        if hold_hours < 24:
            actual_strategy = TradeStrategy.DAY_TRADING
        elif hold_days <= 10:
            actual_strategy = TradeStrategy.SWING_TRADING
        elif hold_days <= 56:  # 8 weeks
            actual_strategy = TradeStrategy.POSITION_TRADING
        else:
            actual_strategy = TradeStrategy.LONG_TERM
        
        return {
            'actual_strategy': actual_strategy.value,
            'hold_time_days': hold_days,
            'hold_time_formatted': self.format_hold_period(hold_days),
            'entry_date': trade_record['timestamp'][:10],
            'symbol': trade_record['symbol'],
            'action': trade_record['action']
        }

def display_trade_categorization(symbol: str, analysis: Dict, market_context: Dict = None):
    """Display trade categorization for a specific symbol"""
    
    categorizer = TradeCategorizer()
    
    if market_context is None:
        market_context = {'regime': 'BULL'}  # Default
    
    category = categorizer.categorize_trade_intent(symbol, analysis, market_context)
    
    print(f"🎯 TRADE STRATEGY CATEGORIZATION: {symbol}")
    print("=" * 60)
    print(f"📋 Primary Strategy: {category['primary_strategy']}")
    
    if category['secondary_strategies']:
        print(f"📋 Secondary: {', '.join(category['secondary_strategies'])}")
    
    print(f"⏰ Expected Hold: {category['expected_hold_period']}")
    print(f"🎯 Profit Target: +{category['profit_target_pct']:.1f}%")
    print(f"🛡️  Stop Loss: {category['stop_loss_pct']:.1f}%")
    print(f"⚡ Risk Level: {category['risk_tolerance']}")
    print(f"📊 Focus: {category['market_focus']}")
    print(f"📝 Description: {category['strategy_description']}")
    print(f"🧠 Rationale: {category['rationale']}")
    
    return category

if __name__ == "__main__":
    # Example usage
    sample_analysis = {
        'final_score': 75,
        'confidence': 'HIGH',
        'action': 'BUY'
    }
    
    sample_market = {
        'regime': 'BULL'
    }
    
    print("📊 STRATEGY CATEGORIZATION EXAMPLES:")
    print()
    
    # Test different asset types
    assets = [
        ('AAPL', 'Tech Stock'),
        ('SPY', 'ETF'),
        ('BTC-USD', 'Cryptocurrency'),
        ('F', 'Regular Stock')
    ]
    
    for symbol, description in assets:
        print(f"\n{description}: {symbol}")
        print("-" * 40)
        category = display_trade_categorization(symbol, sample_analysis, sample_market)
        print()