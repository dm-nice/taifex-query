"""
F01 模組：台指期貨外資淨口數 (OI) 抓取程式
來源：台灣期貨交易所 (TAIFEX) 每日報表
功能：依據日期抓取外資於台指期貨的未平倉淨口數。
"""
import requests
import pandas as pd
from typing import Dict, Any

def fetch(date: str) -> Dict[str, Any]:
    """
    抓取指定日期的台指期貨外資淨口數 (OI)。

    輸入:
        date (str): 日期字串，格式 YYYY-MM-DD
    輸出:
        dict: 統一格式 (成功或失敗)
    """
    module_code = "f01"
    
    # 根據 TAIFEX 網址格式，將 YYYY-MM-DD 轉為 YYYY/MM/DD
    taifex_date = date.replace('-', '/') 

    try:
        # 1. 網路請求
        # queryType=1 (依日期查詢), marketCode=0 (期貨), date={YYYY/MM/DD}
        url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={taifex_date}"
        
        # 設定 headers 模擬瀏覽器，防止某些網站拒絕 requests 請求
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        resp = requests.get(url, headers=headers)
        resp.encoding = "utf-8"
        
        # 確認網頁是否成功回應
        if resp.status_code != 200:
            raise requests.exceptions.RequestException(f"網路請求失敗，HTTP 狀態碼: {resp.status_code}")

        # 2. 資料解析
        # 嘗試讀取網頁中的第一個 HTML 表格
        try:
            df_list = pd.read_html(resp.text)
            if not df_list:
                # 網頁內容可能無表格，或該日無交易資料
                # 檢查網頁文字是否包含 "該條件查無資料"
                if "該條件查無資料" in resp.text:
                    raise ValueError(f"該日 ({date}) 無交易資料，TAIFEX 回傳查無資料")
                else:
                    raise ValueError("TAIFEX 網頁解析失敗，無法取得任何表格 (可能網頁結構改變)")
            
            # 期交所的資料通常在第一個表格
            df = df_list[0]
            
        except Exception as e:
             # 處理 read_html 可能拋出的錯誤
             raise ValueError(f"網頁表格解析失敗：{str(e)}")


        # 3. 欄位確認與篩選
        
        # 確認交易人欄位 (可能名稱有異動)
        trader_cols = ["交易人名稱", "交易人"]
        trader_col = next((col for col in trader_cols if col in df.columns), None)
        if trader_col is None:
            raise ValueError(f"找不到交易人欄位，目前欄位：{list(df.columns)}")
        
        # 確認多單/空單欄位 (可能名稱有異動)
        long_cols = ["多單口數", "多方未平倉口數"]
        short_cols = ["空單口數", "空方未平倉口數"]
        long_col = next((col for col in long_cols if col in df.columns), None)
        short_col = next((col for col in short_cols if col in df.columns), None)
        
        if long_col is None or short_col is None:
            raise ValueError(f"找不到多單/空單欄位，目前欄位：{list(df.columns)}")

        # 篩選外資資料
        foreign_df = df[df[trader_col] == "外資"]
        
        if foreign_df.empty:
            raise ValueError("在資料中找不到 '外資' 的交易人項目 (可能欄位值異動或網頁結構改變)")

        # 4. 數值處理與計算
        
        # 數值轉換工具 (處理千分位逗號)
        def to_int(val):
            return int(str(val).replace(",", "").strip())

        try:
            # 取得外資的多單和空單數值
            # 使用 .iloc[0] 確保只取第一個匹配項
            foreign_long = to_int(foreign_df[long_col].iloc[0])
            foreign_short = to_int(foreign_df[short_col].iloc[0])
            
            # 計算淨口數
            foreign_net = foreign_long - foreign_short

        except Exception:
             raise ValueError("無法將外資多單或空單數值轉換為整數 (欄位值非數字)")

        # 5. 組合成功輸出 (符合 outsourcing_spec.md 的 data 規範)
        
        data = {
            "foreign_net_oi": foreign_net,
            "foreign_long_oi": foreign_long,
            "foreign_short_oi": foreign_short,
        }
        
        # 簡要 summary，可供主程式 log
        summary = f"F1: 台指期貨外資淨口數 (OI): {foreign_net}（來源：TAIFEX）"

        return {
            "module": module_code,
            "date": date,
            "status": "success",
            "data": data, # 符合 outsourcing_spec.md 的 data 規範
            "summary": summary # 額外提供的簡要說明
        }

    except Exception as e:
        # 6. 組合失敗輸出
        return {
            "module": module_code,
            "date": date,
            "status": "fail",
            "error": str(e),
        }

# 測試用：模組可獨立執行
if __name__ == "__main__":
    # 範例測試日期：2025-11-28 (請自行修改為有效日期)
    print("--- 測試 '2025-11-28' ---")
    result = fetch("2025-11-28")
    print(result)
    
    print("\n--- 測試 '查無資料' 案例 (假設 2025-11-30 為假日或未來) ---")
    # 請替換為一個確定會查無資料的日期，這裡僅為模擬
    result_fail = fetch("2025-11-30")
    print(result_fail)