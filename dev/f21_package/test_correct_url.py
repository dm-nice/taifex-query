"""
測試正確的 URL - 根據用戶提供的截圖
用戶URL: https://www.wantgoo.com/global?c=0
可能需要嘗試其他 URL 格式
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# 嘗試不同的 URL
urls_to_try = [
    "https://www.wantgoo.com/global",
    "https://www.wantgoo.com/global/indices",
    "https://www.wantgoo.com/global/futures",
    "https://www.wantgoo.com/investtool/world-indices",
    "https://www.wantgoo.com/global-market",
]

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--start-maximized')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    for url in urls_to_try:
        print(f"\n{'='*60}")
        print(f"Testing URL: {url}")
        print('='*60)

        driver.get(url)
        time.sleep(8)

        # Look for specific text: NASDAQ, 費城半導體, etc.
        targets = ['NASDAQ', 'Nasdaq', '費城半導體', 'EM-ND', '台積電ADR', '台指期']

        found_any = False
        for target in targets:
            try:
                elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{target}')]")
                if elements:
                    print(f"  ✓ Found '{target}' ({len(elements)} elements)")
                    found_any = True

                    # Try to get parent row
                    elem = elements[0]
                    try:
                        row = elem.find_element(By.XPATH, "./ancestor::tr[1]")
                        print(f"    Row text: {row.text[:100]}")
                    except:
                        print(f"    Element text: {elem.text[:100]}")
            except Exception as e:
                pass

        if found_any:
            print(f"\n  *** THIS URL HAS DATA! ***")
            print(f"  Correct URL: {url}")

            # Save screenshot
            screenshot = f"found_data_{url.split('/')[-1]}.png"
            driver.save_screenshot(screenshot)
            print(f"  Screenshot: {screenshot}")

            # Save HTML
            html_file = f"found_data_{url.split('/')[-1]}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print(f"  HTML: {html_file}")

            break
        else:
            print("  ✗ No target data found")

        time.sleep(2)

except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\nClosing browser...")
    driver.quit()
