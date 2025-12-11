
import requests
import pandas as pd
from datetime import datetime

# 測試日期 (最近交易日)
DATE = "2025/12/10"

# 嘗試: 波動率指數 (VIX)
# URL 可能需要調整，先試試看常見的歷史資料查詢端點
# 根據經驗，可能是: https://www.taifex.com.tw/cht/7/vixHistoryDates
# 或者 queryDate 參數
URL_VIX = f"https://www.taifex.com.tw/cht/7/vixHistoryDates?queryDate={DATE}&queryType=1"

print(f"Testing URL: {URL_VIX}")

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    urls_to_test = [
        "https://www.taifex.com.tw/cht/7/vixHistory",
        "https://www.taifex.com.tw/cht/7/vixHistoryDates",  # Might need GET
        "https://www.taifex.com.tw/cht/7/vix",
        "https://www.taifex.com.tw/cht/7/vixMinNew"
    ]

    for url in urls_to_test:
        print(f"\nScanning: {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                if "<table" in resp.text.lower():
                    print("✅ Found table!")
                    try:
                        dfs = pd.read_html(resp.text, flavor='lxml')
                        print(f"Tables count: {len(dfs)}")
                        if len(dfs) > 0:
                            print(dfs[0].head())
                    except:
                        pass
                else:
                    print("No table.")
        except Exception as e:
            print(f"Error: {e}")
        
except Exception as e:
    print(f"Error: {e}")
