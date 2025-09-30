
from abc import ABC, abstractmethod
from typing import Dict
from groq import Groq
from config.settings import Config
from models.shared_models import AgentSignal, SignalType
from datetime import datetime


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents
    Provides LLM calling and response parsing utilities
    """
    
    def __init__(self, name: str, role: str):
        """
        Initialize base agent
        
        Args:
            name: Agent identifier (e.g., "TechnicalAgent")
            role: Agent's role description for LLM system prompt
        """
        self.name = name
        self.role = role
        
        # Initialize Groq client
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
        self.temperature = Config.LLM_TEMPERATURE
    
    def call_llm(self, prompt: str) -> str:
        """
        Call Groq LLM with prompt
        
        Args:
            prompt: Full prompt string
            
        Returns:
            LLM response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are {self.name}, a {self.role}. Provide concise, actionable analysis. Always follow the exact output format requested."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=Config.MAX_TOKENS
            )
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error calling LLM for {self.name}: {e}")
            return "ERROR: SIGNAL: HOLD\nCONFIDENCE: 0.5\nREASONING: Unable to generate response due to API error"
    
    def parse_llm_response(self, response: str) -> Dict[str, str]:
        """
        Parse structured LLM response
        
        Expected format:
        SIGNAL: BUY
        CONFIDENCE: 0.75
        REASONING: [explanation]
        
        Args:
            response: LLM response string
            
        Returns:
            Dict with 'signal', 'confidence', 'reasoning' keys
        """
        lines = response.strip().split('\n')
        parsed = {}
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                parsed[key.strip().lower()] = value.strip()
        
        # Ensure all required fields exist
        if 'signal' not in parsed:
            parsed['signal'] = 'HOLD'
        if 'confidence' not in parsed:
            parsed['confidence'] = '0.5'
        if 'reasoning' not in parsed:
            parsed['reasoning'] = 'No reasoning provided'
        
        return parsed
    
    @abstractmethod
    def analyze(self, **kwargs) -> AgentSignal:
        """
        Abstract method - each agent implements its own analysis logic
        
        Returns:
            AgentSignal with trading recommendation
        """
        pass
    
    def _create_signal(
        self, 
        symbol: str, 
        signal_str: str,
        confidence: float, 
        reasoning: str,
        metadata: Dict = None
    ) -> AgentSignal:
        """
        Helper to create AgentSignal object
        
        Args:
            symbol: Stock ticker
            signal_str: "BUY", "SELL", or "HOLD"
            confidence: 0.0 to 1.0
            reasoning: Explanation text
            metadata: Additional agent-specific data
            
        Returns:
            AgentSignal object
        """
        signal_map = {
            "BUY": SignalType.BUY,
            "SELL": SignalType.SELL,
            "HOLD": SignalType.HOLD
        }
        
        # Normalize signal string
        signal_str_upper = signal_str.upper()
        signal_type = signal_map.get(signal_str_upper, SignalType.HOLD)
        
        # Clamp confidence to valid range
        confidence_clamped = max(0.0, min(1.0, float(confidence)))
        
        return AgentSignal(
            agent_name=self.name,
            symbol=symbol,
            signal=signal_type,
            confidence=confidence_clamped,
            reasoning=reasoning,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )