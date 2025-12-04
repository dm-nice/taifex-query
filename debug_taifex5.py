"""
診斷工具5：嘗試 Selenium 渲染頁面（或尋找 JSON API）
"""

import requests
from bs4 import BeautifulSoup
import json

def try_json_api():
    """嘗試尋找 JSON API"""
    
    date = "2025-11-28"
    url_date = date.replace('-', '/')
    
    print(f"查詢日期: {date}\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.taifex.com.tw/cht/3/futDailyMarketReport',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # 嘗試多個 API 端點
    apis = [
        f"https://www.taifex.com.tw/json/futDailyMarketReport?queryDate={url_date}",
        f"https://www.taifex.com.tw/api/futDailyMarketReport?queryDate={url_date}",
        f"https://www.taifex.com.tw/cht/3/getFutcontract.do?queryDate={url_date}&marketCode=0&commodity_id=TX&ajax=true",
        f"https://www.taifex.com.tw/cht/api/getFutcontract?queryDate={url_date}&marketCode=0&commodity_id=TX",
    ]
    
    for api in apis:
        try:
            print(f"嘗試: {api.split('?')[0]}")
            response = requests.get(api, headers=headers, timeout=5)
            print(f"  狀態碼: {response.status_code}")
            
            # 嘗試解析 JSON
            try:
                data = response.json()
                print(f"  ✓ 成功獲取 JSON 資料!")
                print(f"    數據類型: {type(data)}")
                if isinstance(data, dict):
                    print(f"    鍵: {list(data.keys())[:5]}")
                elif isinstance(data, list):
                    print(f"    列表長度: {len(data)}")
                    if len(data) > 0:
                        print(f"    第一項: {data[0]}")
                break
            except:
                # 嘗試提取 HTML 中的表格
                soup = BeautifulSoup(response.text, 'html.parser')
                tables = soup.find_all('table')
                if tables:
                    print(f"  找到 {len(tables)} 個 HTML 表格")
                    
        except Exception as e:
            print(f"  失敗: {e}")
        
        print()

if __name__ == '__main__':
    try_json_api()
