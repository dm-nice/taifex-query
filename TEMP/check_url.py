"""
診斷：直接檢查 URL 返回的實際日期
"""

import requests
from bs4 import BeautifulSoup
import re

date = "2025-12-01"
url_date = date.replace('-', '/')

url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={url_date}"

print(f"查詢日期: {date}")
print(f"URL: {url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=10)
response.encoding = 'utf-8'

# 找出頁面中所有的日期
date_pattern = r'202[45]/\d{2}/\d{2}'
dates = set(re.findall(date_pattern, response.text))

print(f"頁面中找到的日期:")
for d in sorted(dates):
    print(f"  - {d}")

# 查找表格
soup = BeautifulSoup(response.text, 'html.parser')
tables = soup.find_all('table')
print(f"\n找到 {len(tables)} 個表格")

# 如果找到表格，檢查第一行
if tables:
    import pandas as pd
    try:
        df = pd.read_html(str(tables[0]))[0]
        print(f"\n第一個表格的內容:")
        print(df.head())
    except:
        print("無法解析表格")
