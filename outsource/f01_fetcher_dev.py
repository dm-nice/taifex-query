"""
f01_fetcher.py
F1 指標：台指期貨外資及陸資淨口數 (OI)
資料來源：台灣期貨交易所 (TAIFEX)
依照 interface_spec.md 規範設計
"""

import requests
import pandas as pd
from io import StringIO

def fetch(date: str) -> dict:
    """
    輸入: date (str): 日期字串，格式 YYYY-MM-DD
    輸出: dict: 統一格式 (成功或失敗)
    """
    try:
        # TAIFEX 外資/陸資 OI 資料網址 (每日 CSV)
        url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={date.replace('-', '/')}"
        resp = requests.get(url)
        resp.encoding = "utf-8"

        # 轉成 DataFrame
        df = pd.read_html(resp.text)[0]

        # 篩選外資與陸資
        foreign = df[df["交易人名稱"] == "外資"]
        china   = df[df["交易人名稱"] == "陸資"]

        data = {
            "foreign_long": int(foreign["多單口數"].values[0]),
            "foreign_short": int(foreign["空單口數"].values[0]),
            "foreign_net": int(foreign["多空淨額"].values[0]),
            "china_long": int(china["多單口數"].values[0]),
            "china_short": int(china["空單口數"].values[0]),
            "china_net": int(china["多空淨額"].values[0]),
        }

        return {
            "module": "f01",
            "date": date,
            "status": "success",
            "data": data,
        }

    except Exception as e:
        return {
            "module": "f01",
            "date": date,
            "status": "fail",
            "error": str(e),
        }

if __name__ == "__main__":
    result = fetch("2025-11-28")
    print(result)
