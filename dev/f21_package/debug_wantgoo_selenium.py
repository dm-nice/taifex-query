"""
調試腳本：使用 Selenium 檢查玩股網頁面結構
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

url = "https://www.wantgoo.com/global?c=0"

print("=== 啟動 Selenium Chrome ===")

# Chrome 選項配置
options = Options()
# options.add_argument('--headless')  # 先不用 headless，方便調試
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')

# 啟動 Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    print(f"訪問頁面: {url}")
    driver.get(url)

    print("等待頁面載入...")
    time.sleep(5)  # 等待 JavaScript 載入

    # 獲取頁面 HTML
    html_source = driver.page_source
    print(f"\n頁面大小: {len(html_source)} 字元")

    # 解析 HTML
    soup = BeautifulSoup(html_source, 'html.parser')

    # 查找表格
    tables = soup.find_all('table')
    print(f"\n找到 {len(tables)} 個表格")

    # 查找包含特定文字的元素
    targets = ['NASDAQ', '費城半導體', 'EM-ND', '台積電ADR', '台指期盤後']

    for target in targets:
        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{target}')]")
        print(f"\n找到 {len(elements)} 個包含 '{target}' 的元素")

        if elements:
            # 嘗試找到父元素 (可能是 tr)
            first_elem = elements[0]
            parent_tr = first_elem.find_element(By.XPATH, "./ancestor::tr[1]")

            # 取得該行所有 td
            tds = parent_tr.find_elements(By.TAG_NAME, "td")
            print(f"  該行有 {len(tds)} 個 td")
            print(f"  內容:")
            for i, td in enumerate(tds):
                text = td.text.strip()
                if text:
                    print(f"    td[{i}]: {text}")

    print("\n=== 嘗試定位 NASDAQ 數據 ===")
    try:
        # 嘗試找到 NASDAQ 行
        nasdaq_row = driver.find_element(By.XPATH, "//tr[contains(., 'NASDAQ')]")
        tds = nasdaq_row.find_elements(By.TAG_NAME, "td")

        print(f"NASDAQ 行包含 {len(tds)} 個欄位:")
        for i, td in enumerate(tds):
            print(f"  [{i}] {td.text.strip()}")
    except Exception as e:
        print(f"無法定位 NASDAQ 行: {e}")

    print("\n=== 完成 ===")

except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n關閉瀏覽器...")
    driver.quit()
