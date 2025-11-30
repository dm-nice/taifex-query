"""
F1 模組需求
- 指標名稱：台指期貨外資淨口數 (Open Interest, OI)
- 資料來源：台灣期貨交易所 (TAIFEX) 官方網站
- 需抓取欄位：外資淨口數
- 輸入：date (YYYY-MM-DD)
- 輸出：dict 格式，符合 interface_spec.md 規範

---

成功輸出範例：
{
    "module": "f01",
    "date": "YYYY-MM-DD",
    "status": "success",
    "summary": "F1: 台指期貨外資淨口數 (OI): [請填入數值]（來源：TAIFEX）"
}

---

錯誤回報格式規範（外包程式失敗時）：

基本格式：
{
    "module": "f01",
    "date": "YYYY-MM-DD",
    "status": "fail",
    "error": "錯誤訊息"
}

錯誤訊息撰寫建議：
- 欄位不存在：
  "找不到欄位 '外資淨口數'"
- 網頁結構異常：
  "TAIFEX 網頁表格解析失敗，無法取得第一個表格"
- 無資料可抓取：
  "該日無交易資料，TAIFEX 回傳空表格"


"""

import requests
import pandas as pd

def fetch(date: str) -> dict:
    """
    輸入: date (str): 日期字串，格式 YYYY-MM-DD
    輸出: dict: 統一格式 (成功或失敗)
    """
    try:
        # TAIFEX 外資 OI 資料網址 (每日報表)
        url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={date.replace('-', '/')}"
        resp = requests.get(url)
        resp.encoding = "utf-8"

        # 轉成 DataFrame
        df = pd.read_html(resp.text)[0]

        # 確認欄位名稱
        trader_col = None
        for col in ["交易人名稱", "交易人", "交易人代號"]:
            if col in df.columns:
                trader_col = col
                break
        if trader_col is None:
            raise ValueError(f"找不到交易人欄位，df.columns = {list(df.columns)}")

        # 篩選外資
        foreign = df[df[trader_col] == "外資"]

        # 數值轉換工具
        def to_int(val):
            return int(str(val).replace(",", "").strip())

        # 確認數值欄位
        long_col = None
        for col in ["多單口數", "多方未平倉口數"]:
            if col in df.columns:
                long_col = col
                break
        short_col = None
        for col in ["空單口數", "空方未平倉口數"]:
            if col in df.columns:
                short_col = col
                break
        if long_col is None or short_col is None:
            raise ValueError(f"找不到多單/空單欄位，df.columns = {list(df.columns)}")

        foreign_long = to_int(foreign[long_col].values[0])
        foreign_short = to_int(foreign[short_col].values[0])
        foreign_net = foreign_long - foreign_short

        # 組合輸出
        summary = f"F1: 台指期貨外資淨口數 (OI): {foreign_net}（來源：TAIFEX）"

        return {
            "module": "f01",
            "date": date,
            "status": "success",
            "summary": summary
        }

    except Exception as e:
        return {
            "module": "f01",
            "date": date,
            "status": "fail",
            "error": str(e)
        }

if __name__ == "__main__":
    result = fetch("2025-11-28")
    print(result)


