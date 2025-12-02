import requests
import pandas as pd
from typing import Dict, Any

# 數值轉換工具 (排除掉 DataFrame 中所有非字串的 NaN 和逗號)
def to_int(val: Any) -> int:
    """將可能帶有逗號的字串或非數字類型轉換為整數"""
    if pd.isna(val) or str(val).strip().lower() == 'nan':
        return 0
    try:
        return int(str(val).replace(",", "").strip())
    except ValueError:
        # 處理轉換失敗的情況，例如非預期文字，回傳 0
        return 0

def fetch(date: str) -> Dict[str, Any]:
    """
    F01 外包模組：抓取 TAIFEX 外資期貨未平倉淨口數
    輸入: date (str): 日期字串，格式 YYYY-MM-DD
    輸出: dict: 統一格式 (成功或失敗)
    """
    module_name = "f01"
    
    try:
        # TAIFEX 外資 OI 資料網址 (每日報表)
        # 依照規範書，日期格式需替換為 YYYY/MM/DD
        url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={date.replace('-', '/')}"
        
        # 依照規範書處理網路連線逾時，設置 timeout
        resp = requests.get(url, timeout=15) 
        resp.encoding = "utf-8"

        # 核心修正：
        # 1. 指定 header=[0, 1, 2] 讀取三層標題
        # 2. 總表頁面中，「未平倉口數與契約金額」表格是第二個 (index 1)
        dfs = pd.read_html(resp.text, header=[0, 1, 2])
        
        if len(dfs) < 2:
             # 依照規範書處理假日或無交易日情況
             return {
                "module": module_name,
                "date": date,
                "status": "fail",
                "error": "no data available (TAIFEX 網頁無未平倉餘額表格)" 
             }

        df = dfs[1] # 選擇第二個表格 (未平倉口數與契約金額)
        
        # 3. 處理多層欄位名稱 (MultiIndex)，將其扁平化
        df.columns = ['-'.join(map(str, col)).strip() for col in df.columns.values]

        # 4. 修正交易人名稱欄位為 '身份別'
        # 確保第一欄是身份別，即便標題有時會被解析為 'nan-nan-nan-身份別'
        df = df.rename(columns={df.columns[0]: '身份別'})

        # 5. 篩選外資資料
        # 檢查欄位是否存在以避免 KeyError
        if '身份別' not in df.columns:
             raise ValueError("structure changed (找不到 '身份別' 欄位)")

        # 使用 str.contains 確保找到 "外資" 該行
        foreign = df[df['身份別'].astype(str).str.contains("外資", na=False)]
        
        if foreign.empty:
            return {
                "module": module_name,
                "date": date,
                "status": "fail",
                "error": "no data available (找不到外資行資料)" 
            }

        # 6. 精確定位目標欄位：未平倉餘額 -> 多方/空方 -> 口數 -> 期貨
        long_col = '未平倉餘額-多方-口數-期貨' 
        short_col = '未平倉餘額-空方-口數-期貨' 
        
        # 檢查欄位是否存在，若不存在則視為結構改變
        if long_col not in df.columns or short_col not in df.columns:
            raise ValueError(f"structure changed (找不到關鍵欄位 '{long_col}' 或 '{short_col}')")

        # 7. 提取並計算淨口數
        foreign_long = to_int(foreign[long_col].values[0])
        foreign_short = to_int(foreign[short_col].values[0])
        foreign_net = foreign_long - foreign_short

        # 8. 組合輸出，符合 f01_fetcher_dev_外包範例.md 規範
        summary = f"F1: 台指期外資淨額：{foreign_net}（多：{foreign_long}，空：{foreign_short}）"

        return {
            "module": module_name,
            "date": date,
            "status": "success",
            "summary": summary,
            "data": {
                "外資多方口數": foreign_long,
                "外資空方口數": foreign_short,
                "外資多空淨額": foreign_net
            },
            "source": "TAIFEX"
        }

    except requests.exceptions.Timeout:
        return {
            "module": module_name,
            "date": date,
            "status": "fail",
            "error": "timeout (網路連線逾時)"
        }
    except Exception as e:
        # 處理其他所有錯誤
        error_msg = str(e)
        if "no data available" not in error_msg:
             # 如果錯誤不是預期中的無資料，則回報結構改變或未知錯誤
             error_msg = f"structure changed: {error_msg}"
        
        return {
            "module": module_name,
            "date": date,
            "status": "fail",
            "error": error_msg
        }

if __name__ == "__main__":
    # 測試 '2025-11-28' (有資料)
    print("--- 測試 '2025-11-28' ---")
    result_success = fetch("2025-11-28")
    print(result_success)
    
    # 測試 '2025-11-30' (假設假日或無資料日期)
    print("\n--- 測試 '2025-11-30' (假日或無資料日期) ---")
    result_fail = fetch("2025-11-30")
    print(result_fail)