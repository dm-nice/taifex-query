import pandas as pd
import requests

url = "https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate=2025/12/04&marketCode=0&commodity_id=TX"
print(f"Fetching {url}...")

try:
    dfs = pd.read_html(url)
    if dfs:
        df = dfs[0]
        print("Columns:")
        print(df.columns)
        print("\nFirst 5 rows:")
        print(df.head())
        
        # Check structure
        # Target: Date, Contract(TX), Delivery Month, Close Price
    else:
        print("No tables found.")
except Exception as e:
    print(f"Error: {e}")
