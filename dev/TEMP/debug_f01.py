
import requests
import pandas as pd
import json

def debug_fetch(date):
    url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={date.replace('-', '/')}"
    print(f"Fetching URL: {url}")
    resp = requests.get(url, timeout=10)
    resp.encoding = "utf-8"

    tables = pd.read_html(resp.text)
    if len(tables) == 0:
        print("No tables found")
        return

    df = tables[0]
    print("\n--- DataFrame Columns (Full) ---")
    for col in df.columns:
        print(col)
    
    print("\n--- DataFrame Head ---")
    print(df.head())

    # Check for MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        # Try to find '身份別'
        trader_col = None
        for col in df.columns:
            if '身份別' in str(col) or '身份' in str(col):
                trader_col = col
                break
        print(f"\nTrader Column Found: {trader_col}")
        
        if trader_col:
            print("\n--- Foreign Rows ---")
            # Print unique values in trader column to see what '外資' looks like
            print("Unique values in trader column:", df[trader_col].unique())
            
            foreign_rows = df[df[trader_col] == '外資']
            print(foreign_rows)
            
            if len(foreign_rows) == 0:
                print("No rows with '外資' found. Trying partial match...")
                mask = df[trader_col].astype(str).str.contains('外資')
                print(df[mask])

if __name__ == "__main__":
    debug_fetch("2025-12-02")
