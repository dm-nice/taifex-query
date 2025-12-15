"""
探索 TAIFEX MIS VolatilityQuotes 頁面結構
目標：找出波動率指數的 HTML 元素和確認按鈕位置
"""
# -*- coding: utf-8 -*-
import sys
import os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Chrome 選項
chrome_options = Options()
chrome_options.add_argument('--start-maximized')
# chrome_options.add_argument('--headless')  # 無頭模式（暫不使用，便於觀察）
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

# 啟動 Chrome
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

print("=" * 60)
print("探索 MIS VolatilityQuotes 頁面")
print("=" * 60)

try:
    # 訪問 MIS 頁面
    url = "https://mis.taifex.com.tw/futures/VolatilityQuotes/"
    print(f"\n1️⃣ 訪問頁面: {url}")
    driver.get(url)
    
    # 等待頁面加載
    print("2️⃣ 等待頁面加載...")
    time.sleep(3)
    
    # 查找確認按鈕
    print("3️⃣ 尋找確認按鈕...")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"   找到 {len(buttons)} 個按鈕")
    for i, btn in enumerate(buttons):
        print(f"   - 按鈕 {i}: {btn.get_attribute('id')} | {btn.text}")
    
    # 查找表格
    print("\n4️⃣ 尋找表格元素...")
    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"   找到 {len(tables)} 個表格")
    
    # 查找包含波動率的 div/span
    print("\n5️⃣ 尋找包含 '波動率' 或 'Volatility' 的元素...")
    all_text = driver.find_element(By.TAG_NAME, "body").text
    if '波動率' in all_text:
        print("   ✓ 找到 '波動率'")
        # 找到具體元素
        elements = driver.find_elements(By.XPATH, "//*[contains(text(), '波動率')]")
        print(f"   找到 {len(elements)} 個包含 '波動率' 的元素")
        for i, elem in enumerate(elements[:5]):
            print(f"   - 元素 {i}: {elem.tag_name} | {elem.text[:50]}")
    
    # 查找可能的波動率數值
    print("\n6️⃣ 尋找數值元素...")
    # 查找可能包含波動率數值的 span/div
    spans = driver.find_elements(By.TAG_NAME, "span")
    print(f"   找到 {len(spans)} 個 span 元素")
    
    # 打印前 20 個非空的 span
    count = 0
    for span in spans:
        text = span.text.strip()
        if text and not text.isspace() and len(text) < 50:
            print(f"   - {text}")
            count += 1
            if count >= 20:
                break
    
    # 查看頁面源碼中的關鍵字
    print("\n7️⃣ 檢查源碼中的關鍵詞...")
    page_source = driver.page_source
    
    keywords = ['volatility', 'vix', 'quote', 'confirm', 'button', '確認', '波動', '指數']
    for keyword in keywords:
        count = page_source.lower().count(keyword)
        if count > 0:
            print(f"   - '{keyword}': 出現 {count} 次")
    
    # 嘗試點擊確認按鈕（如果有）
    print("\n8️⃣ 檢查是否需要點擊確認按鈕...")
    try:
        # 尋找中文的「確認」按鈕
        confirm_btn = driver.find_element(By.XPATH, "//button[contains(text(), '確認')]")
        print(f"   ✓ 找到確認按鈕: {confirm_btn.text}")
        print("   → 嘗試點擊...")
        confirm_btn.click()
        time.sleep(2)
        print("   ✓ 點擊成功，等待數據加載...")
    except:
        print("   ✗ 未找到確認按鈕")
    
    # 再次查找表格
    print("\n9️⃣ 再次檢查表格...")
    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"   找到 {len(tables)} 個表格")
    
    if len(tables) > 0:
        print("\n   第一個表格內容:")
        table_html = tables[0].get_attribute("outerHTML")
        print(f"   HTML 長度: {len(table_html)}")
        print(f"   前 500 字:\n{table_html[:500]}")
    
    # 列出頁面中的所有文本內容（簡化）
    print("\n🔟 頁面主要內容:")
    body_text = driver.find_element(By.TAG_NAME, "body").text
    lines = body_text.split('\n')
    for i, line in enumerate(lines[:30]):
        print(f"   {i}: {line[:80]}")
    
    print("\n" + "=" * 60)
    print("✅ 探索完成")
    print("=" * 60)
    
    # 自動關閉（移除 input() 提示）
    print("\n✅ 探索完成，自動關閉瀏覽器...")
    time.sleep(1)

finally:
    driver.quit()
    print("\n瀏覽器已關閉")
