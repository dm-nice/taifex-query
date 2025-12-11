import pandas as pd
import requests
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')

def debug_fetch(date):
    url = f"https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate={date}&marketCode=0&commodity_id=TX"
    print(f"Fetching {url}")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8' # Force utf-8
    
    # Try parsing
    try:
        dfs = pd.read_html(io.StringIO(r.text))
    except:
        print("Parse failed")
        return

    df = dfs[0]
    
    # Find contract col
    contract_col = None
    for c in df.columns:
        if '契約' in str(c) or 'Contract' in str(c):
             # Avoid '未沖銷契約量' (Open Interest) matching '契約'
             # The Contract column is usually just '契約'
             if '未沖銷' not in str(c):
                 contract_col = c
                 break
    if not contract_col:
        contract_col = df.columns[0]
        
    print(f"Contract Column Guessed: {contract_col}")
    
    df['clean_contract'] = df[contract_col].astype(str).str.strip()
    tx_rows = df[df['clean_contract'] == 'TX']
    
    if len(tx_rows) > 0:
        row = tx_rows.iloc[0]
        print("\n--- First TX Row Data ---")
        for col_name, val in row.items():
            print(f"[{col_name}] : {val}")
    else:
        print("No TX rows found")

debug_fetch("2025/12/04")
