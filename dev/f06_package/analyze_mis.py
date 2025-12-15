"""
檢查 MIS VolatilityQuotes 頁面是否有 API 端點
"""
import requests
import re
from urllib.parse import urljoin

url = 'https://mis.taifex.com.tw/futures/VolatilityQuotes/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print('=' * 60)
print('分析 MIS VolatilityQuotes 頁面')
print('=' * 60)

try:
    print(f'\n1. 訪問頁面: {url}')
    resp = requests.get(url, headers=headers, timeout=10)
    print(f'   狀態碼: {resp.status_code}')
    print(f'   內容大小: {len(resp.text)} 字節')
    
    # 尋找 API/數據源相關信息
    text_lower = resp.text.lower()
    
    # 尋找常見的 API 端點模式
    print('\n2. 尋找 API 端點...')
    api_patterns = [
        r'/api/[^\'\"<>\s]+',
        r'/data/[^\'\"<>\s]+',
        r'/ajax/[^\'\"<>\s]+',
        r'/service/[^\'\"<>\s]+',
        r'https?://[^\'\"<>\s]+/.*quote',
        r'https?://[^\'\"<>\s]+/.*volatil',
    ]
    
    found_apis = set()
    for pattern in api_patterns:
        matches = re.findall(pattern, resp.text, re.IGNORECASE)
        found_apis.update(matches)
    
    if found_apis:
        print(f'   找到 {len(found_apis)} 個潛在 API 端點:')
        for api in sorted(found_apis)[:15]:
            print(f'   - {api}')
    else:
        print('   未找到常見 API 端點')
    
    # 尋找 JavaScript 文件
    print('\n3. 尋找 JavaScript 文件...')
    js_patterns = re.findall(r'<script[^>]*src=[\'"]([^\'"]+)[\'"]', resp.text)
    print(f'   找到 {len(js_patterns)} 個 JavaScript 文件:')
    for js in js_patterns[:10]:
        print(f'   - {js}')
    
    # 尋找包含「波動」或「volatility」的內容
    print('\n4. 尋找波動率相關內容...')
    if '波動' in resp.text:
        print('   ✓ 找到「波動」關鍵詞')
        # 找周圍的上下文
        idx = resp.text.find('波動')
        context = resp.text[max(0, idx-100):min(len(resp.text), idx+100)]
        print(f'   上下文: ...{context}...')
    else:
        print('   ✗ 未找到「波動」關鍵詞')
    
    if 'volatility' in text_lower:
        print('   ✓ 找到「volatility」關鍵詞')
    else:
        print('   ✗ 未找到「volatility」關鍵詞')
    
    # 尋找表格相關標籤
    print('\n5. 檢查頁面結構...')
    table_count = resp.text.count('<table')
    div_count = resp.text.count('<div')
    span_count = resp.text.count('<span')
    print(f'   <table>: {table_count} 個')
    print(f'   <div>: {div_count} 個')
    print(f'   <span>: {span_count} 個')
    
    # 尋找資料容器
    if 'grid' in text_lower or 'table' in text_lower:
        print('   ✓ 頁面可能使用 Grid 或 Table 控制項')
    
    # 檢查是否有隱藏的數據
    print('\n6. 尋找隱藏數據...')
    if '<noscript>' in resp.text:
        print('   ✓ 頁面包含 <noscript> 標籤（JavaScript 依賴）')
    
    if resp.text.count('data-') > 10:
        print(f'   ✓ 頁面有多個 data-* 屬性（共 {resp.text.count("data-")} 個）')
    
    print('\n' + '=' * 60)
    print('結論：')
    print('=' * 60)
    print('MIS VolatilityQuotes 頁面特點:')
    print('- 需要 JavaScript 渲染（表格不在靜態 HTML 中）')
    print('- 使用了多個 JS 文件')
    print('- 可能有隱藏的 API 端點')
    print('\n建議方案:')
    print('1. 使用 Selenium + Chrome 自動化瀏覽器')
    print('2. 點擊確認按鈕後抓取渲染結果')
    print('3. 或者查看 Network 標籤找到 API 端點')
    
except Exception as e:
    print(f'錯誤: {e}')
