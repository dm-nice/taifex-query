"""
診斷工具3：檢查頁面原始內容
"""

import requests

def check_page_content():
    """檢查頁面原始內容"""
    
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
    
    # 檢查頁面內容
    print(f"狀態碼: {response.status_code}")
    print(f"頁面大小: {len(response.text)} 字元")
    print(f"包含 'table': {('table' in response.text.lower())}")
    print(f"包含 'TX': {('TX' in response.text)}")
    print(f"包含 '台指': {('台指' in response.text)}")
    print(f"包含 查詢日期 '{url_date}': {(url_date in response.text)}")
    
    # 顯示頁面片段
    print("\n" + "=" * 70)
    print("頁面片段（前 1000 字元）:")
    print("=" * 70)
    print(response.text[:1000])
    
    # 查找 TX 相關的內容
    if 'TX' in response.text:
        idx = response.text.find('TX')
        print("\n找到 TX，上下文:")
        print(response.text[max(0, idx-100):idx+200])

if __name__ == '__main__':
    check_page_content()
