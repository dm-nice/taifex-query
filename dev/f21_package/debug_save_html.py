"""
調試腳本：保存頁面 HTML 以供檢查
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

url = "https://www.wantgoo.com/global?c=0"

print("Starting Selenium Chrome...")

# Chrome options
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')

# Start Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    print(f"Visiting: {url}")
    driver.get(url)

    print("Waiting for page to load...")
    time.sleep(8)  # Wait longer for JavaScript

    # Get page HTML
    html_source = driver.page_source

    # Save to file
    output_file = "wantgoo_page.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_source)

    print(f"HTML saved to: {output_file}")
    print(f"File size: {len(html_source)} bytes")

    # Also save a screenshot
    screenshot_file = "wantgoo_screenshot.png"
    driver.save_screenshot(screenshot_file)
    print(f"Screenshot saved to: {screenshot_file}")

    print("Done!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("Closing browser...")
    driver.quit()
