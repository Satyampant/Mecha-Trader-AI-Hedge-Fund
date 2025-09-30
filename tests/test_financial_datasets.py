"""
Test Financial Datasets API
Documentation: https://financialdatasets.ai/
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# API configuration
BASE_URL = "https://api.financialdatasets.ai"
API_KEY = os.getenv("FINANCIAL_DATASETS_API_KEY", "")

# Headers for API requests
headers = {}
if API_KEY:
    headers["X-API-Key"] = API_KEY

print("Testing Financial Datasets API...")
print(f"API Key configured: {'Yes' if API_KEY else 'No (using free tier)'}")

# Test 1: Fetch AAPL price data
try:
    print("\nTest 1: Fetch AAPL historical prices")
    url = f"{BASE_URL}/prices"
    params = {
        "ticker": "AAPL",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "interval": "day"
    }
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    print(f"✓ Success! Response keys: {data.keys()}")
    
    if 'prices' in data:
        print(f"  Downloaded {len(data['prices'])} days of data")
        print(f"  Sample: {data['prices'][0] if data['prices'] else 'No data'}")
    
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 2: Fetch AAPL fundamentals
try:
    print("\nTest 2: Fetch AAPL financials/fundamentals")
    url = f"{BASE_URL}/financials"
    params = {
        "ticker": "AAPL",
        "period": "ttm",  # trailing twelve months
        "limit": 1
    }
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    print(f"✓ Success! Response keys: {data.keys()}")
    
    if 'financials' in data:
        print(f"  Retrieved {len(data['financials'])} financial reports")
        if data['financials']:
            print(f"  Sample keys: {list(data['financials'][0].keys())[:5]}")
    
except Exception as e:
    print(f"✗ Failed: {e}")

print("\n" + "="*60)
print("Test complete!")
print("="*60)