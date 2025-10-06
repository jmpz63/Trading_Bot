"""
QUANTUM RISK MANAGEMENT SYSTEM
Enterprise-Grade Risk Controls for Algorithmic Trading

Features:
- Portfolio-level risk monitoring
- Real-time VaR calculation
- Dynamic position sizing with Kelly Criterion
- Regime-aware risk adjustment
- Multi-level emergency stops
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    EXTREME = "extreme"

@dataclass
class RiskMetrics:
    portfolio_var_95: float      # 95% Value at Risk
    portfolio_var_99: float      # 99% Value at Risk
    current_drawdown: float      # Current drawdown from peak
    max_drawdown: float          # Maximum historical drawdown
    volatility_annual: float     # Annualized volatility
    sharpe_ratio: float          # Risk-adjusted returns
    kelly_fraction: float        # Optimal position size
    risk_level: RiskLevel        # Overall risk assessment
    concentration_risk: float    # Single position concentration
    liquidity_risk: float        # Market liquidity risk

class QuantumRiskManager:
    """
    Professional risk management system with institutional-grade controls
    """
    
    def __init__(self):
        # Risk limits (institutional standards)
        self.max_portfolio_var_95 = 0.02   # 2% daily VaR limit
        self.max_portfolio_var_99 = 0.04   # 4% daily VaR limit  
        self.max_daily_drawdown = 0.05     # 5% max daily drawdown
        self.max_total_drawdown = 0.15     # 15% max total drawdown
        self.max_position_size = 0.25      # 25% max single position
        self.min_liquidity_ratio = 1.5     # Minimum volume/position ratio
        
        # Kelly Criterion parameters
        self.max_kelly_fraction = 0.25     # Maximum Kelly position size
        self.min_kelly_fraction = 0.01     # Minimum Kelly position size
        self.kelly_safety_factor = 0.5     # Reduce Kelly by 50% for safety
        
        # Risk monitoring
        self.return_history = []
        self.drawdown_history = []
        self.position_history = []
        self.volatility_lookback = 30
        
        # Performance tracking
        self.peak_portfolio_value = 0.0
        self.daily_start_value = 0.0
        self.trades_today = 0
        self.max_daily_trades = 8
        
        # Emergency states
        self.emergency_stop_active = False
        self.risk_override_active = False
        
    def calculate_portfolio_risk(self, 
                               portfolio_value: float,
                               positions: Dict[str, float],
                               price_data: Dict[str, List[float]],
                               market_data: Dict[str, float]) -> RiskMetrics:
        """
        Calculate comprehensive portfolio risk metrics
        """
        
        # Update return history
        if hasattr(self, 'last_portfolio_value') and self.last_portfolio_value > 0:
            portfolio_return = (portfolio_value / self.last_portfolio_value) - 1
            self.return_history.append(portfolio_return)
            
            # Keep only recent history for performance
            if len(self.return_history) > 200:
                self.return_history = self.return_history[-100:]
        
        self.last_portfolio_value = portfolio_value
        
        # Update peak and calculate drawdown
        if portfolio_value > self.peak_portfolio_value:
            self.peak_portfolio_value = portfolio_value
        
        current_drawdown = (self.peak_portfolio_value - portfolio_value) / self.peak_portfolio_value
        self.drawdown_history.append(current_drawdown)
        
        # Calculate VaR if we have sufficient data
        if len(self.return_history) >= 30:
            returns_array = np.array(self.return_history[-self.volatility_lookback:])
            
            # Portfolio VaR calculation
            var_95 = np.percentile(returns_array, 5)  # 5th percentile = 95% VaR
            var_99 = np.percentile(returns_array, 1)  # 1st percentile = 99% VaR
            
            # Annualized volatility  
            volatility = np.std(returns_array) * np.sqrt(288)  # 288 = 24*12 (5min periods)
            
            # Sharpe ratio calculation
            mean_return = np.mean(returns_array)
            sharpe_ratio = (mean_return / np.std(returns_array)) * np.sqrt(288) if np.std(returns_array) > 0 else 0
            
        else:
            var_95 = -0.02  # Conservative default
            var_99 = -0.04
            volatility = 0.20
            sharpe_ratio = 0.0
        
        # Calculate optimal Kelly fraction
        kelly_fraction = self._calculate_kelly_fraction(market_data, volatility)
        
        # Assess concentration risk
        if positions and portfolio_value > 0:
            position_values = {asset: qty * price for asset, qty in positions.items() 
                             for price in [market_data.get(f"{asset}_price", 0)]}
            max_position_value = max(position_values.values()) if position_values else 0
            concentration_risk = max_position_value / portfolio_value
        else:
            concentration_risk = 0.0
        
        # Assess liquidity risk
        liquidity_risk = self._assess_liquidity_risk(market_data)
        
        # Determine overall risk level
        risk_level = self._determine_risk_level(var_95, var_99, current_drawdown, 
                                              volatility, concentration_risk, liquidity_risk)
        
        return RiskMetrics(
            portfolio_var_95=-var_95,  # Convert to positive for display
            portfolio_var_99=-var_99,
            current_drawdown=current_drawdown,
            max_drawdown=max(self.drawdown_history) if self.drawdown_history else 0,
            volatility_annual=volatility,
            sharpe_ratio=sharpe_ratio,
            kelly_fraction=kelly_fraction,
            risk_level=risk_level,
            concentration_risk=concentration_risk,
            liquidity_risk=liquidity_risk
        )
    
    def calculate_optimal_position_size(self,
                                      signal_confidence: float,
                                      expected_return: float,
                                      expected_loss: float,
                                      portfolio_value: float,
                                      current_volatility: float) -> float:
        """
        Calculate optimal position size using Kelly Criterion with safety adjustments
        """
        
        # Kelly Criterion: f = (bp - q) / b
        # Where: b = odds, p = win probability, q = loss probability
        win_prob = signal_confidence
        loss_prob = 1 - win_prob
        
        if expected_return > 0 and expected_loss > 0 and win_prob > 0.5:
            # Kelly fraction calculation
            kelly_fraction = (win_prob * expected_return - loss_prob * expected_loss) / expected_return
            
            # Apply safety factor
            kelly_fraction *= self.kelly_safety_factor
            
            # Enforce limits
            kelly_fraction = max(self.min_kelly_fraction, 
                               min(kelly_fraction, self.max_kelly_fraction))
        else:
            kelly_fraction = self.min_kelly_fraction
        
        # Volatility adjustment - reduce size in high volatility
        vol_adjustment = min(0.2 / max(current_volatility, 0.1), 2.0)
        
        # Calculate raw position size
        raw_position_size = portfolio_value * kelly_fraction * vol_adjustment
        
        # Apply maximum position size limit
        max_position = portfolio_value * self.max_position_size
        
        final_position_size = min(raw_position_size, max_position)
        
        return final_position_size
    
    def check_risk_limits(self, risk_metrics: RiskMetrics, 
                         portfolio_value: float) -> Tuple[bool, List[str]]:
        """
        Check if current risk levels exceed defined limits
        """
        
        violations = []
        
        # VaR limit checks
        if risk_metrics.portfolio_var_95 > self.max_portfolio_var_95:
            violations.append(f"95% VaR exceeded: {risk_metrics.portfolio_var_95:.2%} > {self.max_portfolio_var_95:.2%}")
        
        if risk_metrics.portfolio_var_99 > self.max_portfolio_var_99:
            violations.append(f"99% VaR exceeded: {risk_metrics.portfolio_var_99:.2%} > {self.max_portfolio_var_99:.2%}")
        
        # Drawdown checks  
        if risk_metrics.current_drawdown > self.max_daily_drawdown:
            violations.append(f"Daily drawdown exceeded: {risk_metrics.current_drawdown:.2%} > {self.max_daily_drawdown:.2%}")
        
        if risk_metrics.max_drawdown > self.max_total_drawdown:
            violations.append(f"Total drawdown exceeded: {risk_metrics.max_drawdown:.2%} > {self.max_total_drawdown:.2%}")
        
        # Concentration risk
        if risk_metrics.concentration_risk > self.max_position_size:
            violations.append(f"Position concentration exceeded: {risk_metrics.concentration_risk:.2%} > {self.max_position_size:.2%}")
        
        # Liquidity risk
        if risk_metrics.liquidity_risk > 0.8:
            violations.append(f"High liquidity risk detected: {risk_metrics.liquidity_risk:.2f}")
        
        # Trading frequency
        if self.trades_today >= self.max_daily_trades:
            violations.append(f"Daily trade limit exceeded: {self.trades_today} >= {self.max_daily_trades}")
        
        # Overall risk level
        if risk_metrics.risk_level == RiskLevel.EXTREME:
            violations.append("Extreme risk level detected - immediate action required")
        
        within_limits = len(violations) == 0
        
        return within_limits, violations
    
    def should_halt_trading(self, risk_metrics: RiskMetrics) -> bool:
        """
        Determine if trading should be halted due to risk conditions
        """
        
        # Emergency stop conditions
        halt_conditions = [
            risk_metrics.current_drawdown > self.max_daily_drawdown,
            risk_metrics.max_drawdown > self.max_total_drawdown,
            risk_metrics.portfolio_var_99 > self.max_portfolio_var_99 * 1.5,
            risk_metrics.risk_level == RiskLevel.EXTREME,
            self.trades_today >= self.max_daily_trades,
            risk_metrics.liquidity_risk > 0.9
        ]
        
        return any(halt_conditions)
    
    def _calculate_kelly_fraction(self, market_data: Dict[str, float], 
                                volatility: float) -> float:
        """
        Calculate Kelly fraction based on current market conditions
        """
        
        # Get market indicators
        spread_bps = market_data.get('spread_bps', 10)
        volume_ratio = market_data.get('volume_ratio', 1.0)
        
        # Base Kelly calculation (simplified)
        estimated_win_rate = 0.55  # Conservative estimate
        estimated_win_amount = 0.02  # 2% average win
        estimated_loss_amount = 0.015  # 1.5% average loss
        
        kelly = (estimated_win_rate * estimated_win_amount - 
                (1 - estimated_win_rate) * estimated_loss_amount) / estimated_win_amount
        
        # Adjust for market conditions
        if spread_bps > 15:  # High spreads reduce edge
            kelly *= 0.5
        
        if volume_ratio < 1.0:  # Low volume increases risk
            kelly *= 0.7
        
        if volatility > 0.3:  # High volatility requires smaller positions
            kelly *= 0.6
        
        # Apply safety factor and limits
        kelly *= self.kelly_safety_factor
        return max(self.min_kelly_fraction, min(kelly, self.max_kelly_fraction))
    
    def _assess_liquidity_risk(self, market_data: Dict[str, float]) -> float:
        """
        Assess current market liquidity risk (0 = low risk, 1 = high risk)
        """
        
        volume_ratio = market_data.get('volume_ratio', 1.0)
        spread_bps = market_data.get('spread_bps', 10)
        
        # Low volume increases liquidity risk
        volume_risk = max(0, (1.5 - volume_ratio) / 1.5) if volume_ratio < 1.5 else 0
        
        # High spreads increase liquidity risk  
        spread_risk = max(0, (spread_bps - 10) / 40) if spread_bps > 10 else 0
        
        # Combined liquidity risk score
        liquidity_risk = min(volume_risk + spread_risk, 1.0)
        
        return liquidity_risk
    
    def _determine_risk_level(self, var_95: float, var_99: float, 
                            current_drawdown: float, volatility: float,
                            concentration_risk: float, liquidity_risk: float) -> RiskLevel:
        """
        Determine overall risk level based on multiple factors
        """
        
        risk_score = 0
        
        # VaR contribution
        if -var_95 > self.max_portfolio_var_95 * 0.8:
            risk_score += 2
        elif -var_95 > self.max_portfolio_var_95 * 0.5:
            risk_score += 1
        
        # Drawdown contribution  
        if current_drawdown > self.max_daily_drawdown * 0.8:
            risk_score += 2
        elif current_drawdown > self.max_daily_drawdown * 0.5:
            risk_score += 1
        
        # Volatility contribution
        if volatility > 0.4:
            risk_score += 2
        elif volatility > 0.25:
            risk_score += 1
        
        # Concentration contribution
        if concentration_risk > 0.4:
            risk_score += 1
        
        # Liquidity contribution
        if liquidity_risk > 0.7:
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 6:
            return RiskLevel.EXTREME
        elif risk_score >= 4:
            return RiskLevel.HIGH
        elif risk_score >= 2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def record_trade(self, trade_details: Dict):
        """Record trade for risk monitoring"""
        
        self.trades_today += 1
        self.position_history.append(trade_details)
        
        # Keep position history manageable
        if len(self.position_history) > 100:
            self.position_history = self.position_history[-50:]
    
    def reset_daily_counters(self):
        """Reset daily risk counters"""
        
        self.trades_today = 0
        self.daily_start_value = self.last_portfolio_value
    
    def get_risk_report(self, risk_metrics: RiskMetrics) -> str:
        """Generate formatted risk report"""
        
        report = f"""
🛡️ QUANTUM RISK REPORT
{'='*50}
📊 Portfolio VaR (95%): {risk_metrics.portfolio_var_95:.2%}
📊 Portfolio VaR (99%): {risk_metrics.portfolio_var_99:.2%}
📉 Current Drawdown: {risk_metrics.current_drawdown:.2%}
📉 Maximum Drawdown: {risk_metrics.max_drawdown:.2%}
📊 Annual Volatility: {risk_metrics.volatility_annual:.1%}
⚡ Sharpe Ratio: {risk_metrics.sharpe_ratio:.2f}
🎯 Optimal Kelly: {risk_metrics.kelly_fraction:.1%}
🎛️ Risk Level: {risk_metrics.risk_level.value.upper()}
🎯 Concentration Risk: {risk_metrics.concentration_risk:.1%}
💧 Liquidity Risk: {risk_metrics.liquidity_risk:.1%}
🔄 Trades Today: {self.trades_today}/{self.max_daily_trades}
{'='*50}
        """
        
        return report