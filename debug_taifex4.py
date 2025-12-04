"""
診斷工具4：找出 AJAX 請求的實際 API 端點
"""

import requests
import re

def check_ajax_endpoint():
    """找出 AJAX 請求的實際端點"""
    
    date = "2025-11-28"
    url_date = date.replace('-', '/')
    url = f"https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate={url_date}"
    
    print(f"查詢日期: {date}")
    print(f"URL: {url}\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.taifex.com.tw/cht/3/futDailyMarketReport'
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'
    
    # 尋找 getFutcontract 端點
    matches = re.findall(r'(\w+\.do|\.json|\.action)\?[^"<>]*', response.text)
    print("找到的端點:")
    for match in set(matches):
        print(f"  - {match}")
    
    # 尋找 queryDate 相關參數
    print("\n可能的 API 請求方式:")
    if 'getFutcontract.do' in response.text:
        print("  ✓ 找到 getFutcontract.do")
        
        # 測試 API 端點
        api_url = f"https://www.taifex.com.tw/cht/3/getFutcontract.do?queryDate={url_date}&marketCode=0&commodity_id=TX"
        print(f"\n嘗試 API 端點: {api_url}")
        
        try:
            api_response = requests.get(api_url, headers=headers, timeout=10)
            print(f"狀態碼: {api_response.status_code}")
            print(f"返回內容長度: {len(api_response.text)}")
            print(f"內容類型: {api_response.headers.get('Content-Type', '不詳')}")
            print(f"\n前 500 字元:")
            print(api_response.text[:500])
        except Exception as e:
            print(f"失敗: {e}")

if __name__ == '__main__':
    check_ajax_endpoint()
