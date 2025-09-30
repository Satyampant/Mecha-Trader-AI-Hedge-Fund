
class PromptTemplates:
    """Collection of prompt templates for different agent types"""
    
    TECHNICAL_ANALYSIS = """You are a technical analysis expert. Analyze the following stock data and provide a trading signal.

Stock: {symbol}
Current Price: ${current_price}
50-day SMA: ${sma_50}
200-day SMA: ${sma_200}
RSI (14-day): {rsi}

Price History (last 10 days):
{price_history}

Based on this technical data, provide:
1. Signal: BUY, SELL, or HOLD
2. Confidence: 0.0 to 1.0
3. Reasoning: 2-3 sentence explanation

Format your response EXACTLY as:
SIGNAL: [BUY/SELL/HOLD]
CONFIDENCE: [0.0-1.0]
REASONING: [Your explanation]
"""

    SENTIMENT_ANALYSIS = """You are a market sentiment analyst. Analyze the following news headlines and provide a trading signal.

Stock: {symbol}
Date: {date}

Recent Headlines:
{headlines}

Based on the sentiment of these headlines, provide:
1. Signal: BUY, SELL, or HOLD
2. Confidence: 0.0 to 1.0
3. Reasoning: 2-3 sentence explanation

Format your response EXACTLY as:
SIGNAL: [BUY/SELL/HOLD]
CONFIDENCE: [0.0-1.0]
REASONING: [Your explanation]
"""

    FUNDAMENTAL_ANALYSIS = """You are a fundamental analysis expert. Analyze the following financial metrics and provide a trading signal.

Stock: {symbol}
Current Price: ${current_price}

Financial Metrics:
- P/E Ratio: {pe_ratio}
- Market Cap: ${market_cap}
- Revenue Growth: {revenue_growth}%
- Debt-to-Equity: {debt_to_equity}

Industry Average P/E: {industry_pe}

Based on these fundamentals, provide:
1. Signal: BUY, SELL, or HOLD
2. Confidence: 0.0 to 1.0
3. Reasoning: 2-3 sentence explanation

Format your response EXACTLY as:
SIGNAL: [BUY/SELL/HOLD]
CONFIDENCE: [0.0-1.0]
REASONING: [Your explanation]
"""

    PORTFOLIO_DECISION = """You are a portfolio manager. Based on signals from multiple analysts, make final trading decisions.

Current Portfolio:
- Cash: ${cash}
- Positions: {positions}
- Total Value: ${total_value}

Analyst Signals for {symbol}:
{analyst_signals}

Current Price: ${current_price}

Risk Parameters:
- Max position size: {max_position}% of portfolio
- Cash reserve requirement: {cash_reserve}%

Decide:
1. Action: BUY, SELL, or HOLD
2. Quantity: Number of shares (if applicable, 0 for HOLD)
3. Reasoning: Why this decision?

Format your response EXACTLY as:
ACTION: [BUY/SELL/HOLD]
QUANTITY: [number or 0]
REASONING: [Your explanation]
"""