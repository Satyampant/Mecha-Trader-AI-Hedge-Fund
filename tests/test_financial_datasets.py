import financial_datasets as fd

print("Testing Financial Datasets connection...")

try:
    print("\nTest 1: Fetch AAPL price data")
    df = fd.load_prices(ticker="AAPL", start_date="2024-01-01", end_date="2024-01-31")
    print(f"✓ Success! Downloaded {len(df)} days of data")
    print(df.head())
except Exception as e:
    print(f"✗ Failed: {e}")

try:
    print("\nTest 2: Fetch AAPL fundamentals")
    df = fd.load_fundamentals(ticker="AAPL")
    print(f"✓ Success! Got {len(df)} reports")
    print(df.head())
except Exception as e:
    print(f"✗ Failed: {e}")