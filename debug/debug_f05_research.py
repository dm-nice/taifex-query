
import requests
import pandas as pd
from datetime import datetime

# 測試日期 (最近交易日)
DATE = "2025/12/10"

# 嘗試 1: 期貨每日交易行情 (futDailyMarketReport) - 但商品改為 TXO (台指選)
# 通常選擇權有自己的 URL，例如 optDailyMarketReport
URL_OPT = f"https://www.taifex.com.tw/cht/3/optDailyMarketReport?queryDate={DATE}&marketCode=0&commodity_id=TXO"

print(f"Testing URL: {URL_OPT}")

try:
    response = requests.get(URL_OPT, timeout=10)
    response.encoding = 'utf-8'
    
    tables = pd.read_html(response.text)
    print(f"Found {len(tables)} tables")
    
    if len(tables) > 0:
        df = tables[0]
        print("\nColumns:")
        print(df.columns.tolist())
        print("\nFirst 5 rows:")
        print(df.head())
        
        # 尋找 "成交量" 相關欄位
        for col in df.columns:
            if "成交量" in str(col):
                print(f"\nFound Volume Column: {col}")
                # 嘗試加總
                try:
                    total_vol = df[col].astype(str).str.replace(',', '').astype(float).sum()
                    print(f"Total Volume for {col}: {total_vol}")
                except:
                    print("Could not sum column")
                    
except Exception as e:
    print(f"Error: {e}")
