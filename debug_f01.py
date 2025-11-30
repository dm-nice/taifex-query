"""
調試 F01 fetcher - 查看實際 HTML 結構
"""

import requests
import pandas as pd

def debug_f01():
    """調試 TAIFEX HTML 結構"""
    date = "2025-11-28"
    url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={date.replace('-', '/')}"
    
    print(f"URL: {url}")
    print("=" * 70)
    
    resp = requests.get(url)
    resp.encoding = "utf-8"
    
    # 取得所有表格
    tables = pd.read_html(resp.text)
    print(f"找到 {len(tables)} 個表格\n")
    
    for i, df in enumerate(tables):
        print(f"表格 {i}:")
        print(f"  形狀: {df.shape}")
        print(f"  欄位: {list(df.columns)}")
        print(f"  資料預覽:")
        print(df.head(10))
        print("\n" + "-" * 70 + "\n")

if __name__ == "__main__":
    debug_f01()
