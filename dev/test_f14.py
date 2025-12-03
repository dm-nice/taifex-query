import requests
import pandas as pd
from datetime import datetime

def test_f14_fetch(date):
    """測試抓取台指期貨收盤價"""
    # URL 格式：需要帶入日期參數
    url = f"https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate={date.replace('-', '/')}"
    
    print(f"Testing URL: {url}")
    resp = requests.get(url, timeout=10)
    resp.encoding = "utf-8"
    
    # 嘗試解析表格
    tables = pd.read_html(resp.text)
    print(f"\n找到 {len(tables)} 個表格")
    
    if len(tables) > 0:
        for i, df in enumerate(tables):
            print(f"\n=== 表格 {i} ===")
            print(f"欄位: {df.columns.tolist()}")
            print(f"形狀: {df.shape}")
            print(df.head())
            
            # 嘗試找到 TX 相關資料
            if '商品代號' in df.columns or '契約' in str(df.columns):
                print("\n可能包含 TX 資料的表格:")
                print(df)

if __name__ == "__main__":
    # 使用今天的日期測試
    test_date = "2025-12-03"
    test_f14_fetch(test_date)
