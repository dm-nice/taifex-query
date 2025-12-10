import pandas as pd
import requests
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Override to query Today 2025-12-10
def debug_fetch(date):
    url = f"https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate={date}&marketCode=0&commodity_id=TX"
    print(f"Fetching {url}")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers)
        r.encoding = 'utf-8'
        dfs = pd.read_html(io.StringIO(r.text))
        df = dfs[0]
        
        col_contract = None
        for c in df.columns:
            if '契約' in str(c): col_contract = c; break
        if not col_contract: col_contract = df.columns[0]
        
        df['clean'] = df[col_contract].astype(str).str.strip()
        tx_rows = df[df['clean'] == 'TX']
        
        if not tx_rows.empty:
            print("--- Today TX Row ---")
            print(tx_rows.iloc[0].to_string())
        else:
            print("No TX rows")

    except Exception as e:
        print(f"Error: {e}")

debug_fetch("2025/12/10")
