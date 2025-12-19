"""
調試腳本：檢查玩股網頁面結構和數據來源
"""
import requests
from bs4 import BeautifulSoup

url = "https://www.wantgoo.com/global?c=0"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print("=== 測試 1: 嘗試直接 HTTP 請求 ===")
response = requests.get(url, headers=headers, timeout=30)
response.encoding = "utf-8"

print(f"HTTP 狀態碼: {response.status_code}")
print(f"內容長度: {len(response.text)} 字元")

# 解析 HTML
soup = BeautifulSoup(response.text, 'html.parser')

# 查找表格
tables = soup.find_all('table')
print(f"\n找到 {len(tables)} 個表格")

# 查找包含 "NASDAQ" 的元素
nasdaq_elements = soup.find_all(text=lambda t: 'NASDAQ' in str(t) if t else False)
print(f"\n找到 {len(nasdaq_elements)} 個包含 'NASDAQ' 的元素")

if nasdaq_elements:
    print("前 3 個 NASDAQ 元素:")
    for elem in nasdaq_elements[:3]:
        print(f"  - {elem}")

# 查找所有 script 標籤（可能有 API 調用）
scripts = soup.find_all('script')
print(f"\n找到 {len(scripts)} 個 script 標籤")

# 檢查是否有 AJAX API 調用
api_keywords = ['api', 'ajax', 'data', 'json']
for script in scripts:
    script_text = script.string
    if script_text:
        for keyword in api_keywords:
            if keyword in script_text.lower():
                print(f"\n找到可能的 API 調用 (關鍵字: {keyword}):")
                # 只顯示前 200 個字元
                snippet = script_text[:200].replace('\n', ' ')
                print(f"  {snippet}...")
                break

print("\n=== 結論 ===")
if len(tables) == 0 and len(nasdaq_elements) == 0:
    print("❌ HTTP 直接請求無法取得數據")
    print("✅ 需要使用 Selenium（JavaScript 動態載入）")
else:
    print("✅ HTTP 直接請求可能可行")
    print("ℹ️  建議先嘗試 Selenium 確保穩定性")
