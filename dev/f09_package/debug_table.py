"""
調試腳本：檢查 TAIFEX 夜盤表格實際欄位
"""
import requests
import pandas as pd
import io

url = "https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate=2025/12/17&marketCode=0&commodity_id=TX&queryType=2"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=30)
response.encoding = "utf-8"

dfs = pd.read_html(io.StringIO(response.text))
df = dfs[0]

print("=== 表格欄位 ===")
print(df.columns.tolist())
print("\n=== 前 5 行資料 ===")
print(df.head())
print("\n=== TX 行資料 ===")
df['clean_contract'] = df[df.columns[0]].astype(str).str.strip()
tx_rows = df[df['clean_contract'] == 'TX']
if len(tx_rows) > 0:
    print(tx_rows.iloc[0])
else:
    print("找不到 TX")
