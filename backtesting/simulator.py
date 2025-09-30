"""
Trading simulator
Simulates trade execution and portfolio management
"""

from typing import Dict, List
from models.shared_models import TradeOrder, PortfolioState, SignalType
from datetime import datetime


class TradingSimulator:
    """Simulates trade execution and portfolio management"""
    
    def __init__(self, initial_capital: float):
        """
        Initialize simulator
        
        Args:
            initial_capital: Starting cash amount
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, int] = {}  # {symbol: shares}
        self.trade_history: List[TradeOrder] = []
        self.portfolio_history: List[PortfolioState] = []
    
    def execute_trades(
        self,
        trades: List[TradeOrder],
        date: datetime
    ):
        """
        Execute list of trade orders
        
        Args:
            trades: List of TradeOrder objects
            date: Current simulation date
        """
        for trade in trades:
            if trade.action == SignalType.BUY:
                self._execute_buy(trade)
            elif trade.action == SignalType.SELL:
                self._execute_sell(trade)
            
            # Always add to history, even if skipped
            self.trade_history.append(trade)
    
    def _execute_buy(self, trade: TradeOrder):
        """
        Execute buy order
        
        Args:
            trade: TradeOrder with BUY action
        """
        cost = trade.quantity * trade.price
        
        if cost <= self.cash:
            self.cash -= cost
            self.positions[trade.symbol] = self.positions.get(trade.symbol, 0) + trade.quantity
            print(f"    ✓ BUY  {trade.quantity:>4} {trade.symbol} @ ${trade.price:.2f} (Total: ${cost:,.2f})")
        else:
            print(f"    ✗ SKIP BUY {trade.symbol}: Insufficient cash (need ${cost:,.2f}, have ${self.cash:,.2f})")
    
    def _execute_sell(self, trade: TradeOrder):
        """
        Execute sell order
        
        Args:
            trade: TradeOrder with SELL action
        """
        current_position = self.positions.get(trade.symbol, 0)
        
        if current_position >= trade.quantity:
            proceeds = trade.quantity * trade.price
            self.cash += proceeds
            self.positions[trade.symbol] -= trade.quantity
            
            # Remove symbol from positions if we sold everything
            if self.positions[trade.symbol] == 0:
                del self.positions[trade.symbol]
            
            print(f"    ✓ SELL {trade.quantity:>4} {trade.symbol} @ ${trade.price:.2f} (Total: ${proceeds:,.2f})")
        else:
            print(f"    ✗ SKIP SELL {trade.symbol}: Insufficient shares (need {trade.quantity}, have {current_position})")
    
    def update_portfolio_value(
        self,
        current_prices: Dict[str, float],
        date: datetime
    ):
        """
        Update portfolio value and record state
        
        Args:
            current_prices: {symbol: current_price}
            date: Current date
        """
        # Calculate total value of positions
        positions_value = sum(
            qty * current_prices.get(symbol, 0)
            for symbol, qty in self.positions.items()
        )
        
        total_value = self.cash + positions_value
        
        # Create and store portfolio state
        state = PortfolioState(
            cash=self.cash,
            positions=self.positions.copy(),
            total_value=total_value,
            date=date
        )
        
        self.portfolio_history.append(state)
    
    def get_current_state(self, date: datetime) -> PortfolioState:
        """
        Get current portfolio state
        
        Args:
            date: Current date
            
        Returns:
            PortfolioState object
        """
        # Return most recent state if available
        if self.portfolio_history:
            return self.portfolio_history[-1]
        
        # Otherwise create new state
        return PortfolioState(
            cash=self.cash,
            positions=self.positions.copy(),
            total_value=self.cash,
            date=date
        )
    
    def get_portfolio_values(self) -> List[float]:
        """
        Get time series of portfolio values
        
        Returns:
            List of portfolio values over time
        """
        return [state.total_value for state in self.portfolio_history]
    
    def get_dates(self) -> List[datetime]:
        """
        Get time series of dates
        
        Returns:
            List of dates corresponding to portfolio history
        """
        return [state.date for state in self.portfolio_history]
    
    def get_trade_count(self) -> int:
        """
        Get total number of executed trades
        
        Returns:
            Count of trades in history
        """
        return len(self.trade_history)
    
    def get_trade_pnls(self) -> List[float]:
        """
        Calculate P&L for each trade pair (buy-sell)
        
        Returns:
            List of trade P&Ls
        """
        # This is a simplified version for PoC
        # In production, would track individual trade lots
        pnls = []
        
        # Group trades by symbol
        symbol_trades = {}
        for trade in self.trade_history:
            if trade.symbol not in symbol_trades:
                symbol_trades[trade.symbol] = []
            symbol_trades[trade.symbol].append(trade)
        
        # Calculate P&L for each symbol
        for symbol, trades in symbol_trades.items():
            buys = [t for t in trades if t.action == SignalType.BUY]
            sells = [t for t in trades if t.action == SignalType.SELL]
            
            # Simplified P&L calculation
            for sell in sells:
                if buys:
                    buy = buys[0]  # FIFO
                    pnl = (sell.price - buy.price) * sell.quantity
                    pnls.append(pnl)
        
        return pnls
    
    def get_summary(self) -> Dict:
        """
        Get summary statistics of simulation
        
        Returns:
            Dictionary with simulation statistics
        """
        return {
            "initial_capital": self.initial_capital,
            "final_cash": self.cash,
            "positions": self.positions.copy(),
            "num_trades": self.get_trade_count(),
            "num_portfolio_snapshots": len(self.portfolio_history)
        }