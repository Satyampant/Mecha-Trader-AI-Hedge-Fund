import yfinance as yf
import time

print("Testing yfinance connection...")

try:
    print("\nTest 1: Download AAPL data")
    data = yf.download('AAPL', start='2024-01-01', end='2024-01-31', progress=False)
    print(f"✓ Success! Downloaded {len(data)} days of data")
    print(data.head())
except Exception as e:
    print(f"✗ Failed: {e}")

time.sleep(2)

try:
    print("\nTest 2: Get AAPL ticker info")
    ticker = yf.Ticker('AAPL')
    info = ticker.info
    print(f"✓ Success! Got info for {info.get('symbol', 'AAPL')}")
    print(f"  PE Ratio: {info.get('trailingPE')}")
except Exception as e:
    print(f"✗ Failed: {e}")