"""
調試腳本：尋找正確的全球股市頁面
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

print("Starting Chrome...")

# Chrome options
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--start-maximized')

# Start Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Try main wantgoo page
    print("Visiting main wantgoo page...")
    driver.get("https://www.wantgoo.com/")
    time.sleep(5)

    # Look for navigation links related to global markets
    print("\nSearching for navigation links...")
    links = driver.find_elements(By.TAG_NAME, "a")

    potential_links = []
    for link in links:
        href = link.get_attribute("href")
        text = link.text.strip()

        if href and ("global" in href.lower() or "international" in href.lower() or "world" in href.lower()):
            potential_links.append({
                'text': text,
                'href': href
            })
            print(f"  Found: {text} -> {href}")

    # Also search by text
    keywords = ["全球", "國際", "美股", "指數", "夜盤"]
    for keyword in keywords:
        print(f"\nSearching for links with '{keyword}'...")
        elems = driver.find_elements(By.XPATH, f"//a[contains(text(), '{keyword}')]")
        for elem in elems[:5]:
            href = elem.get_attribute("href")
            text = elem.text.strip()
            if href:
                print(f"  {text} -> {href}")

    # Try clicking on a global/international markets link
    print("\n\nTrying to navigate to global markets...")
    try:
        # Look for elements with "國際" or "全球"
        global_link = driver.find_element(By.XPATH, "//a[contains(text(), '國際') or contains(text(), '全球')]")
        href = global_link.get_attribute("href")
        text = global_link.text
        print(f"Clicking: {text} -> {href}")

        global_link.click()
        time.sleep(8)

        # Save screenshot
        driver.save_screenshot("global_markets_page.png")
        print(f"\nScreenshot saved: global_markets_page.png")

        # Check current URL
        current_url = driver.current_url
        print(f"Current URL: {current_url}")

        # Look for table with data
        rows = driver.find_elements(By.TAG_NAME, "tr")
        print(f"Found {len(rows)} table rows")

        # Print some rows
        for i, row in enumerate(rows[:15]):
            text = row.text.strip()
            if text:
                # Encode to bytes then decode, to handle encoding
                try:
                    print(f"Row {i+1}: {text[:100]}")
                except:
                    print(f"Row {i+1}: [encoding issue]")

        # Save HTML
        with open("global_markets.html", 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"\nHTML saved: global_markets.html")

    except Exception as e:
        print(f"Could not navigate to global markets: {e}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    input("\nPress Enter to close browser...")
    driver.quit()
