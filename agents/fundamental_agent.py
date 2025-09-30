"""
Fundamental analysis agent
Analyzes financial metrics and company fundamentals
"""

from typing import Optional
from agents.base_agent import BaseAgent
from models.shared_models import FinancialMetrics, AgentSignal
from utils.prompts import PromptTemplates


class FundamentalAgent(BaseAgent):
    """Agent specializing in fundamental analysis"""
    
    def __init__(self):
        super().__init__(
            name="FundamentalAgent",
            role="fundamental analysis specialist focusing on financial metrics and valuation"
        )
        
        # Industry average P/E ratios (mock data for PoC)
        # In production, this would be fetched from a database or API
        self.industry_pe_averages = {
            "AAPL": 25.0,
            "MSFT": 30.0,
            "GOOGL": 22.0,
            "TSLA": 60.0,
            "AMZN": 50.0,
            "default": 20.0
        }
    
    def analyze(
        self, 
        symbol: str, 
        metrics: Optional[FinancialMetrics],
        current_price: float
    ) -> AgentSignal:
        """
        Analyze fundamental metrics and generate signal
        
        Args:
            symbol: Stock ticker
            metrics: FinancialMetrics object (may be None if unavailable)
            current_price: Current stock price
            
        Returns:
            AgentSignal with fundamental analysis recommendation
        """
        # Handle case with no metrics
        if not metrics:
            return self._create_signal(
                symbol=symbol,
                signal_str="HOLD",
                confidence=0.5,
                reasoning="Insufficient fundamental data available for analysis",
                metadata={'data_available': False}
            )
        
        # Get industry average P/E
        industry_pe = self.industry_pe_averages.get(
            symbol, 
            self.industry_pe_averages['default']
        )
        
        # Format metrics for LLM, handling None values
        pe_ratio_str = f"{metrics.pe_ratio:.2f}" if metrics.pe_ratio else "N/A"
        market_cap_str = f"{metrics.market_cap:,.0f}" if metrics.market_cap else "N/A"
        revenue_growth_str = f"{metrics.revenue_growth:.2f}" if metrics.revenue_growth else "N/A"
        debt_to_equity_str = f"{metrics.debt_to_equity:.2f}" if metrics.debt_to_equity else "N/A"
        
        # Build prompt
        prompt = PromptTemplates.FUNDAMENTAL_ANALYSIS.format(
            symbol=symbol,
            current_price=f"{current_price:.2f}",
            pe_ratio=pe_ratio_str,
            market_cap=market_cap_str,
            revenue_growth=revenue_growth_str,
            debt_to_equity=debt_to_equity_str,
            industry_pe=f"{industry_pe:.2f}"
        )
        
        # Get LLM analysis
        response = self.call_llm(prompt)
        parsed = self.parse_llm_response(response)
        
        # Create signal
        return self._create_signal(
            symbol=symbol,
            signal_str=parsed.get('signal', 'HOLD'),
            confidence=float(parsed.get('confidence', 0.5)),
            reasoning=parsed.get('reasoning', 'Fundamental analysis complete'),
            metadata={
                'pe_ratio': metrics.pe_ratio,
                'market_cap': metrics.market_cap,
                'revenue_growth': metrics.revenue_growth,
                'debt_to_equity': metrics.debt_to_equity,
                'industry_pe': industry_pe,
                'data_available': True,
                'is_complete': metrics.is_complete()
            }
        )