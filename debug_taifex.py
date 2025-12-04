"""
診斷工具：檢查 TAIFEX 網站的實際請求方式
用於查找正確的日期查詢參數
"""

import requests
import re
from bs4 import BeautifulSoup

def check_taifex_urls():
    """測試多種 URL 格式來找出正確的查詢方式"""
    
    date = "2025-12-02"
    url_date = date.replace('-', '/')
    
    print(f"查詢日期: {date}")
    print("=" * 70)
    
    # 測試各種 URL 格式
    urls = {
        "格式1 (futContractsDate)": f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={url_date}",
        "格式2 (futDailyMarketReport)": f"https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate={url_date}",
        "格式3 (futOtc)": f"https://www.taifex.com.tw/cht/3/futOtc?queryDate={url_date}",
        "格式4 (futDailyMarketReport Post)": "https://www.taifex.com.tw/cht/3/futDailyMarketReport",
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for name, url in list(urls.items())[:-1]:  # 跳過 POST 格式
        try:
            print(f"\n測試: {name}")
            print(f"URL: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            # 檢查返回內容中是否包含查詢日期
            if url_date in response.text:
                print("✓ 找到查詢日期在頁面中")
            elif date in response.text:
                print("✓ 找到查詢日期格式在頁面中")
            else:
                print("✗ 查詢日期未在頁面中找到")
            
            # 檢查是否有表格
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table')
            print(f"  找到 {len(tables)} 個表格")
            
            # 查找日期相關的標籤或輸入框
            date_pattern = r'\d{4}[/-]\d{2}[/-]\d{2}'
            dates_found = re.findall(date_pattern, response.text)
            if dates_found:
                unique_dates = list(set(dates_found))[:3]
                print(f"  頁面中找到的日期: {unique_dates}")
            
        except Exception as e:
            print(f"✗ 連接失敗: {e}")
    
    # 嘗試 POST 請求
    try:
        print(f"\n測試: 格式4 (POST 請求)")
        url = urls["格式4 (futDailyMarketReport Post)"]
        print(f"URL: {url}")
        
        data = {
            'queryDate': url_date,
            'queryDate.x': '0',
            'queryDate.y': '0'
        }
        
        response = requests.post(url, data=data, headers=headers, timeout=10)
        print(f"狀態碼: {response.status_code}")
        
        if url_date in response.text or date in response.text:
            print("✓ 找到查詢日期在返回內容中")
        else:
            print("✗ 查詢日期未在返回內容中找到")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        print(f"  找到 {len(tables)} 個表格")
        
    except Exception as e:
        print(f"✗ POST 請求失敗: {e}")

if __name__ == '__main__':
    check_taifex_urls()
