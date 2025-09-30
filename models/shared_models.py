"""
Shared data models used across all modules
Defines core data structures for the entire system
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class SignalType(Enum):
    """Trading signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class AgentSignal:
    """
    Output from any analyst agent
    Represents a trading recommendation with confidence and reasoning
    """
    agent_name: str              # e.g., "TechnicalAgent"
    symbol: str                  # e.g., "AAPL"
    signal: SignalType           # BUY/SELL/HOLD
    confidence: float            # 0.0 to 1.0
    reasoning: str               # LLM-generated explanation
    timestamp: datetime
    metadata: Dict = field(default_factory=dict)  # Agent-specific data
    
    def __post_init__(self):
        """Validate signal data after initialization"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        
        if not isinstance(self.signal, SignalType):
            raise TypeError(f"Signal must be SignalType enum, got {type(self.signal)}")


@dataclass
class StockData:
    """
    Historical price data for a single trading day
    Used for technical analysis and portfolio valuation
    """
    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: float
    
    def __post_init__(self):
        """Validate price data"""
        if self.high < self.low:
            raise ValueError(f"High price {self.high} cannot be less than low price {self.low}")
        
        if self.volume < 0:
            raise ValueError(f"Volume cannot be negative, got {self.volume}")


@dataclass
class FinancialMetrics:
    """
    Fundamental data snapshot for a company
    Used for fundamental analysis
    """
    symbol: str
    date: datetime
    pe_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    revenue_growth: Optional[float] = None  # Percentage
    debt_to_equity: Optional[float] = None
    
    def is_complete(self) -> bool:
        """Check if all metrics are available"""
        return all([
            self.pe_ratio is not None,
            self.market_cap is not None,
            self.revenue_growth is not None,
            self.debt_to_equity is not None
        ])


@dataclass
class NewsHeadline:
    """
    News article metadata for sentiment analysis
    """
    symbol: str
    date: datetime
    headline: str
    source: str
    url: Optional[str] = None


@dataclass
class TradeOrder:
    """
    Portfolio manager trade decision
    Represents a single buy or sell order
    """
    symbol: str
    action: SignalType           # BUY or SELL (never HOLD)
    quantity: int
    price: float                 # Execution price
    timestamp: datetime
    reasoning: str
    
    def __post_init__(self):
        """Validate trade order"""
        if self.action == SignalType.HOLD:
            raise ValueError("TradeOrder cannot have HOLD action")
        
        if self.quantity <= 0:
            raise ValueError(f"Quantity must be positive, got {self.quantity}")
        
        if self.price <= 0:
            raise ValueError(f"Price must be positive, got {self.price}")
    
    @property
    def total_value(self) -> float:
        """Calculate total value of the trade"""
        return self.quantity * self.price


@dataclass
class PortfolioState:
    """
    Current portfolio snapshot
    Represents the state of the portfolio at a specific point in time
    """
    cash: float
    positions: Dict[str, int]    # {symbol: shares_held}
    total_value: float
    date: datetime
    
    def get_position_value(self, symbol: str, current_price: float) -> float:
        """Calculate value of a specific position"""
        shares = self.positions.get(symbol, 0)
        return shares * current_price
    
    def get_position_weight(self, symbol: str, current_price: float) -> float:
        """Calculate weight of a position in the portfolio"""
        if self.total_value == 0:
            return 0.0
        position_value = self.get_position_value(symbol, current_price)
        return position_value / self.total_value
    
    def copy(self) -> 'PortfolioState':
        """Create a deep copy of the portfolio state"""
        return PortfolioState(
            cash=self.cash,
            positions=self.positions.copy(),
            total_value=self.total_value,
            date=self.date
        )


@dataclass
class PerformanceReport:
    """
    Comprehensive backtest results
    Contains all performance metrics and statistics
    """
    initial_capital: float
    final_value: float
    total_return: float          # Percentage
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float          # Percentage
    num_trades: int
    winning_trades: int
    losing_trades: int
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage"""
        total_trades = self.winning_trades + self.losing_trades
        if total_trades == 0:
            return 0.0
        return (self.winning_trades / total_trades) * 100
    
    @property
    def profit_loss(self) -> float:
        """Calculate absolute profit/loss"""
        return self.final_value - self.initial_capital
    
    def to_dict(self) -> Dict:
        """Convert report to dictionary for serialization"""
        return {
            "initial_capital": self.initial_capital,
            "final_value": self.final_value,
            "total_return": self.total_return,
            "sharpe_ratio": self.sharpe_ratio,
            "sortino_ratio": self.sortino_ratio,
            "max_drawdown": self.max_drawdown,
            "num_trades": self.num_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.win_rate,
            "profit_loss": self.profit_loss
        }