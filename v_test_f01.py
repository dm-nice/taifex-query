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
        # 1. 組成目標 URL
        # 根據輸入的日期，產生對應的期交所查詢網址
        url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={date.replace('-', '/')}"
        
        # 2. 發送 HTTP 請求並取得網頁內容
        resp = requests.get(url)
        resp.encoding = "utf-8" # 設定正確的編碼以避免亂碼

        # 3. 使用 pandas 解析 HTML 表格
        # pd.read_html 會自動抓取網頁中所有的表格，並回傳一個 DataFrame 的 list
        # 根據期交所網頁結構，我們需要的資料在第一個表格中
        df = pd.read_html(resp.text)[0]

        # 4. 彈性尋找欄位名稱
        # 為了應對網站未來可能修改欄位名稱的情況，我們用一個列表來儲存可能的欄位名稱
        trader_col = None
        possible_trader_cols = ["交易人名稱", "交易人", "交易人代號"]
        for col in possible_trader_cols:
            if col in df.columns:
                trader_col = col
                break
        if trader_col is None:
            raise ValueError(f"找不到交易人欄位，目前網頁上的欄位為: {list(df.columns)}")

        # 5. 篩選出「外資」的資料
        foreign_df = df[df[trader_col] == "外資"]
        if foreign_df.empty:
            raise ValueError("在表格中找不到 '外資' 的資料列")

        # 6. 數值轉換與欄位確認
        # 定義一個內部函數，用來將字串格式的數字（如 "1,234"）轉換為整數
        def to_int(val):
            return int(str(val).replace(",", "").strip())

        # 同樣彈性地尋找「多單」與「空單」的欄位
        long_col, short_col = None, None
        possible_long_cols = ["多單口數", "多方未平倉口數"]
        possible_short_cols = ["空單口數", "空方未平倉口數"]

        for col in possible_long_cols:
            if col in df.columns:
                long_col = col
                break
        
        for col in possible_short_cols:
            if col in df.columns:
                short_col = col
                break

        if long_col is None or short_col is None:
            raise ValueError(f"找不到多單或空單欄位，目前網頁上的欄位為: {list(df.columns)}")

        # 7. 取得外資多空單口數並計算淨口數
        foreign_long = to_int(foreign_df[long_col].values[0])
        foreign_short = to_int(foreign_df[short_col].values[0])
        foreign_net = foreign_long - foreign_short

        # 8. 組合成功時的輸出訊息
        summary = f"F1: 台指期貨外資淨口數 (OI): {foreign_net}（來源：TAIFEX）"

        return {
            "module": "f01",
            "date": date,
            "status": "success",
            "summary": summary
        }

    except Exception as e:
        # 9. 處理所有可能的錯誤
        # 如果在 try 區塊中發生任何錯誤（如網路問題、解析失敗、找不到欄位等），
        # 就會執行這裡的程式碼，並回傳統一的錯誤格式
        return {
            "module": "f01",
            "date": date,
            "status": "fail",
            "error": str(e)
        }

# 當這個 .py 檔案被直接執行時，會執行以下區塊，方便進行單獨測試
if __name__ == "__main__":
    # 測試抓取 2025-11-28 的資料
    result = fetch("2025-11-28")
    print(result)

