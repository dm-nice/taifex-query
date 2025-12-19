"""
調試腳本：嘗試與頁面互動以顯示數據
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

url = "https://www.wantgoo.com/global?c=0"

print("Starting Chrome...")

# Chrome options
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
options.add_argument('--start-maximized')

# Start Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    print(f"Visiting: {url}")
    driver.get(url)

    print("Waiting for initial load...")
    time.sleep(5)

    # Try clicking on tabs or buttons to reveal data
    # Look for navigation elements
    try:
        # Find all clickable elements (buttons, tabs, links)
        clickables = driver.find_elements(By.XPATH, "//a | //button | //div[@role='button']")
        print(f"\nFound {len(clickables)} clickable elements")

        # Look for tabs with text containing "國際", "全球", "指數", etc.
        for elem in clickables:
            text = elem.text.strip()
            if text and any(keyword in text for keyword in ["國際", "全球", "指數", "期貨", "夜盤"]):
                print(f"  Clicking: {text}")
                try:
                    elem.click()
                    time.sleep(2)
                    break
                except:
                    pass
    except Exception as e:
        print(f"Error clicking elements: {e}")

    # Wait more time for AJAX
    print("\nWaiting 10 more seconds for data to load...")
    time.sleep(10)

    # Try to find table with data
    print("\nSearching for table rows...")
    rows = driver.find_elements(By.TAG_NAME, "tr")
    print(f"Found {len(rows)} table rows")

    # Print first few rows that have content
    count = 0
    for row in rows:
        text = row.text.strip()
        if text and len(text) > 10:
            print(f"\nRow {count+1}:")
            print(f"  {text[:150]}")
            count += 1
            if count >= 10:
                break

    # Look for div elements with data
    print("\n\nSearching for div elements with numeric data...")
    divs = driver.find_elements(By.XPATH, "//div[contains(text(), ',')]")
    print(f"Found {len(divs)} divs with commas (potential numbers)")

    for div in divs[:20]:
        text = div.text.strip()
        if text:
            print(f"  {text}")

    # Save screenshot
    screenshot_file = "wantgoo_interact.png"
    driver.save_screenshot(screenshot_file)
    print(f"\nScreenshot saved to: {screenshot_file}")

    # Save HTML
    html = driver.page_source
    with open("wantgoo_interact.html", 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"HTML saved to: wantgoo_interact.html ({len(html)} bytes)")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\nClosing browser...")
    driver.quit()
