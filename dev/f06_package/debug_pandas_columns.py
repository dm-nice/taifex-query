#!/usr/bin/env python3
"""
調試 pandas read_html 的欄位名稱
"""

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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
    print("訪問 MIS 頁面...")
    driver.get(url)
    time.sleep(3)
    
    # 點擊免責聲明
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if "接受" in btn.text:
                btn.click()
                time.sleep(2)
                break
    except:
        pass
    
    time.sleep(1)
    
    # 取得 HTML
    page_html = driver.page_source
    
    # 使用 pd.read_html
    print("\n使用 pd.read_html 解析...")
    try:
        tables = pd.read_html(page_html)
        print(f"找到 {len(tables)} 個表格\n")
        
        for idx, df in enumerate(tables):
            print(f"表格 #{idx + 1}:")
            print(f"  形狀: {df.shape}")
            print(f"  欄位: {list(df.columns)}")
            print(f"  欄位類型: {df.dtypes.to_dict()}")
            print(f"  第一行:")
            print(df.iloc[0] if len(df) > 0 else "無數據")
            print()
            
    except Exception as e:
        print(f"pd.read_html 失敗: {e}")
    
finally:
    driver.quit()
