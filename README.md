# AI Hedge Fund - Multi-Agent Trading System

A proof-of-concept multi-agent AI system for simulated stock trading, featuring specialized analyst agents, portfolio management, and comprehensive backtesting capabilities.

## 🎯 Features

- **Multi-Agent Architecture**: Coordinated Technical, Sentiment, and Fundamental analysis agents
- **MCP Integration**: Model Context Protocol for standardized data access
- **Groq LLM**: Fast inference using Llama-3.3-70B-Versatile
- **Comprehensive Backtesting**: Full simulation engine with performance metrics
- **Multi-Modal Output**: Text reports, visualizations (charts), and voice summaries
- **Risk Management**: Position sizing and cash reserve constraints

## 🏗️ Architecture
┌─────────────────────────────────────────────────┐
│              Orchestrator                        │
│         (Main Coordination Logic)                │
└────────────┬────────────────────────────────────┘
│
┌────────┴────────┬────────────┬──────────────┐
│                 │            │              │
┌───▼────┐     ┌─────▼─────┐  ┌──▼────┐    ┌────▼────┐
│Technical│     │ Sentiment │  │Fundamental  │Portfolio│
│ Agent  │     │  Agent    │  │  Agent   │  │ Manager │
└───┬────┘     └─────┬─────┘  └───┬────┘    └────┬────┘
│                │            │              │
└────────────────┴────────────┴──────────────┘
│
┌────────┴─────────┐
│                  │
┌───▼────┐      ┌─────▼──────┐
│  MCP   │      │ Simulator  │
│Connector│      │ & Metrics  │
└────────┘      └────────────┘

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- Groq API Key ([Get one here](https://console.groq.com))

### Setup Steps
```bash
# 1. Clone the repository
git clone <repository-url>
cd ai-hedge-fund

# 2. Create and activate virtual environment
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env

# 5. Edit .env and add your GROQ_API_KEY
nano .env  # or use your preferred editor
🚀 Usage
Basic Backtest
Run a backtest with default settings (AAPL, MSFT, GOOGL from 2024-04-01 to 2024-10-01):
bashpython orchestrator.py
Custom Configuration
Specify custom symbols, date range, and initial capital:
bashpython orchestrator.py \
  --symbols AAPL,MSFT,GOOGL,TSLA \
  --start-date 2024-01-01 \
  --end-date 2024-06-30 \
  --capital 250000
Command-Line Options
OptionDescriptionDefault--symbolsComma-separated stock tickersAAPL,MSFT,GOOGL--start-dateBacktest start date (YYYY-MM-DD)2024-04-01--end-dateBacktest end date (YYYY-MM-DD)2024-10-01--capitalInitial capital in USD100000
Example Commands
bash# Single stock backtest
python orchestrator.py --symbols AAPL --start-date 2024-01-01 --end-date 2024-03-31

# Large portfolio with more capital
python orchestrator.py --symbols AAPL,MSFT,GOOGL,AMZN,TSLA --capital 500000

# Short-term backtest (1 month)
python orchestrator.py --start-date 2024-09-01 --end-date 2024-09-30
📊 Output
The system generates three types of output (multi-modal):
1. Text Report (Console)
==========================================================
              BACKTEST RESULTS
==========================================================
Initial Capital               $100,000.00
Final Value                   $112,450.00
Total Return                        +12.45%
Profit/Loss                    +$12,450.00

Sharpe Ratio                          0.782
Sortino Ratio                         1.124
Max Drawdown                          8.30%

Total Trades                             47
Winning Trades                           28
Losing Trades                            19
Win Rate                              59.6%
==========================================================
2. Visualization (portfolio_performance.png)

Portfolio vs benchmark comparison chart
Normalized performance (starting value = 100)
High-resolution PNG saved to current directory

3. Voice Summary (Audio Playback)

Spoken summary of key results
Uses text-to-speech (pyttsx3)
Automatically plays at the end of backtest

🧪 Testing
Run the test suite:
bash# Install pytest if not already installed
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_agents.py -v
🔧 Configuration
Environment Variables (.env)
bash# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional overrides (uncomment to use)
# INITIAL_CAPITAL=100000
# START_DATE=2024-04-01
# END_DATE=2024-10-01
System Settings (config/settings.py)
Modify these settings directly in config/settings.py:

LLM Model: GROQ_MODEL = "llama-3.3-70b-versatile"
Temperature: LLM_TEMPERATURE = 0.3
Max Position Size: MAX_POSITION_SIZE = 0.3 (30% of portfolio)
Cash Reserve: CASH_RESERVE = 0.1 (10% minimum cash)
Risk-Free Rate: RISK_FREE_RATE = 0.02 (2% annual)

📁 Project Structure
ai-hedge-fund/
├── config/
│   └── settings.py              # Configuration management
├── agents/
│   ├── __init__.py
│   ├── base_agent.py            # Base agent class
│   ├── technical_agent.py       # Technical analysis
│   ├── sentiment_agent.py       # News sentiment analysis
│   ├── fundamental_agent.py     # Financial metrics analysis
│   └── portfolio_manager.py     # Trading decisions
├── backtesting/
│   ├── __init__.py
│   ├── data_loader.py           # Data prefetching
│   ├── simulator.py             # Trade simulation
│   └── metrics.py               # Performance calculation
├── mcp/
│   ├── __init__.py
│   └── market_data_connector.py # MCP data interface
├── models/
│   ├── __init__.py
│   └── shared_models.py         # Data structures
├── utils/
│   ├── __init__.py
│   ├── helpers.py               # Utility functions
│   ├── prompts.py               # LLM prompt templates
│   └── output_handlers.py       # Multi-modal outputs
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Test fixtures
│   └── test_*.py                # Test modules
├── orchestrator.py              # Main entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .gitignore
└── README.md
🤝 How It Works
Multi-Agent System

Technical Agent

Analyzes price patterns, SMA, RSI
Generates BUY/SELL/HOLD signals based on chart patterns


Sentiment Agent

Analyzes news headlines
Assesses market sentiment
Provides confidence-weighted signals


Fundamental Agent

Evaluates P/E ratio, market cap, debt-to-equity
Compares metrics to industry averages
Recommends based on valuation


Portfolio Manager

Aggregates signals from all analysts
Makes final trading decisions
Enforces risk management rules



Backtest Flow
1. Load historical data (prices, metrics, news)
   ↓
2. For each trading day:
   a. Get current prices
   b. Run analyst agents → generate signals
   c. Portfolio manager decides → create orders
   d. Simulator executes trades
   e. Update portfolio value
   ↓
3. Calculate performance metrics
   ↓
4. Generate outputs (text, chart, voice)
Risk Management

Position Sizing: Max 30% of portfolio per stock
Cash Reserve: Maintain 10% minimum cash
Validation: All trades validated before execution
Stop-loss: Implicit through agent signals

📈 Performance Metrics
The system calculates:

Total Return: Percentage gain/loss
Sharpe Ratio: Risk-adjusted return
Sortino Ratio: Downside risk-adjusted return
Max Drawdown: Largest peak-to-trough decline
Win Rate: Percentage of profitable trades

🔍 Troubleshooting
Common Issues
Issue: ValueError: GROQ_API_KEY not set

Solution: Add your Groq API key to .env file

Issue: No trading dates available

Solution: Check date range and ensure markets were open

Issue: Voice synthesis unavailable

Solution: Install pyttsx3 dependencies for your OS

macOS: brew install espeak
Linux: sudo apt-get install espeak
Windows: Built-in support



Issue: ModuleNotFoundError

Solution: Run pip install -r requirements.txt

Issue: No price data available

Solution: Check internet connection and yfinance API status

⚠️ Limitations (PoC)
This is a proof-of-concept system with intentional simplifications:

Mock news headlines (not real news API)
Simplified position sizing
No real-time trading
Basic technical indicators only
No transaction costs modeled
Single-threaded execution

🚀 Future Enhancements
Potential production improvements:

 Real news API integration (NewsAPI, Alpha Vantage)
 Advanced technical indicators (MACD, Bollinger Bands)
 Risk management agent (separate from portfolio manager)
 Database persistence (PostgreSQL, MongoDB)
 Web dashboard (React + FastAPI)
 Paper trading mode
 Multi-asset support (crypto, forex, options)
 Real-time streaming data
 Advanced position sizing algorithms
 Transaction cost modeling

📄 License
MIT License - See LICENSE file for details
⚠️ Disclaimer
IMPORTANT: This is a simulation system for educational purposes only.

Not financial advice: Do not use for real trading decisions
No warranties: System provided "as is" without guarantees
Paper trading: Test thoroughly before any real-world use
Risk warning: Past performance does not guarantee future results

By using this software, you acknowledge:

You understand the risks of algorithmic trading
You will not hold the authors liable for any losses
You will comply with all applicable securities regulations

🙏 Acknowledgments

Groq: Fast LLM inference
yfinance: Market data access
LangChain: Agent framework
OpenAI: Inspiration for multi-agent systems

📧 Support
For issues, questions, or contributions:

Open an issue on GitHub
Check existing documentation
Review test cases for usage examples

