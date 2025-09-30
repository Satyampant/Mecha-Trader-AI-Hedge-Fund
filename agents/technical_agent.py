"""
Technical analysis agent
Analyzes price patterns and technical indicators to generate trading signals
"""

from typing import List
from agents.base_agent import BaseAgent
from models.shared_models import StockData, AgentSignal
from utils.helpers import calculate_sma, calculate_rsi
from utils.prompts import PromptTemplates


class TechnicalAgent(BaseAgent):
    """Agent specializing in technical analysis"""
    
    def __init__(self):
        super().__init__(
            name="TechnicalAgent",
            role="technical analysis specialist focusing on price patterns and indicators"
        )
    
    def analyze(
        self, 
        symbol: str, 
        price_history: List[StockData]
    ) -> AgentSignal:
        """
        Analyze technical indicators and generate signal
        
        Args:
            symbol: Stock ticker
            price_history: List of historical StockData (at least 200 days for SMA-200)
            
        Returns:
            AgentSignal with technical analysis recommendation
        """
        # Check if we have enough data
        if len(price_history) < 50:
            return self._create_signal(
                symbol=symbol,
                signal_str="HOLD",
                confidence=0.5,
                reasoning="Insufficient historical data for technical analysis (need at least 50 days)",
                metadata={'data_points': len(price_history)}
            )
        
        # Extract closing prices
        closes = [p.close for p in price_history]
        current_price = closes[-1]
        
        # Calculate technical indicators
        sma_50 = calculate_sma(closes, 50)
        sma_200 = calculate_sma(closes, 200) if len(closes) >= 200 else None
        rsi = calculate_rsi(closes, 14)
        
        # Format price history for LLM (last 10 days)
        recent_prices = "\n".join([
            f"{p.date.strftime('%Y-%m-%d')}: ${p.close:.2f}"
            for p in price_history[-10:]
        ])
        
        # Build prompt
        prompt = PromptTemplates.TECHNICAL_ANALYSIS.format(
            symbol=symbol,
            current_price=f"{current_price:.2f}",
            sma_50=f"{sma_50:.2f}" if sma_50 else "N/A",
            sma_200=f"{sma_200:.2f}" if sma_200 else "N/A",
            rsi=f"{rsi:.2f}",
            price_history=recent_prices
        )
        
        # Get LLM analysis
        response = self.call_llm(prompt)
        parsed = self.parse_llm_response(response)
        
        # Create signal with metadata
        return self._create_signal(
            symbol=symbol,
            signal_str=parsed.get('signal', 'HOLD'),
            confidence=float(parsed.get('confidence', 0.5)),
            reasoning=parsed.get('reasoning', 'Technical analysis complete'),
            metadata={
                'sma_50': sma_50,
                'sma_200': sma_200,
                'rsi': rsi,
                'current_price': current_price,
                'data_points': len(price_history)
            }
        )