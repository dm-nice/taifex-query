"""
診斷工具2：檢查 TAIFEX 返回的表格內容
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup

def check_table_content():
    """檢查返回的表格內容"""
    
    date = "2025-11-28"
    url_date = date.replace('-', '/')
    url = f"https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate={url_date}"
    
    print(f"查詢日期: {date}")
    print(f"URL: {url}")
    print("=" * 70)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    
    # 直接使用 pandas 讀取所有表格
    try:
        tables = pd.read_html(response.text)
        print(f"使用 pd.read_html 找到 {len(tables)} 個表格\n")
        
        for idx, df in enumerate(tables):
            print(f"表格 {idx + 1}:")
            print("-" * 70)
            print(f"表格形狀: {df.shape}")
            print(f"欄位: {df.columns.tolist()[:10]}")  # 顯示前 10 個欄位
            print(f"\n前 3 行:")
            print(df.head(3))
            print()
            
    except Exception as e:
        print(f"pd.read_html 失敗: {e}")

if __name__ == '__main__':
    check_table_content()
