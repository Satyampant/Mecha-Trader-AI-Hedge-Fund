"""
Portfolio manager agent
Makes final trading decisions based on analyst signals and risk management
"""

from typing import List
from agents.base_agent import BaseAgent
from models.shared_models import AgentSignal, TradeOrder, PortfolioState, SignalType
from utils.prompts import PromptTemplates
from config.settings import Config
from datetime import datetime


class PortfolioManager(BaseAgent):
    """Agent responsible for final trading decisions and risk management"""
    
    def __init__(self):
        super().__init__(
            name="PortfolioManager",
            role="portfolio manager responsible for trade execution and risk management"
        )
    
    def analyze(self, **kwargs) -> AgentSignal:
        """
        Abstract method implementation (not used by PortfolioManager)
        PortfolioManager uses decide_trades() instead
        
        This method exists only to satisfy the BaseAgent abstract class requirement
        """
        raise NotImplementedError(
            "PortfolioManager uses decide_trades() method instead of analyze()"
        )
    
    def decide_trades(
        self,
        symbol: str,
        analyst_signals: List[AgentSignal],
        portfolio_state: PortfolioState,
        current_price: float
    ) -> List[TradeOrder]:
        """
        Aggregate analyst signals and make trading decision
        
        Args:
            symbol: Stock ticker
            analyst_signals: List of signals from technical, sentiment, fundamental agents
            portfolio_state: Current portfolio state (cash, positions, total_value)
            current_price: Current stock price
            
        Returns:
            List of TradeOrder objects (empty if no action)
        """
        # Format analyst signals for LLM
        signals_text = "\n".join([
            f"- {sig.agent_name}: {sig.signal.value} (confidence: {sig.confidence:.2f})\n  Reasoning: {sig.reasoning}"
            for sig in analyst_signals
        ])
        
        # Format portfolio positions
        if portfolio_state.positions:
            positions_text = ", ".join([
                f"{sym}: {qty} shares"
                for sym, qty in portfolio_state.positions.items()
            ])
        else:
            positions_text = "No positions"
        
        # Build prompt
        prompt = PromptTemplates.PORTFOLIO_DECISION.format(
            cash=f"{portfolio_state.cash:.2f}",
            positions=positions_text,
            total_value=f"{portfolio_state.total_value:.2f}",
            symbol=symbol,
            analyst_signals=signals_text,
            current_price=f"{current_price:.2f}",
            max_position=Config.MAX_POSITION_SIZE * 100,
            cash_reserve=Config.CASH_RESERVE * 100
        )
        
        # Get LLM decision
        response = self.call_llm(prompt)
        parsed = self.parse_llm_response(response)
        
        # Extract decision components
        action = parsed.get('action', 'HOLD').upper()
        quantity_str = parsed.get('quantity', '0')
        reasoning = parsed.get('reasoning', 'Portfolio decision made')
        
        # Parse quantity safely
        try:
            quantity = int(float(quantity_str))
        except (ValueError, TypeError):
            quantity = 0
        
        # Validate and execute decision
        trades = []
        
        if action == "BUY" and quantity > 0:
            # Validate buy order
            validated_quantity = self._validate_buy_order(
                symbol=symbol,
                quantity=quantity,
                price=current_price,
                portfolio_state=portfolio_state
            )
            
            if validated_quantity > 0:
                trades.append(TradeOrder(
                    symbol=symbol,
                    action=SignalType.BUY,
                    quantity=validated_quantity,
                    price=current_price,
                    timestamp=datetime.now(),
                    reasoning=reasoning
                ))
        
        elif action == "SELL" and quantity > 0:
            # Validate sell order
            validated_quantity = self._validate_sell_order(
                symbol=symbol,
                quantity=quantity,
                portfolio_state=portfolio_state
            )
            
            if validated_quantity > 0:
                trades.append(TradeOrder(
                    symbol=symbol,
                    action=SignalType.SELL,
                    quantity=validated_quantity,
                    price=current_price,
                    timestamp=datetime.now(),
                    reasoning=reasoning
                ))
        
        return trades
    
    def _validate_buy_order(
        self,
        symbol: str,
        quantity: int,
        price: float,
        portfolio_state: PortfolioState
    ) -> int:
        """
        Validate and adjust buy order based on risk constraints
        
        Args:
            symbol: Stock ticker
            quantity: Desired quantity
            price: Current price
            portfolio_state: Current portfolio state
            
        Returns:
            Validated quantity (may be reduced or 0 if invalid)
        """
        # Calculate cost
        cost = quantity * price
        
        # Check if we have enough cash (with 1% buffer for fees/slippage)
        required_cash = cost * 1.01
        if required_cash > portfolio_state.cash:
            # Reduce quantity to fit available cash
            max_quantity = int((portfolio_state.cash / 1.01) / price)
            if max_quantity <= 0:
                return 0
            quantity = max_quantity
            cost = quantity * price
        
        # Check max position size constraint
        max_position_value = portfolio_state.total_value * Config.MAX_POSITION_SIZE
        current_position_value = portfolio_state.positions.get(symbol, 0) * price
        
        if current_position_value + cost > max_position_value:
            # Reduce quantity to fit max position size
            available_position_value = max_position_value - current_position_value
            if available_position_value <= 0:
                return 0
            max_quantity = int(available_position_value / price)
            quantity = min(quantity, max_quantity)
        
        # Check cash reserve constraint
        min_cash_reserve = portfolio_state.total_value * Config.CASH_RESERVE
        remaining_cash = portfolio_state.cash - (quantity * price * 1.01)
        
        if remaining_cash < min_cash_reserve:
            # Reduce quantity to maintain cash reserve
            available_cash = portfolio_state.cash - min_cash_reserve
            if available_cash <= 0:
                return 0
            max_quantity = int((available_cash / 1.01) / price)
            quantity = min(quantity, max_quantity)
        
        return max(0, quantity)
    
    def _validate_sell_order(
        self,
        symbol: str,
        quantity: int,
        portfolio_state: PortfolioState
    ) -> int:
        """
        Validate sell order based on current positions
        
        Args:
            symbol: Stock ticker
            quantity: Desired quantity
            portfolio_state: Current portfolio state
            
        Returns:
            Validated quantity (may be reduced or 0 if invalid)
        """
        current_position = portfolio_state.positions.get(symbol, 0)
        
        # Can't sell more than we own
        if current_position == 0:
            return 0
        
        # Adjust quantity if we don't have enough shares
        return min(quantity, current_position)
    
    def calculate_position_size(
        self,
        portfolio_value: float,
        current_price: float,
        max_position_pct: float = None
    ) -> int:
        """
        Calculate recommended position size
        
        Args:
            portfolio_value: Total portfolio value
            current_price: Stock price
            max_position_pct: Max position size as percentage (default from Config)
            
        Returns:
            Number of shares to buy
        """
        if max_position_pct is None:
            max_position_pct = Config.MAX_POSITION_SIZE
        
        max_investment = portfolio_value * max_position_pct
        shares = int(max_investment / current_price)
        
        return shares