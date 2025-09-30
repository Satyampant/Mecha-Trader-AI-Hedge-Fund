"""
Multi-modal output handlers
Provides visualization (charts), text formatting, and voice synthesis
"""

import matplotlib.pyplot as plt
from datetime import datetime
from typing import List
import pyttsx3
from models.shared_models import PerformanceReport


class VisualizationHandler:
    """Handles chart generation (vision modality)"""
    
    @staticmethod
    def generate_portfolio_chart(
        dates: List[datetime],
        portfolio_values: List[float],
        benchmark_values: List[float],
        output_path: str = "portfolio_performance.png"
    ):
        """
        Generate portfolio performance chart
        
        Args:
            dates: List of dates
            portfolio_values: Portfolio values over time
            benchmark_values: Benchmark values over time
            output_path: Path to save chart
        """
        if len(dates) == 0 or len(portfolio_values) == 0:
            print("⚠️  Insufficient data to generate chart")
            return
        
        plt.figure(figsize=(12, 6))
        
        # Normalize both to starting value of 100
        portfolio_normalized = [v / portfolio_values[0] * 100 for v in portfolio_values]
        
        if benchmark_values and len(benchmark_values) > 0:
            # Ensure benchmark values align with portfolio dates
            min_len = min(len(portfolio_normalized), len(benchmark_values))
            benchmark_normalized = [v / benchmark_values[0] * 100 for v in benchmark_values[:min_len]]
            dates_trimmed = dates[:min_len]
            portfolio_normalized = portfolio_normalized[:min_len]
        else:
            benchmark_normalized = None
            dates_trimmed = dates
        
        # Plot portfolio
        plt.plot(
            dates_trimmed, 
            portfolio_normalized, 
            label='AI Hedge Fund', 
            linewidth=2, 
            color='#2E86AB'
        )
        
        # Plot benchmark if available
        if benchmark_normalized:
            plt.plot(
                dates_trimmed, 
                benchmark_normalized, 
                label='SPY Benchmark', 
                linewidth=2, 
                color='#A23B72', 
                linestyle='--'
            )
        
        plt.title('Portfolio Performance vs Benchmark', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Normalized Value (Starting = 100)', fontsize=12)
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n📊 Chart saved to: {output_path}")
        plt.close()
    
    @staticmethod
    def generate_metrics_table(report: PerformanceReport):
        """
        Print formatted metrics table to console
        
        Args:
            report: PerformanceReport object
        """
        print("\n" + "="*60)
        print(" "*18 + "BACKTEST RESULTS")
        print("="*60)
        
        metrics = [
            ("Initial Capital", f"${report.initial_capital:,.2f}"),
            ("Final Value", f"${report.final_value:,.2f}"),
            ("Total Return", f"{report.total_return:+.2f}%"),
            ("Profit/Loss", f"${report.profit_loss:+,.2f}"),
            ("", ""),
            ("Sharpe Ratio", f"{report.sharpe_ratio:.3f}"),
            ("Sortino Ratio", f"{report.sortino_ratio:.3f}"),
            ("Max Drawdown", f"{report.max_drawdown:.2f}%"),
            ("", ""),
            ("Total Trades", f"{report.num_trades}"),
            ("Winning Trades", f"{report.winning_trades}"),
            ("Losing Trades", f"{report.losing_trades}"),
            ("Win Rate", f"{report.win_rate:.1f}%"),
        ]
        
        for label, value in metrics:
            if label:  # Skip empty lines
                print(f"{label:<22} {value:>25}")
            else:
                print()
        
        print("="*60 + "\n")


class VoiceHandler:
    """Handles text-to-speech output (voice modality)"""
    
    def __init__(self):
        """Initialize TTS engine"""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  # Speed
            self.engine.setProperty('volume', 0.9)  # Volume
            self.enabled = True
        except Exception as e:
            print(f"⚠️  Voice synthesis unavailable: {e}")
            self.enabled = False
    
    def speak_summary(self, report: PerformanceReport):
        """
        Generate voice summary of results
        
        Args:
            report: PerformanceReport object
        """
        if not self.enabled:
            print("🔇 Voice output disabled")
            return
        
        # Create summary text
        summary = (
            f"Backtest complete. "
            f"Starting with {report.initial_capital:,.0f} dollars, "
            f"the portfolio grew to {report.final_value:,.0f} dollars, "
            f"achieving a total return of {report.total_return:.1f} percent. "
            f"The Sharpe ratio was {report.sharpe_ratio:.2f}, "
            f"with a maximum drawdown of {report.max_drawdown:.1f} percent. "
            f"Total trades executed: {report.num_trades}. "
            f"Win rate: {report.win_rate:.0f} percent."
        )
        
        print("\n🔊 Playing voice summary...")
        try:
            self.engine.say(summary)
            self.engine.runAndWait()
            print("✓ Voice summary complete")
        except Exception as e:
            print(f"❌ Error playing voice: {e}")


class MultiModalOutputManager:
    """Unified manager for all output modalities"""
    
    def __init__(self):
        self.viz = VisualizationHandler()
        self.voice = VoiceHandler()
    
    def generate_all_outputs(
        self,
        report: PerformanceReport,
        dates: List[datetime],
        portfolio_values: List[float],
        benchmark_values: List[float]
    ):
        """
        Generate all output types (text, vision, voice)
        
        Args:
            report: PerformanceReport
            dates: Trading dates
            portfolio_values: Portfolio value time series
            benchmark_values: Benchmark value time series
        """
        # Text output (modality 1)
        self.viz.generate_metrics_table(report)
        
        # Vision output (modality 2)
        self.viz.generate_portfolio_chart(
            dates=dates,
            portfolio_values=portfolio_values,
            benchmark_values=benchmark_values
        )
        
        # Voice output (modality 3)
        self.voice.speak_summary(report)