"""
Implements standardized interface for fetching market data
Using FinancialDatasets REST API (free access for AAPL, GOOGL, MSFT, NVDA, TSLA)
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

from models.shared_models import StockData, FinancialMetrics, NewsHeadline

# Base URL for Financial Datasets API
FD_BASE = "https://api.financialdatasets.ai"

# Free tickers that don't require API key
FREE_TICKERS = {"AAPL", "GOOGL", "MSFT", "NVDA", "TSLA"}

# Read API key from environment by default
FD_API_KEY = os.getenv("FINANCIAL_DATASETS_API_KEY")


class MCPMarketDataConnector:
    """
    MCP-compliant market data provider using FinancialDatasets API
    Provides standardized access to stock prices, financial metrics, and news.

    Behavior:
      - For symbols in FREE_TICKERS, requests will be attempted without an API key.
      - For other symbols, FINANCIAL_DATASETS_API_KEY must be set (or passed into constructor).
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the MCP connector"""
        self.cache: Dict[str, pd.DataFrame] = {}
        self.metrics_cache: Dict[str, FinancialMetrics] = {}
        # allow passing API key explicitly (falls back to env var)
        self.api_key = api_key or FD_API_KEY
        # don't print an error here; we check per-request whether an API key is required
        self._headers = {"X-API-KEY": self.api_key} if self.api_key else {}

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
            raise ValueError(
                f"Unknown tool: {tool_name}. Available tools: {list(tool_map.keys())}"
            )

        return tool_map[tool_name](**params)

    def _require_api_key(self, symbol: str) -> bool:
        """Return True if an API key is required for the given symbol"""
        return symbol.upper() not in FREE_TICKERS

    def _get_stock_prices(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "day",
        interval_multiplier: int = 1,
    ) -> List[StockData]:
        """
        Fetch historical price data using FinancialDatasets /prices endpoint.

        Args:
            symbol: Stock ticker (e.g., "AAPL")
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            interval: one of {'minute','day','week','month','year'}
            interval_multiplier: integer multiplier for the interval

        Returns:
            List of StockData objects
        """
        cache_key = f"{symbol}_{start_date}_{end_date}_{interval}_{interval_multiplier}"

        # Check cache first
        if cache_key not in self.cache:
            # enforce API key requirement only when symbol is not free
            if self._require_api_key(symbol) and not self.api_key:
                print(f"Error: API key required for {symbol}. Please set FINANCIAL_DATASETS_API_KEY")
                return []

            params = {
                "ticker": symbol,
                "interval": interval,
                "interval_multiplier": interval_multiplier,
                "start_date": start_date,
                "end_date": end_date,
            }
            url = f"{FD_BASE}/prices/"

            try:
                resp = requests.get(url, headers=self._headers if self.api_key else {}, params=params, timeout=30)
                resp.raise_for_status()
                payload = resp.json()
                prices = payload.get("prices") or payload.get("data") or payload.get("items") or []
                if not prices:
                    print(f"Warning: No data returned for {symbol} from {start_date} to {end_date}")
                    return []

                # Normalize into DataFrame for downstream behavior similar to yfinance
                df = pd.DataFrame(prices)

                # Attempt to standardize column names (some endpoints use 'time' or 'date')
                if "time" in df.columns:
                    df["datetime"] = pd.to_datetime(df["time"])
                elif "date" in df.columns:
                    df["datetime"] = pd.to_datetime(df["date"])
                elif "label" in df.columns:
                    df["datetime"] = pd.to_datetime(df["label"])
                else:
                    # if none present, try index or bail out
                    try:
                        df.index = pd.to_datetime(df.index)
                        df["datetime"] = df.index
                    except Exception:
                        print(f"Warning: could not find datetime column in prices for {symbol}")

                # ensure conventional columns exist (Open/High/Low/Close/Volume/Adj Close)
                col_map = {}
                for c in ("open", "high", "low", "close", "volume", "adj_close"):
                    if c in df.columns:
                        col_map[c] = c.capitalize() if c != "adj_close" else "Adj Close"
                df.rename(columns=col_map, inplace=True)

                # set datetime index for iteration like yfinance's df.iterrows()
                df.set_index("datetime", inplace=True, drop=True)
                # store in cache
                self.cache[cache_key] = df
            except requests.HTTPError as e:
                print(f"HTTP error fetching prices for {symbol}: {e}")
                return []
            except Exception as e:
                print(f"Error fetching prices for {symbol}: {e}")
                return []

        df = self.cache[cache_key]

        # Convert DataFrame to list of StockData objects
        result: List[StockData] = []
        for date, row in df.iterrows():
            try:
                open_val = self._safe_get(row, ["Open", "open"])
                high_val = self._safe_get(row, ["High", "high"])
                low_val = self._safe_get(row, ["Low", "low"])
                close_val = self._safe_get(row, ["Close", "close"])
                adj_close_val = self._safe_get(row, ["Adj Close", "adj_close", "close"])
                volume_val = self._safe_get(row, ["Volume", "volume"]) or 0

                result.append(
                    StockData(
                        symbol=symbol,
                        date=pd.to_datetime(date).to_pydatetime(),
                        open=float(open_val) if open_val is not None else None,
                        high=float(high_val) if high_val is not None else None,
                        low=float(low_val) if low_val is not None else None,
                        close=float(close_val) if close_val is not None else None,
                        volume=int(volume_val) if volume_val is not None else 0,
                        adj_close=float(adj_close_val) if adj_close_val is not None else None,
                    )
                )
            except Exception as e:
                print(f"Warning: Skipping data point for {symbol} on {date}: {e}")
                continue

        return result

    def _get_financial_metrics(
        self,
        symbol: str,
        date: str,
    ) -> Optional[FinancialMetrics]:
        """
        Fetch fundamental financial metrics using FinancialDatasets /financial-metrics endpoint.

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

        # require API key for non-free tickers
        if self._require_api_key(symbol) and not self.api_key:
            print(f"Error: API key required for {symbol}. Please set FINANCIAL_DATASETS_API_KEY")
            return None

        url = f"{FD_BASE}/financial-metrics"
        params = {"ticker": symbol}

        try:
            resp = requests.get(url, headers=self._headers if self.api_key else {}, params=params, timeout=30)
            resp.raise_for_status()
            payload = resp.json()
            metrics_list = payload.get("financial_metrics") or payload.get("metrics") or payload.get("data") or []

            if not metrics_list:
                print(f"Warning: No financial metrics found for {symbol}")
                return None

            # Find the record closest to the requested date
            target_dt = datetime.strptime(date, "%Y-%m-%d")
            best_record = None
            best_diff = None
            for rec in metrics_list:
                rec_date_str = rec.get("date") or rec.get("report_date") or rec.get("as_of")
                if not rec_date_str:
                    continue
                try:
                    rec_dt = pd.to_datetime(rec_date_str).to_pydatetime()
                except Exception:
                    continue
                diff = abs((rec_dt - target_dt).days)
                if best_diff is None or diff < best_diff:
                    best_diff = diff
                    best_record = rec

            if not best_record:
                print(f"Warning: Could not match any financial metric date for {symbol}")
                return None

            pe_ratio = best_record.get("pe_ratio") or best_record.get("trailingPE") or best_record.get("pe")
            market_cap = best_record.get("market_cap") or best_record.get("marketCap") or best_record.get("market_capitalization")
            revenue_growth = best_record.get("revenue_growth") or best_record.get("revenueGrowth") or best_record.get("yoy_revenue_growth")
            debt_to_equity = best_record.get("debt_to_equity") or best_record.get("debtToEquity") or best_record.get("debt_equity_ratio")

            fm = FinancialMetrics(
                symbol=symbol,
                date=pd.to_datetime(best_record.get("date") or best_record.get("report_date") or date).to_pydatetime(),
                pe_ratio=float(pe_ratio) if pe_ratio is not None else None,
                market_cap=int(market_cap) if market_cap is not None else None,
                revenue_growth=float(revenue_growth) * 100 if revenue_growth is not None else None,
                debt_to_equity=float(debt_to_equity) if debt_to_equity is not None else None,
            )

            # Cache the result
            self.metrics_cache[cache_key] = fm

            return fm

        except requests.HTTPError as e:
            print(f"HTTP error fetching financial metrics for {symbol}: {e}")
            return None
        except Exception as e:
            print(f"Error fetching financial metrics for {symbol}: {e}")
            return None

    def _get_news_headlines(
        self,
        symbol: str,
        date: str,
        days_back: int = 7,
        limit: int = 10,
    ) -> List[NewsHeadline]:
        """
        Fetch recent news headlines using FinancialDatasets /news endpoint.

        This implementation is defensive:
        - uses 'ticker' (singular)
        - tries common date param names and falls back on press-releases
        - logs response body on 4xx/5xx to help debug
        """
        # require API key for non-free tickers
        if self._require_api_key(symbol) and not self.api_key:
            print(f"Error: API key required for {symbol}. Please set FINANCIAL_DATASETS_API_KEY")
            return []

        ref_dt = datetime.strptime(date, "%Y-%m-%d")
        from_date = (ref_dt - timedelta(days=days_back)).strftime("%Y-%m-%d")
        to_date = ref_dt.strftime("%Y-%m-%d")

        url = f"{FD_BASE}/news"
        headers = self._headers if self.api_key else {}

        # First attempt: use 'ticker' + 'from_date'/'to_date' (common in docs)
        params_attempts = [
            {"ticker": symbol, "from_date": from_date, "to_date": to_date, "limit": limit},
            # second attempt: alternative date param names
            {"ticker": symbol, "start_date": from_date, "end_date": to_date, "limit": limit},
            # third attempt: legacy plural param (in case); rarely required but harmless
            {"tickers": symbol, "from_date": from_date, "to_date": to_date, "limit": limit},
        ]

        items = []
        last_error_text = None

        for params in params_attempts:
            try:
                resp = requests.get(url, headers=headers, params=params, timeout=30)
                if resp.status_code == 200:
                    payload = resp.json()
                    items = payload.get("news") or payload.get("items") or payload.get("data") or payload.get("articles") or []
                    if items:
                        break  # got something useful
                    # if body 200 but empty, continue to next params attempt/fallback
                else:
                    # for 4xx/5xx, capture body for debugging and try next param style
                    last_error_text = f"HTTP {resp.status_code}: {resp.text}"
                    # try next param style
            except Exception as e:
                last_error_text = str(e)

        # if still empty, try press-release endpoint as fallback
        if not items:
            try:
                alt_url = f"{FD_BASE}/earnings/press-releases"
                alt_params = {"ticker": symbol, "from_date": from_date, "to_date": to_date, "limit": limit}
                alt_resp = requests.get(alt_url, headers=headers, params=alt_params, timeout=20)
                if alt_resp.ok:
                    alt_payload = alt_resp.json()
                    items = alt_payload.get("press_releases") or alt_payload.get("items") or []
                else:
                    last_error_text = f"Press releases fetch HTTP {alt_resp.status_code}: {alt_resp.text}"
            except Exception as e:
                last_error_text = str(e)

        if not items:
            if last_error_text:
                print(f"HTTP error fetching news for {symbol}: {last_error_text}")
            else:
                print(f"Warning: No news items found for {symbol} between {from_date} and {to_date}")
            return []

        # Map items defensively into NewsHeadline objects
        result: List[NewsHeadline] = []
        for it in items[:limit]:
            published_at = it.get("published_at") or it.get("date") or it.get("time") or it.get("pub_date")
            try:
                published_dt = pd.to_datetime(published_at).to_pydatetime() if published_at else None
            except Exception:
                published_dt = None

            title = it.get("title") or it.get("headline") or it.get("summary") or it.get("description")
            source = it.get("source") or it.get("publisher") or it.get("site") or "FinancialDatasets"
            url_field = it.get("url") or it.get("link")

            if not title:
                continue

            nh = NewsHeadline(
                symbol=symbol,
                date=published_dt if published_dt else ref_dt,
                headline=title,
                source=source,
                url=url_field,
            )
            result.append(nh)

        return result
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        self.metrics_cache.clear()

    @staticmethod
    def _safe_get(row, keys):
        """helper to pull first available key from a pandas Series/row"""
        for k in keys:
            if k in row and pd.notna(row[k]):
                return row[k]
        return None
