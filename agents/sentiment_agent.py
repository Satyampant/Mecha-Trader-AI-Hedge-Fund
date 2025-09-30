
from typing import List
from agents.base_agent import BaseAgent
from models.shared_models import NewsHeadline, AgentSignal
from utils.prompts import PromptTemplates


class SentimentAgent(BaseAgent):
    """Agent specializing in news sentiment analysis"""
    
    def __init__(self):
        super().__init__(
            name="SentimentAgent",
            role="market sentiment analyst focusing on news and public perception"
        )
    
    def analyze(
        self, 
        symbol: str, 
        headlines: List[NewsHeadline],
        current_date: str
    ) -> AgentSignal:
        """
        Analyze news sentiment and generate signal
        
        Args:
            symbol: Stock ticker
            headlines: List of recent NewsHeadline objects
            current_date: Analysis date (YYYY-MM-DD)
            
        Returns:
            AgentSignal with sentiment analysis recommendation
        """
        # Handle case with no headlines
        if not headlines:
            return self._create_signal(
                symbol=symbol,
                signal_str="HOLD",
                confidence=0.5,
                reasoning="No news headlines available for sentiment analysis",
                metadata={'num_headlines': 0}
            )
        
        # Format headlines for LLM
        formatted_headlines = "\n".join([
            f"- [{h.date.strftime('%Y-%m-%d')}] {h.headline} ({h.source})"
            for h in headlines
        ])
        
        # Build prompt
        prompt = PromptTemplates.SENTIMENT_ANALYSIS.format(
            symbol=symbol,
            date=current_date,
            headlines=formatted_headlines
        )
        
        # Get LLM analysis
        response = self.call_llm(prompt)
        parsed = self.parse_llm_response(response)
        
        # Extract unique sources
        sources = list(set(h.source for h in headlines))
        
        # Create signal
        return self._create_signal(
            symbol=symbol,
            signal_str=parsed.get('signal', 'HOLD'),
            confidence=float(parsed.get('confidence', 0.5)),
            reasoning=parsed.get('reasoning', 'Sentiment analysis complete'),
            metadata={
                'num_headlines': len(headlines),
                'sources': sources,
                'date_range': f"{headlines[-1].date.strftime('%Y-%m-%d')} to {headlines[0].date.strftime('%Y-%m-%d')}"
            }
        )