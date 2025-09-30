"""
Implements standardized interface for fetching market data
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from models.shared_models import StockData, FinancialMetrics, NewsHeadline


class MCPMarketDataConnector:
    """
    MCP-compliant market data provider
    Provides standardized access to stock prices, financial metrics, and news
    """
    
    def __init__(self):
        """Initialize the MCP connector"""
        self.cache: Dict[str, pd.DataFrame] = {}
        self.metrics_cache: Dict[str, FinancialMetrics] = {}
    
    def execute_tool(self, tool_name: str, params: Dict) -> any:
        """
        MCP standard tool execution interface
        
        Args:
            tool_name: Name of the tool to execute
            params: Parameters for the tool
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool name is unknown
        """
        tool_map = {
            "get_stock_prices": self._get_stock_prices,
            "get_financial_metrics": self._get_financial_metrics,
            "get_news_headlines": self._get_news_headlines,
        }
        
        if tool_name not in tool_map:
            raise ValueError(f"Unknown tool: {tool_name}. Available tools: {list(tool_map.keys())}")
        
        return tool_map[tool_name](**params)
    
    def _get_stock_prices(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str
    ) -> List[StockData]:
        """
        Fetch historical price data
        
        Args:
            symbol: Stock ticker (e.g., "AAPL")
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of StockData objects
        """
        cache_key = f"{symbol}_{start_date}_{end_date}"
        
        # Check cache first
        if cache_key not in self.cache:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date)
                
                if df.empty:
                    print(f"Warning: No data available for {symbol} from {start_date} to {end_date}")
                    return []
                
                self.cache[cache_key] = df
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                return []
        
        df = self.cache[cache_key]
        
        # Convert DataFrame to list of StockData objects
        result = []
        for date, row in df.iterrows():
            try:
                result.append(StockData(
                    symbol=symbol,
                    date=date.to_pydatetime(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume']),
                    adj_close=float(row['Close'])
                ))
            except Exception as e:
                print(f"Warning: Skipping data point for {symbol} on {date}: {e}")
                continue
        
        return result
    
    def _get_financial_metrics(
        self, 
        symbol: str, 
        date: str
    ) -> Optional[FinancialMetrics]:
        """
        Fetch fundamental financial metrics
        
        Args:
            symbol: Stock ticker
            date: Date for metrics (YYYY-MM-DD)
            
        Returns:
            FinancialMetrics object or None if unavailable
        """
        # Check cache first
        cache_key = f"{symbol}_{date}"
        if cache_key in self.metrics_cache:
            return self.metrics_cache[cache_key]
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            metrics = FinancialMetrics(
                symbol=symbol,
                date=datetime.strptime(date, "%Y-%m-%d"),
                pe_ratio=info.get('trailingPE'),
                market_cap=info.get('marketCap'),
                revenue_growth=info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else None,
                debt_to_equity=info.get('debtToEquity')
            )
            
            # Cache the result
            self.metrics_cache[cache_key] = metrics
            
            return metrics
        
        except Exception as e:
            print(f"Error fetching financial metrics for {symbol}: {e}")
            return None
    
    def _get_news_headlines(
        self, 
        symbol: str, 
        date: str, 
        days_back: int = 7
    ) -> List[NewsHeadline]:
        """
        Fetch recent news headlines
        
        For PoC, returns mock headlines based on the symbol
        In production, this would integrate with a news API
        
        Args:
            symbol: Stock ticker
            date: Reference date (YYYY-MM-DD)
            days_back: Number of days to look back
            
        Returns:
            List of NewsHeadline objects
        """
        target_date = datetime.strptime(date, "%Y-%m-%d")
        
        # Mock headlines for PoC
        # In production, replace with actual news API integration
        mock_headline_templates = [
            "{symbol} reports quarterly earnings that beat analyst expectations",
            "Wall Street analysts upgrade {symbol} with increased price targets",
            "{symbol} announces strategic partnership to expand market reach",
            "Market volatility impacts tech sector including {symbol}",
            "{symbol} CEO discusses future growth strategy in interview",
            "Institutional investors increase positions in {symbol}",
            "{symbol} faces regulatory scrutiny in European markets",
            "Strong consumer demand drives {symbol} sales growth",
            "{symbol} unveils innovative product lineup for next quarter",
            "Industry analysts remain bullish on {symbol} long-term prospects"
        ]
        
        # Select 3 random-ish headlines based on symbol and date
        seed_value = sum(ord(c) for c in symbol) + target_date.day
        selected_indices = [(seed_value + i) % len(mock_headline_templates) for i in range(3)]
        
        result = []
        for i, idx in enumerate(selected_indices):
            headline_text = mock_headline_templates[idx].format(symbol=symbol)
            result.append(NewsHeadline(
                symbol=symbol,
                date=target_date - timedelta(days=i*2),
                headline=headline_text,
                source="MockFinancialNews",
                url=None
            ))
        
        return result
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        self.metrics_cache.clear()