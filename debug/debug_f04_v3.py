import pandas as pd
import requests
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')

def debug_fetch(date, market_code):
    url = f"https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate={date}&marketCode={market_code}&commodity_id=TX"
    market_name = "Regular" if market_code == 0 else "After-Hours"
    print(f"Fetching {market_name} ({url})")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers)
        r.encoding = 'utf-8'
        dfs = pd.read_html(io.StringIO(r.text))
        df = dfs[0]
        
        # Helper to find cols
        def find_col(keywords):
            for c in df.columns:
                if any(k in str(c) for k in keywords):
                    return c
            return None

        contract_col = find_col(['契約', 'Contract'])
        if not contract_col: contract_col = df.columns[0]
        
        df['clean'] = df[contract_col].astype(str).str.strip()
        tx_rows = df[df['clean'] == 'TX']
        
        if not tx_rows.empty:
            print(f"--- {market_name} TX Row ---")
            print(tx_rows.iloc[0].to_string())
        else:
            print(f"No TX rows for {market_name}")

    except Exception as e:
        print(f"Error: {e}")

debug_fetch("2025/12/04", 0) # Regular
print("-" * 30)
debug_fetch("2025/12/04", 1) # After Hours
