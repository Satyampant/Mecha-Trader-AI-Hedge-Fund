
from datetime import datetime
from typing import List


def calculate_sma(prices: List[float], window: int) -> float:
    """
    Calculate Simple Moving Average
    
    Args:
        prices: List of price values
        window: Number of periods to average
        
    Returns:
        SMA value or None if insufficient data
    """
    if len(prices) < window:
        return None
    
    recent_prices = prices[-window:]
    return sum(recent_prices) / window


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """
    Calculate Relative Strength Index
    
    Args:
        prices: List of price values
        period: RSI period (default 14)
        
    Returns:
        RSI value between 0 and 100
    """
    if len(prices) < period + 1:
        return 50.0  # Neutral RSI
    
    # Calculate price changes
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    # Separate gains and losses
    recent_deltas = deltas[-period:]
    gains = [d if d > 0 else 0 for d in recent_deltas]
    losses = [-d if d < 0 else 0 for d in recent_deltas]
    
    # Calculate average gain and loss
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    # Handle edge case where there are no losses
    if avg_loss == 0:
        return 100.0
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def format_currency(amount: float) -> str:
    """
    Format number as currency string
    
    Args:
        amount: Dollar amount
        
    Returns:
        Formatted string (e.g., "$1,234.56")
    """
    return f"${amount:,.2f}"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values
    
    Args:
        old_value: Starting value
        new_value: Ending value
        
    Returns:
        Percentage change
    """
    if old_value == 0:
        return 0.0
    
    return ((new_value - old_value) / old_value) * 100


def parse_date(date_str: str) -> datetime:
    """
    Parse date string to datetime object
    
    Args:
        date_str: Date in YYYY-MM-DD format
        
    Returns:
        datetime object
    """
    return datetime.strptime(date_str, "%Y-%m-%d")


def validate_price_data(open_price: float, high: float, low: float, close: float) -> bool:
    """
    Validate that price data is logically consistent
    
    Args:
        open_price: Opening price
        high: High price
        low: Low price
        close: Closing price
        
    Returns:
        True if valid, False otherwise
    """
    # High must be >= all other prices
    if high < open_price or high < close or high < low:
        return False
    
    # Low must be <= all other prices
    if low > open_price or low > close or low > high:
        return False
    
    # All prices must be positive
    if any(p <= 0 for p in [open_price, high, low, close]):
        return False
    
    return True


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."