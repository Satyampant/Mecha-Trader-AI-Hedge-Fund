#!/usr/bin/env python3
"""
AI Hedge Fund - Main Orchestrator
Coordinates multi-agent trading system and backtesting engine
"""

import argparse
from datetime import datetime
from typing import List, Dict
from config.settings import Config
from mcp.market_data_connector import MCPMarketDataConnector
from backtesting.data_loader import DataLoader
from backtesting.simulator import TradingSimulator
from backtesting.metrics import PerformanceMetrics
from agents.technical_agent import TechnicalAgent
from agents.sentiment_agent import SentimentAgent
from agents.fundamental_agent import FundamentalAgent
from agents.portfolio_manager import PortfolioManager
from utils.output_handlers import MultiModalOutputManager
from models.shared_models import AgentSignal


class AIHedgeFundOrchestrator:
    """Main orchestrator for AI hedge fund system"""
    
    def __init__(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        initial_capital: float
    ):
        """
        Initialize orchestrator
        
        Args:
            symbols: List of stock tickers to trade
            start_date: Backtest start date (YYYY-MM-DD)
            end_date: Backtest end date (YYYY-MM-DD)
            initial_capital: Starting capital
        """
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        
        # Display banner
        print("\n" + "="*70)
        print(" "*15 + "🤖 AI HEDGE FUND - MULTI-AGENT SYSTEM")
        print("="*70)
        print()
        
        # Initialize components
        print("🚀 Initializing system components...")
        
        # MCP connector
        print("  • Creating MCP market data connector...")
        self.mcp = MCPMarketDataConnector()
        
        # Data loader
        print("  • Initializing data loader...")
        self.data_loader = DataLoader(self.mcp)
        
        # Trading simulator
        print("  • Setting up trading simulator...")
        self.simulator = TradingSimulator(initial_capital)
        
        # Initialize agents
        print("  • Creating analyst agents...")
        self.technical_agent = TechnicalAgent()
        print("    ✓ Technical Agent")
        
        self.sentiment_agent = SentimentAgent()
        print("    ✓ Sentiment Agent")
        
        self.fundamental_agent = FundamentalAgent()
        print("    ✓ Fundamental Agent")
        
        print("  • Creating portfolio manager...")
        self.portfolio_manager = PortfolioManager()
        print("    ✓ Portfolio Manager")
        
        # Output manager
        print("  • Initializing multi-modal output manager...")
        self.output_manager = MultiModalOutputManager()
        
        print("\n✅ Initialization complete\n")
    
    def run_backtest(self):
        """Execute complete backtest loop"""
        
        # Step 1: Load all data
        print("=" * 70)
        print("PHASE 1: DATA LOADING")
        print("=" * 70)
        
        self.data_loader.load_all_data(
            symbols=self.symbols,
            start_date=self.start_date,
            end_date=self.end_date,
            benchmark="SPY"
        )
        
        # Get trading dates
        trading_dates = self.data_loader.get_trading_dates()
        
        if not trading_dates:
            print("❌ No trading dates available. Exiting.")
            return None
        
        print(f"📅 Trading period: {len(trading_dates)} days")
        print(f"   Start: {trading_dates[0].strftime('%Y-%m-%d')}")
        print(f"   End:   {trading_dates[-1].strftime('%Y-%m-%d')}\n")
        
        # Step 2: Run simulation loop
        print("=" * 70)
        print("PHASE 2: SIMULATION LOOP")
        print("=" * 70)
        print()
        
        for i, current_date in enumerate(trading_dates):
            date_str = current_date.strftime('%Y-%m-%d')
            print(f"📆 Day {i+1}/{len(trading_dates)}: {date_str}")
            
            # Get current prices for all symbols
            current_prices = self._get_current_prices(current_date)
            
            if not current_prices:
                print("  ⚠️  No price data available for this date")
                # Still update portfolio value with previous prices
                self.simulator.update_portfolio_value({}, current_date)
                continue
            
            # Process each symbol
            for symbol in self.symbols:
                if symbol not in current_prices:
                    print(f"  ⚠️  No price data for {symbol}")
                    continue
                
                print(f"  🔍 Analyzing {symbol} (${current_prices[symbol]:.2f})...")
                
                # Collect analyst signals
                signals = self._gather_analyst_signals(symbol, current_date)
                
                if not signals:
                    print(f"    ⚠️  No signals generated for {symbol}")
                    continue
                
                # Display signals
                for sig in signals:
                    print(f"    • {sig.agent_name}: {sig.signal.value} (confidence: {sig.confidence:.2f})")
                
                # Portfolio manager makes decision
                portfolio_state = self.simulator.get_current_state(current_date)
                trades = self.portfolio_manager.decide_trades(
                    symbol=symbol,
                    analyst_signals=signals,
                    portfolio_state=portfolio_state,
                    current_price=current_prices[symbol]
                )
                
                # Execute trades
                if trades:
                    self.simulator.execute_trades(trades, current_date)
                else:
                    print(f"    → HOLD (no action)")
            
            # Update portfolio value at end of day
            self.simulator.update_portfolio_value(current_prices, current_date)
            
            # Display portfolio status
            current_state = self.simulator.get_current_state(current_date)
            print(f"  💰 Portfolio Value: ${current_state.total_value:,.2f}")
            print()
        
        print("=" * 70)
        print("✅ Simulation complete")
        print("=" * 70)
        print()
        
        # Step 3: Calculate performance metrics
        print("=" * 70)
        print("PHASE 3: PERFORMANCE ANALYSIS")
        print("=" * 70)
        
        portfolio_values = self.simulator.get_portfolio_values()
        benchmark_data = self.data_loader.get_benchmark_data()
        
        # Align benchmark values with trading dates
        benchmark_values = []
        if benchmark_data:
            benchmark_dict = {d.date: d.close for d in benchmark_data}
            benchmark_values = [
                benchmark_dict.get(date, 0) 
                for date in trading_dates
            ]
            
            # Normalize benchmark to same starting capital
            if benchmark_values and benchmark_values[0] > 0:
                benchmark_multiplier = self.initial_capital / benchmark_values[0]
                benchmark_values = [v * benchmark_multiplier for v in benchmark_values]
        
        # Get trade P&Ls
        trade_pnls = self.simulator.get_trade_pnls()
        
        # Generate performance report
        final_value = portfolio_values[-1] if portfolio_values else self.initial_capital
        
        report = PerformanceMetrics.generate_report(
            initial_capital=self.initial_capital,
            final_value=final_value,
            portfolio_values=portfolio_values,
            num_trades=self.simulator.get_trade_count(),
            trade_pnls=trade_pnls
        )
        
        # Calculate benchmark metrics for comparison
        if benchmark_values and len(benchmark_values) > 1:
            benchmark_returns = PerformanceMetrics.calculate_returns(benchmark_values)
            benchmark_sharpe = PerformanceMetrics.sharpe_ratio(benchmark_returns)
            benchmark_return = ((benchmark_values[-1] - self.initial_capital) / self.initial_capital) * 100
            
            print(f"\n📊 Benchmark (SPY) Performance:")
            print(f"   Total Return: {benchmark_return:+.2f}%")
            print(f"   Sharpe Ratio: {benchmark_sharpe:.3f}")
        
        # Step 4: Generate outputs (multi-modal)
        print("\n" + "=" * 70)
        print("PHASE 4: OUTPUT GENERATION")
        print("=" * 70)
        
        self.output_manager.generate_all_outputs(
            report=report,
            dates=self.simulator.get_dates(),
            portfolio_values=portfolio_values,
            benchmark_values=benchmark_values
        )
        
        return report
    
    def _get_current_prices(self, date: datetime) -> Dict[str, float]:
        """
        Get current prices for all symbols on specific date
        
        Args:
            date: Target date
            
        Returns:
            Dict of {symbol: price}
        """
        prices = {}
        for symbol in self.symbols:
            price_data = self.data_loader.get_price_data(symbol, date, lookback_days=1)
            if price_data:
                prices[symbol] = price_data[-1].close
        
        return prices
    
    def _gather_analyst_signals(
        self,
        symbol: str,
        date: datetime
    ) -> List[AgentSignal]:
        """
        Collect signals from all analyst agents
        
        Args:
            symbol: Stock ticker
            date: Current date
            
        Returns:
            List of AgentSignal objects
        """
        signals = []
        
        # Technical analysis
        price_history = self.data_loader.get_price_data(symbol, date, lookback_days=200)
        if price_history:
            try:
                tech_signal = self.technical_agent.analyze(symbol, price_history)
                signals.append(tech_signal)
            except Exception as e:
                print(f"      ⚠️  Technical analysis error: {e}")
        
        # Sentiment analysis
        try:
            headlines = self.data_loader.get_news_headlines(symbol, date)
            sent_signal = self.sentiment_agent.analyze(
                symbol,
                headlines,
                date.strftime("%Y-%m-%d")
            )
            signals.append(sent_signal)
        except Exception as e:
            print(f"      ⚠️  Sentiment analysis error: {e}")
        
        # Fundamental analysis
        try:
            metrics = self.data_loader.get_financial_metrics(symbol)
            current_price = price_history[-1].close if price_history else 0
            fund_signal = self.fundamental_agent.analyze(symbol, metrics, current_price)
            signals.append(fund_signal)
        except Exception as e:
            print(f"      ⚠️  Fundamental analysis error: {e}")
        
        return signals


def main():
    """Main entry point"""
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='AI Hedge Fund - Multi-Agent Backtesting System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python orchestrator.py
  python orchestrator.py --symbols AAPL,MSFT --start-date 2024-01-01 --end-date 2024-06-30
  python orchestrator.py --capital 250000 --symbols AAPL,GOOGL,TSLA
        """
    )
    
    parser.add_argument(
        '--symbols',
        type=str,
        default=','.join(Config.SYMBOLS),
        help=f'Comma-separated list of stock symbols (default: {",".join(Config.SYMBOLS)})'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        default=Config.START_DATE,
        help=f'Start date in YYYY-MM-DD format (default: {Config.START_DATE})'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        default=Config.END_DATE,
        help=f'End date in YYYY-MM-DD format (default: {Config.END_DATE})'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=Config.INITIAL_CAPITAL,
        help=f'Initial capital in dollars (default: {Config.INITIAL_CAPITAL})'
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}\n")
        return 1
    
    # Parse symbols
    symbols = [s.strip().upper() for s in args.symbols.split(',')]
    
    if not symbols:
        print("\n❌ Error: No symbols specified\n")
        return 1
    
    # Create orchestrator
    try:
        orchestrator = AIHedgeFundOrchestrator(
            symbols=symbols,
            start_date=args.start_date,
            end_date=args.end_date,
            initial_capital=args.capital
        )
    except Exception as e:
        print(f"\n❌ Initialization Error: {e}\n")
        import traceback
        traceback.print_exc()
        return 1
    
    # Run backtest
    try:
        report = orchestrator.run_backtest()
        
        if report:
            print("\n" + "=" * 70)
            print("🎉 BACKTEST COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print()
        else:
            print("\n" + "=" * 70)
            print("⚠️  BACKTEST COMPLETED WITH WARNINGS")
            print("=" * 70)
            print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Backtest interrupted by user")
        return 130
    
    except Exception as e:
        print(f"\n❌ Runtime Error: {e}\n")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())