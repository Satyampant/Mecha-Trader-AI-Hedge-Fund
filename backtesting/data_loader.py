"""
Data loader for backtesting
Prefetches and caches all historical data needed for backtest
"""

from typing import Dict, List
from datetime import datetime
from mcp.market_data_connector import MCPMarketDataConnector
from models.shared_models import StockData, FinancialMetrics, NewsHeadline


class DataLoader:
    """Prefetches and caches all backtest data"""
    
    def __init__(self, mcp_connector: MCPMarketDataConnector):
        """
        Initialize data loader
        
        Args:
            mcp_connector: MCP connector instance for fetching data
        """
        self.mcp = mcp_connector
        self.price_data: Dict[str, List[StockData]] = {}
        self.financial_data: Dict[str, FinancialMetrics] = {}
        self.news_data: Dict[str, List[NewsHeadline]] = {}
        self.benchmark_data: List[StockData] = []
    
    def load_all_data(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        benchmark: str = "SPY"
    ):
        """
        Load all data for backtest period
        
        Args:
            symbols: List of stock tickers
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            benchmark: Benchmark ticker (default SPY)
        """
        print(f"📥 Loading data for {len(symbols)} symbols from {start_date} to {end_date}...")
        
        # Load price data for each symbol
        for symbol in symbols:
            print(f"  • Loading {symbol} price data...")
            try:
                self.price_data[symbol] = self.mcp.execute_tool(
                    "get_stock_prices",
                    {
                        "symbol": symbol,
                        "start_date": start_date,
                        "end_date": end_date
                    }
                )
                
                if not self.price_data[symbol]:
                    print(f"    ⚠️  No price data available for {symbol}")
                else:
                    print(f"    ✓ Loaded {len(self.price_data[symbol])} trading days")
                
                # Load financial metrics (snapshot at start date)
                print(f"  • Loading {symbol} financial metrics...")
                self.financial_data[symbol] = self.mcp.execute_tool(
                    "get_financial_metrics",
                    {
                        "symbol": symbol,
                        "date": start_date
                    }
                )
                
                if self.financial_data[symbol]:
                    print(f"    ✓ Financial metrics loaded")
                else:
                    print(f"    ⚠️  No financial metrics available")
                    
            except Exception as e:
                print(f"    ❌ Error loading data for {symbol}: {e}")
                self.price_data[symbol] = []
                self.financial_data[symbol] = None
        
        # Load benchmark data
        print(f"  • Loading benchmark {benchmark}...")
        try:
            self.benchmark_data = self.mcp.execute_tool(
                "get_stock_prices",
                {
                    "symbol": benchmark,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            if self.benchmark_data:
                print(f"    ✓ Loaded {len(self.benchmark_data)} trading days")
            else:
                print(f"    ⚠️  No benchmark data available")
                
        except Exception as e:
            print(f"    ❌ Error loading benchmark: {e}")
            self.benchmark_data = []
        
        print("✅ Data loading complete\n")
    
    def get_price_data(
        self,
        symbol: str,
        end_date: datetime,
        lookback_days: int = 200
    ) -> List[StockData]:
        """
        Get price data up to a specific date
        
        Args:
            symbol: Stock ticker
            end_date: End date for data
            lookback_days: Number of days to look back
            
        Returns:
            List of StockData up to end_date
        """
        all_data = self.price_data.get(symbol, [])
        
        # Filter data up to end_date
        filtered = [d for d in all_data if d.date <= end_date]
        
        # Return last lookback_days entries
        if len(filtered) > lookback_days:
            return filtered[-lookback_days:]
        
        return filtered
    
    def get_financial_metrics(self, symbol: str) -> FinancialMetrics:
        """
        Get cached financial metrics for symbol
        
        Args:
            symbol: Stock ticker
            
        Returns:
            FinancialMetrics object or None
        """
        return self.financial_data.get(symbol)
    
    def get_news_headlines(
        self,
        symbol: str,
        date: datetime
    ) -> List[NewsHeadline]:
        """
        Get news headlines for a specific date
        
        Args:
            symbol: Stock ticker
            date: Reference date
            
        Returns:
            List of NewsHeadline objects
        """
        # For PoC, fetch on-demand
        # In production, this would be cached during load_all_data
        try:
            return self.mcp.execute_tool(
                "get_news_headlines",
                {
                    "symbol": symbol,
                    "date": date.strftime("%Y-%m-%d"),
                    "days_back": 7
                }
            )
        except Exception as e:
            print(f"Warning: Error fetching news for {symbol}: {e}")
            return []
    
    def get_benchmark_data(self) -> List[StockData]:
        """
        Get benchmark price data
        
        Returns:
            List of StockData for benchmark
        """
        return self.benchmark_data
    
    def get_trading_dates(self) -> List[datetime]:
        """
        Get list of all trading dates in the dataset
        
        Returns:
            Sorted list of datetime objects
        """
        if not self.benchmark_data:
            # If no benchmark data, use first symbol's dates
            for symbol_data in self.price_data.values():
                if symbol_data:
                    dates = sorted(set(d.date for d in symbol_data))
                    return dates
            return []
        
        dates = sorted(set(d.date for d in self.benchmark_data))
        return dates
    
    def get_summary(self) -> Dict:
        """
        Get summary of loaded data
        
        Returns:
            Dictionary with data statistics
        """
        return {
            "symbols": list(self.price_data.keys()),
            "price_data_points": {
                symbol: len(data) 
                for symbol, data in self.price_data.items()
            },
            "financial_metrics_available": {
                symbol: metrics is not None
                for symbol, metrics in self.financial_data.items()
            },
            "benchmark_data_points": len(self.benchmark_data),
            "trading_dates": len(self.get_trading_dates())
        }