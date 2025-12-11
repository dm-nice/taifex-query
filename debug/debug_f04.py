import pandas as pd
import requests
import io
import sys

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')

def debug_fetch(date):
    url = f"https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate={date}&marketCode=0&commodity_id=TX"
    print(f"Fetching {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    
    dfs = pd.read_html(io.StringIO(r.text))
    df = dfs[0]
    
    # Identify key columns
    contract_col = None
    month_col = None
    price_col = None
    
    for c in df.columns:
        c_str = str(c)
        if '契約' in c_str or 'Contract' in c_str:
            contract_col = c
        elif '到期' in c_str or 'Month' in c_str:
            month_col = c
        elif '最後成交價' in c_str or 'Close' in c_str or 'Last Price' in c_str:
            price_col = c
            
    print(f"Columns mapped: Contract={contract_col}, Month={month_col}, Price={price_col}")
    
    if not contract_col or not price_col:
        print("Could not map columns!")
        return

    df['clean_contract'] = df[contract_col].astype(str).str.strip()
    tx_rows = df[df['clean_contract'] == 'TX']
    
    print(f"\nFound {len(tx_rows)} TX rows:")
    if month_col:
        print(tx_rows[[contract_col, month_col, price_col]].to_string())
    else:
        print(tx_rows[[contract_col, price_col]].to_string())

debug_fetch("2025/12/04")
