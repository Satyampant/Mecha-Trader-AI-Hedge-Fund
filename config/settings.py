
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    
    # ==================== API Configuration ====================
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    FINANCIAL_DATASETS_API_KEY: str = os.getenv("FINANCIAL_DATASETS_API_KEY", "")
    
    # ==================== LLM Configuration ====================
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.3
    MAX_TOKENS: int = 1024
    
    # ==================== Trading Configuration ====================
    SYMBOLS: List[str] = ["AAPL", "MSFT", "GOOGL"]
    FREE_TICKERS = {"AAPL", "GOOGL", "MSFT", "NVDA", "TSLA"}
    INITIAL_CAPITAL: float = 100000.0
    
    # ==================== Backtest Configuration ====================
    START_DATE: str = "2025-08-01"
    END_DATE: str = "2025-09-01"
    
    # ==================== Risk Management Parameters ====================
    MAX_POSITION_SIZE: float = 0.3  # 30% of portfolio per stock
    CASH_RESERVE: float = 0.1       # Keeping 10% in cash
    
    # ==================== Performance Metrics Configuration ====================
    RISK_FREE_RATE: float = 0.02    # 2% annual risk-free rate
    TRADING_DAYS_PER_YEAR: int = 252
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration settings
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If any configuration is invalid
        """
        if not cls.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not set in environment. "
                "Please add it to your .env file."
            )
        
        if cls.INITIAL_CAPITAL <= 0:
            raise ValueError(
                f"INITIAL_CAPITAL must be positive, got {cls.INITIAL_CAPITAL}"
            )
        
        if not cls.SYMBOLS or len(cls.SYMBOLS) == 0:
            raise ValueError("SYMBOLS list cannot be empty")
        
        if not (0 < cls.MAX_POSITION_SIZE <= 1):
            raise ValueError(
                f"MAX_POSITION_SIZE must be between 0 and 1, got {cls.MAX_POSITION_SIZE}"
            )
        
        if not (0 <= cls.CASH_RESERVE < 1):
            raise ValueError(
                f"CASH_RESERVE must be between 0 and 1, got {cls.CASH_RESERVE}"
            )
        
        if cls.LLM_TEMPERATURE < 0 or cls.LLM_TEMPERATURE > 2:
            raise ValueError(
                f"LLM_TEMPERATURE must be between 0 and 2, got {cls.LLM_TEMPERATURE}"
            )
        
        return True
    
    @classmethod
    def display_config(cls):
        """Display current configuration (for debugging)"""
        print("\n" + "="*60)
        print("CONFIGURATION SETTINGS")
        print("="*60)
        print(f"LLM Model: {cls.GROQ_MODEL}")
        print(f"Temperature: {cls.LLM_TEMPERATURE}")
        print(f"Trading Symbols: {', '.join(cls.SYMBOLS)}")
        print(f"Initial Capital: ${cls.INITIAL_CAPITAL:,.2f}")
        print(f"Backtest Period: {cls.START_DATE} to {cls.END_DATE}")
        print(f"Max Position Size: {cls.MAX_POSITION_SIZE*100:.0f}%")
        print(f"Cash Reserve: {cls.CASH_RESERVE*100:.0f}%")
        print("="*60 + "\n")