"""
Performance metrics calculator
Calculates comprehensive backtest performance statistics
"""

import numpy as np
from typing import List
from models.shared_models import PerformanceReport
from config.settings import Config


class PerformanceMetrics:
    """Calculates portfolio performance statistics"""
    
    @staticmethod
    def calculate_returns(portfolio_values: List[float]) -> np.ndarray:
        """
        Calculate daily returns
        
        Args:
            portfolio_values: Time series of portfolio values
            
        Returns:
            Array of daily returns
        """
        if len(portfolio_values) < 2:
            return np.array([])
        
        values = np.array(portfolio_values)
        returns = np.diff(values) / values[:-1]
        
        return returns
    
    @staticmethod
    def sharpe_ratio(
        returns: np.ndarray,
        risk_free_rate: float = None,
        periods_per_year: int = None
    ) -> float:
        """
        Calculate Sharpe Ratio
        
        Args:
            returns: Array of daily returns
            risk_free_rate: Annual risk-free rate (default from Config)
            periods_per_year: Trading days per year (default from Config)
            
        Returns:
            Annualized Sharpe ratio
        """
        if risk_free_rate is None:
            risk_free_rate = Config.RISK_FREE_RATE
        
        if periods_per_year is None:
            periods_per_year = Config.TRADING_DAYS_PER_YEAR
        
        if len(returns) == 0:
            return 0.0
        
        # Calculate daily risk-free rate
        daily_rf_rate = risk_free_rate / periods_per_year
        
        # Calculate excess returns
        excess_returns = returns - daily_rf_rate
        
        # Handle zero standard deviation
        if np.std(excess_returns) == 0:
            return 0.0
        
        # Calculate Sharpe ratio
        sharpe = np.mean(excess_returns) / np.std(excess_returns)
        
        # Annualize
        annualized_sharpe = sharpe * np.sqrt(periods_per_year)
        
        return annualized_sharpe
    
    @staticmethod
    def sortino_ratio(
        returns: np.ndarray,
        risk_free_rate: float = None,
        periods_per_year: int = None
    ) -> float:
        """
        Calculate Sortino Ratio (focuses on downside deviation)
        
        Args:
            returns: Array of daily returns
            risk_free_rate: Annual risk-free rate (default from Config)
            periods_per_year: Trading days per year (default from Config)
            
        Returns:
            Annualized Sortino ratio
        """
        if risk_free_rate is None:
            risk_free_rate = Config.RISK_FREE_RATE
        
        if periods_per_year is None:
            periods_per_year = Config.TRADING_DAYS_PER_YEAR
        
        if len(returns) == 0:
            return 0.0
        
        # Calculate daily risk-free rate
        daily_rf_rate = risk_free_rate / periods_per_year
        
        # Calculate excess returns
        excess_returns = returns - daily_rf_rate
        
        # Only consider negative returns for downside deviation
        downside_returns = excess_returns[excess_returns < 0]
        
        # Handle case with no downside or zero downside deviation
        if len(downside_returns) == 0 or np.std(downside_returns) == 0:
            return 0.0
        
        # Calculate Sortino ratio
        sortino = np.mean(excess_returns) / np.std(downside_returns)
        
        # Annualize
        annualized_sortino = sortino * np.sqrt(periods_per_year)
        
        return annualized_sortino
    
    @staticmethod
    def max_drawdown(portfolio_values: List[float]) -> float:
        """
        Calculate maximum drawdown
        
        Args:
            portfolio_values: Time series of portfolio values
            
        Returns:
            Maximum drawdown as positive percentage
        """
        if len(portfolio_values) == 0:
            return 0.0
        
        values = np.array(portfolio_values)
        
        # Calculate running maximum
        running_max = np.maximum.accumulate(values)
        
        # Calculate drawdown at each point
        drawdowns = (values - running_max) / running_max
        
        # Get maximum drawdown (most negative value)
        max_dd = np.min(drawdowns)
        
        # Return as positive percentage
        return abs(max_dd * 100)
    
    @staticmethod
    def calculate_winning_trades(trade_pnls: List[float]) -> tuple:
        """
        Calculate winning vs losing trades
        
        Args:
            trade_pnls: List of trade P&Ls
            
        Returns:
            Tuple of (winning_count, losing_count)
        """
        winning = sum(1 for pnl in trade_pnls if pnl > 0)
        losing = sum(1 for pnl in trade_pnls if pnl < 0)
        
        return (winning, losing)
    
    @staticmethod
    def generate_report(
        initial_capital: float,
        final_value: float,
        portfolio_values: List[float],
        num_trades: int,
        trade_pnls: List[float] = None
    ) -> PerformanceReport:
        """
        Generate comprehensive performance report
        
        Args:
            initial_capital: Starting capital
            final_value: Final portfolio value
            portfolio_values: Time series of portfolio values
            num_trades: Total number of trades executed
            trade_pnls: Optional list of trade P&Ls
            
        Returns:
            PerformanceReport object with all metrics
        """
        # Calculate returns
        returns = PerformanceMetrics.calculate_returns(portfolio_values)
        
        # Calculate total return percentage
        if initial_capital > 0:
            total_return = ((final_value - initial_capital) / initial_capital) * 100
        else:
            total_return = 0.0
        
        # Calculate risk-adjusted metrics
        sharpe = PerformanceMetrics.sharpe_ratio(returns)
        sortino = PerformanceMetrics.sortino_ratio(returns)
        
        # Calculate drawdown
        max_dd = PerformanceMetrics.max_drawdown(portfolio_values)
        
        # Calculate winning/losing trades
        winning_trades = 0
        losing_trades = 0
        if trade_pnls:
            winning_trades, losing_trades = PerformanceMetrics.calculate_winning_trades(trade_pnls)
        
        return PerformanceReport(
            initial_capital=initial_capital,
            final_value=final_value,
            total_return=total_return,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            max_drawdown=max_dd,
            num_trades=num_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades
        )