#!/usr/bin/env python3
"""
探索 MIS VolatilityQuotes 頁面結構
目的：了解免責聲明後頁面的實際內容和表格結構
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def explore_mis_page():
    """訪問 MIS 頁面並輸出結構信息"""
    
    url = "https://mis.taifex.com.tw/futures/VolatilityQuotes/"
    
    # Chrome 選項配置
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        print("=" * 80)
        print("開始訪問 MIS VolatilityQuotes 頁面")
        print("=" * 80)
        
        driver.get(url)
        time.sleep(3)
        
        # 檢查免責聲明
        print("\n【第 1 步】檢查免責聲明按鈕...")
        try:
            disclaimer_buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"找到 {len(disclaimer_buttons)} 個按鈕")
            for i, btn in enumerate(disclaimer_buttons):
                text = btn.text
                print(f"  [{i}] 文字: '{text}'")
                if "接受" in text or "同意" in text:
                    print(f"      ↓ 點擊此按鈕")
                    btn.click()
                    time.sleep(2)
                    break
        except Exception as e:
            print(f"按鈕探索失敗: {e}")
        
        # 檢查頁面標題
        print("\n【第 2 步】檢查頁面標題和標頭...")
        try:
            title = driver.title
            print(f"頁面標題: {title}")
        except:
            pass
        
        # 檢查確認按鈕
        print("\n【第 3 步】檢查確認按鈕...")
        try:
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"所有按鈕（免責聲明後）:")
            for i, btn in enumerate(all_buttons):
                text = btn.text
                classes = btn.get_attribute("class")
                id_attr = btn.get_attribute("id")
                print(f"  [{i}] 文字: '{text}' | class: '{classes}' | id: '{id_attr}'")
        except Exception as e:
            print(f"按鈕檢查失敗: {e}")
        
        # 檢查表格
        print("\n【第 4 步】檢查表格結構...")
        try:
            tables = driver.find_elements(By.TAG_NAME, "table")
            print(f"找到 {len(tables)} 個表格")
            
            for table_idx, table in enumerate(tables):
                print(f"\n表格 #{table_idx + 1}:")
                # 提取表格 HTML
                table_html = table.get_attribute("outerHTML")
                print(f"表格大小: {len(table_html)} 字節")
                
                # 提取欄位標題
                headers = table.find_elements(By.TAG_NAME, "th")
                print(f"欄位數: {len(headers)}")
                for h_idx, header in enumerate(headers):
                    print(f"  [{h_idx}] {header.text}")
                
                # 提取前 3 行資料
                rows = table.find_elements(By.TAG_NAME, "tr")
                print(f"資料行數: {len(rows)}")
                for r_idx, row in enumerate(rows[:3]):
                    cols = row.find_elements(By.TAG_NAME, "td")
                    values = [col.text for col in cols]
                    print(f"  行 {r_idx}: {values}")
        except Exception as e:
            print(f"表格檢查失敗: {e}")
        
        # 輸出完整 HTML（前 2000 字符）
        print("\n【第 5 步】頁面 HTML（前 2000 字）:")
        print("=" * 80)
        page_html = driver.page_source
        print(page_html[:2000])
        print("...")
        print("=" * 80)
        
    finally:
        driver.quit()
        print("\n瀏覽器已關閉")

if __name__ == "__main__":
    explore_mis_page()
