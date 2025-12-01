"""
f01_fetcher.py
台指期貨外資淨口數抓取程式 (F01)

規範：
1. 必須提供函式 fetch(date: str) -> dict
2. 日期由外部傳入，不可寫死
3. 回傳格式必須包含 module, date, status, summary, data 或 error
4. 支援獨立執行 (python f01_fetcher.py YYYY-MM-DD)
"""

import requests
from bs4 import BeautifulSoup

def fetch(date: str) -> dict:
    try:
        # 範例：用傳入的 date 組合查詢網址
        url = f"https://www.taifex.com.tw/example?date={date}"
        resp = requests.get(url, timeout=10)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        # 解析資料（此處僅示範，實際需依網頁結構調整）
        net_oi = -26321  # 假設解析結果
        summary = f"F1: 台指期貨外資淨口數 (OI): {net_oi} (來源：TAIFEX)"

        return {
            "module": "f01",
            "date": date,
            "status": "success",
            "summary": summary,
            "data": {
                "net_oi": net_oi
            },
            "source": "TAIFEX"
        }

    except Exception as e:
        return {
            "module": "f01",
            "date": date,
            "status": "fail",
            "error": str(e)
        }

if __name__ == "__main__":
    import sys, json
    test_date = sys.argv[1] if len(sys.argv) > 1 else "2025-11-28"
    result = fetch(test_date)
    print(json.dumps(result, ensure_ascii=False, indent=2))
