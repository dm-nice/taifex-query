"""
f01_fetcher.py
F1 指標：台指期貨外資及陸資淨口數 (OI)
資料來源：台灣期貨交易所 (TAIFEX)
依照 interface_spec.md 規範設計
"""

def fetch(date: str) -> dict:
    """
    輸入:
        date (str): 日期字串，格式 YYYY-MM-DD
    輸出:
        dict: 統一格式 (成功或失敗)
    """

    try:
        # TODO: 在這裡補上實際爬蟲或 API 抓取邏輯
        # 目前先用假資料測試
        data = {
            "foreign_long": 8000,
            "foreign_short": 6800,
            "foreign_net": 1200,
            "china_long": 1500,
            "china_short": 1700,
            "china_net": -200
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


# 測試用：模組可獨立執行
if __name__ == "__main__":
    result = fetch("2025-11-28")
    print(result)
