"""
F01 模組：台指期貨外資淨口數 (OI) 抓取程式
來源：TAIFEX 每日所有商品總表 (totalTableDate)
功能：抓取指定日期「外資」於「期貨」的未平倉淨口數。
      結構依照使用者提供的圖片優化，處理 MultiIndex。
"""
import requests
import pandas as pd
from typing import Dict, Any

def fetch(date: str) -> Dict[str, Any]:
    """
    輸入: date (str): 日期字串，格式 YYYY-MM-DD
    輸出: dict: 統一格式 (成功或失敗)
    """
    module_code = "f01"
    
    # 根據 TAIFEX 網址格式，將 YYYY-MM-DD 轉為 YYYY/MM/DD
    taifex_date = date.replace('-', '/') 

    try:
        # 1. 網路請求 (使用 totalTableDate 網址)
        # 查詢所有商品總表
        url = f"https://www.taifex.com.tw/cht/3/totalTableDate?queryType=1&marketCode=0&date={taifex_date}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=10) # 增加 timeout
        resp.encoding = "utf-8"
        
        if resp.status_code != 200:
            raise requests.exceptions.RequestException(f"網路請求失敗，HTTP 狀態碼: {resp.status_code}")
        
        if "該條件查無資料" in resp.text:
            raise ValueError(f"該日 ({date}) 無交易資料，TAIFEX 回傳查無資料")

        # 2. 資料解析與標題處理
        try:
            df_list = pd.read_html(resp.text)
            
            # 🚨 關鍵修正：圖片顯示「未平倉餘額」表格為網頁上的第二個主要表格 (索引 1) 🚨
            # 如果總表結構變動，可能需要調整這裡的索引
            if len(df_list) < 2:
                raise ValueError("TAIFEX 網頁解析失敗，未找到未平倉餘額表格 (df_list 數量不足)")
                
            df_oi = df_list[1] # 專注於未平倉餘額表格
            
            # 處理多層標題 (MultiIndex Header)
            if isinstance(df_oi.columns, pd.MultiIndex):
                new_cols = []
                for col in df_oi.columns:
                    # 扁平化：將層級組合起來，如：('未平倉餘額', '多方', '口數') -> '未平倉餘額-多方-口數'
                    # 避免在 MultiIndex 中出現 NaN，這裡使用 join
                    new_col = '-'.join([str(c) for c in col if str(c).strip() != ''])
                    new_cols.append(new_col)
                df_oi.columns = new_cols
            
            # 移除所有 NaN/空白列，增加資料處理穩定性
            df_oi = df_oi.dropna(how='all')
            
        except Exception as e:
             raise ValueError(f"網頁表格解析失敗，請檢查網頁結構：{str(e)}")


        # 3. 欄位確認與篩選
        
        # 尋找「身份別」或「交易人」欄位
        trader_col = next((col for col in df_oi.columns if "身份別" in col or "交易人" in col), None)
        if trader_col is None:
            # 檢查是否欄位名稱被合併
            trader_col = next((col for col in df_oi.columns if "未平倉餘額-多方-口數" in col), None)
            if trader_col is None:
                raise ValueError(f"找不到身份別/交易人欄位，目前扁平化欄位：{list(df_oi.columns)}")
        
        # 篩選出「外資」的資料
        foreign_row = df_oi[df_oi[trader_col].astype(str).str.contains("外資", na=False)]
        
        if foreign_row.empty:
            raise ValueError("在未平倉表格中找不到 '外資' 的交易人項目")

        # 4. 數值處理與計算
        
        # 根據圖片結構，精確尋找多單/空單未平倉口數欄位 (定位到「期貨」)
        # 欄位名稱應包含: '多方' AND '口數' AND '期貨'
        oi_long_col = next((col for col in df_oi.columns if "多方" in col and "口數" in col and "期貨" in col), None)
        oi_short_col = next((col for col in df_oi.columns if "空方" in col and "口數" in col and "期貨" in col), None)
        
        if oi_long_col is None or oi_short_col is None:
            raise ValueError(f"找不到多方/空方 期貨未平倉口數欄位，請檢查扁平化後欄位：{list(df_oi.columns)}")

        # 數值轉換工具 (處理千分位逗號)
        def to_int(val):
            return int(str(val).replace(",", "").strip())

        try:
            # 抓取數值
            foreign_long = to_int(foreign_row[oi_long_col].iloc[0])
            foreign_short = to_int(foreign_row[oi_short_col].iloc[0])
            
            # 計算淨口數
            foreign_net = foreign_long - foreign_short

        except Exception:
             raise ValueError("無法將外資多單或空單數值轉換為整數 (欄位值非數字或缺失)")

        # 5. 組合成功輸出 (符合 outsourcing_spec.md 規範)
        data = {
            "foreign_net_oi": foreign_net,
            "foreign_long_oi": foreign_long,
            "foreign_short_oi": foreign_short,
        }
        
        summary = f"F1: 台指期貨外資淨口數 (OI): {foreign_net}（來源：TAIFEX/總表）"

        return {
            "module": module_code,
            "date": date,
            "status": "success",
            "data": data, # 根據範例，應提供 data 欄位
            "summary": summary
        }

    except Exception as e:
        # 6. 組合失敗輸出 (符合 outsourcing_spec.md 規範)
        return {
            "module": module_code,
            "date": date,
            "status": "fail",
            "error": str(e),
        }

# 測試用：模組可獨立執行
if __name__ == "__main__":
    # 使用一個過去確實有交易資料的日期進行測試
    test_date = "2023-11-28" 
    print(f"--- 測試 '{test_date}' (依照圖片結構解析) ---")
    result = fetch(test_date)
    print(result)
    
    print("\n--- 測試 '查無資料' 案例 (例如未來日期) ---")
    result_fail = fetch("2099-01-01")
    print(result_fail)



