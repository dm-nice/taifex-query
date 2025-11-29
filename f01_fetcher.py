"""
f01_fetcher.py
F1 指標抓取程式範例
依照 interface_spec.md 規範設計
"""

import random

def fetch(date: str) -> dict:
    """
    輸入:
        date (str): 日期字串，格式 YYYY-MM-DD
    輸出:
        dict: 統一格式 (成功或失敗)
    """

    try:
        # 模擬抓取資料 (實際上這裡應該是 requests / API / Selenium 等)
        # 這裡先用隨機數字假裝抓到資料
        data = {
            "open": random.randint(15000, 16000),
            "close": random.randint(15000, 16000),
            "volume": random.randint(1000, 5000),
        }

        return {
            "module": "f01",
            "date": date,
            "status": "success",
            "data": data,
        }

    except Exception as e:
        # 若失敗，回傳錯誤格式
        return {
            "module": "f01",
            "date": date,
            "status": "fail",
            "error": str(e),
        }


# 測試用：模組可獨立執行
if __name__ == "__main__":
    result = fetch("2025-11-29")
    print(result)
