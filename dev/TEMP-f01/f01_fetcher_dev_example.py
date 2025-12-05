"""
===========================================================
 f01_fetcher_dev_example.py  —  外包商模組範例
===========================================================

【用途】
- 提供外資期貨口數資料，回傳 dict 給 run.py
- 必須符合 run.py 的驗收規範，包含 status、module、source、data 欄位

【規範】
- 必須定義 fetch(date: str) → dict
- 回傳格式：
  {
    "status": "success" / "fail" / "error" / "invalid",
    "module": "f01",
    "source": "TAIFEX",
    "data": {
      "外資多方口數": int 或 "-",
      "外資空方口數": int 或 "-",
      "外資多空淨額": int 或 "-"
    }
  }

【範例】
  >>> from dev.f01_fetcher_dev_example import fetch
  >>> fetch("2025-12-01")
===========================================================
"""

import requests
from bs4 import BeautifulSoup

def fetch(date: str) -> dict:
    try:
        # 模擬抓取 TAIFEX 網頁資料
        # 注意：外包商需依照實際網頁結構撰寫
        url = f"https://www.taifex.com.tw/example?date={date}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # 假設網頁表格有三個欄位
        long_val = soup.find("td", {"id": "long"}).text.strip()
        short_val = soup.find("td", {"id": "short"}).text.strip()
        net_val = soup.find("td", {"id": "net"}).text.strip()

        # 整理成 dict
        data = {
            "外資多方口數": int(long_val.replace(",", "")) if long_val else "-",
            "外資空方口數": int(short_val.replace(",", "")) if short_val else "-",
            "外資多空淨額": int(net_val.replace(",", "")) if net_val else "-"
        }

        return {
            "status": "success",
            "module": "f01",
            "source": "TAIFEX",
            "data": data
        }

    except Exception as e:
        # 錯誤處理：仍需回傳 dict
        return {
            "status": "error",
            "module": "f01",
            "source": "TAIFEX",
            "data": {
                "外資多方口數": "-",
                "外資空方口數": "-",
                "外資多空淨額": "-"
            },
            "error": str(e)
        }