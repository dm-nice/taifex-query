"""
簡化測試腳本
"""
import sys
import io
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Fix encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# URLs to test
urls = [
    "https://www.wantgoo.com/global",
    "https://www.wantgoo.com/investtool/world-indices",
]

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    for url in urls:
        print(f"\nTesting: {url}")
        driver.get(url)
        time.sleep(10)

        # Search for NASDAQ
        try:
            elem = driver.find_element(By.XPATH, "//*[contains(text(), 'NASDAQ') or contains(text(), 'Nasdaq')]")
            print(f"FOUND DATA at: {url}")
            row = elem.find_element(By.XPATH, "./ancestor::tr[1]")
            print(f"Row: {row.text}")

            driver.save_screenshot(f"success.png")
            break
        except:
            print("No data found")

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()
