"""
調試腳本：尋找動態載入的數據
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

url = "https://www.wantgoo.com/global?c=0"

print("Starting Chrome with network logging...")

# Chrome options
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# Enable Performance Logging
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

# Start Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    print(f"Visiting: {url}")
    driver.get(url)

    print("Waiting 10 seconds for AJAX to complete...")
    time.sleep(10)

    # Get performance logs to find network requests
    logs = driver.get_log('performance')

    print(f"\nFound {len(logs)} network events")

    # Filter for XHR/Fetch requests
    xhr_requests = []
    for log in logs:
        message = json.loads(log['message'])['message']

        if message['method'] == 'Network.responseReceived':
            response = message['params']['response']
            url_response = response['url']

            # Look for API endpoints
            if 'api' in url_response.lower() or 'data' in url_response.lower() or 'json' in url_response.lower():
                xhr_requests.append({
                    'url': url_response,
                    'status': response['status'],
                    'mimeType': response.get('mimeType', 'unknown')
                })

    print(f"\nFound {len(xhr_requests)} potential API requests:")
    for req in xhr_requests[:10]:
        print(f"  - {req['url']}")
        print(f"    Status: {req['status']}, Type: {req['mimeType']}")

    # Try to find elements with specific class names or IDs
    print("\n\nSearching for data elements by class/id...")

    # Common patterns for financial data tables
    patterns = [
        "quote", "stock", "market", "index", "price",
        "data-table", "global", "futures"
    ]

    for pattern in patterns:
        try:
            elements = driver.find_elements(By.XPATH, f"//*[contains(@class, '{pattern}') or contains(@id, '{pattern}')]")
            if elements:
                print(f"  Found {len(elements)} elements with '{pattern}'")
                if len(elements) <= 5:
                    for elem in elements:
                        text = elem.text.strip()[:100]
                        if text:
                            print(f"    - {text}")
        except:
            pass

    # Try to find any table
    print("\n\nSearching for tables...")
    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"Found {len(tables)} tables")

    for i, table in enumerate(tables):
        text = table.text.strip()
        if text and len(text) > 20:
            print(f"\nTable {i+1} (first 200 chars):")
            print(text[:200])

    # Save final HTML
    final_html = driver.page_source
    with open("wantgoo_final.html", 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"\nFinal HTML saved to: wantgoo_final.html ({len(final_html)} bytes)")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\nClosing browser...")
    driver.quit()
