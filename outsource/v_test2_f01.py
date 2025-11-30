"""
F2 模組需求 (範例) - 自動抓取最新資料版本
- 指標名稱：三大法人-外資及陸資-臺股期貨淨未平倉口數
- 資料來源：台灣期貨交易所 (TAIFEX) 官方網站 - 三大法人
- 需抓取欄位：臺股期貨 未平倉口數淨額
- 輸入：無
- 輸出：dict 格式，包含最新資料
"""

import requests
import pandas as pd
from datetime import date

def fetch_latest_institutional_investors_data() -> dict:
    """
    抓取三大法人臺股期貨外資淨未平倉口數 (最新交易日)

    輸出: dict: 統一格式 (成功或失敗)
    """
    # 使用今天的日期來查詢，期交所系統會自動回傳最近的一個交易日資料
    query_date = date.today().strftime("%Y-%m-%d")
    
    try:
        # 1. 目標 URL
        url = "https://www.taifex.com.tw/cht/3/totalTableDate"

        # 2. 準備 POST 表單資料
        #    - queryType: '2' 代表依日期查詢
        #    - queryDate: 日期，格式需為 YYYY/MM/DD
        form_data = {
            'queryType': '2',
            'queryDate': query_date.replace('-', '/')
        }

        # 3. 發送 POST 請求
        response = requests.post(url, data=form_data)
        response.encoding = 'utf-8'

        # 4. 使用 pandas 解析回傳的 HTML 表格
        #    三大法人的資料在第五個表格中 ([4])
        dfs = pd.read_html(response.text)
        if len(dfs) < 5:
            raise ValueError("TAIFEX 網頁結構可能已變更，找不到預期的資料表格")
        
        df = dfs[4]

        # 5. 清理與重設欄位名稱
        #    原始表格有多層欄位，我們將其簡化以便操作
        df.columns = [col[1] for col in df.columns]

        # 6. 篩選商品為「臺股期貨」且身份別為「外資及陸資」的資料
        target_row = df.loc[(df['商品名稱'] == '臺股期貨') & (df['身份別'] == '外資及陸資')]

        if target_row.empty:
            raise ValueError(f"在 {query_date} 找不到 '臺股期貨' 的 '外資及陸資' 資料")

        # 7. 取得「未平倉口數淨額」
        net_oi = int(target_row['未平倉口數淨額'].iloc[0])
        
        # 從表格中解析出實際的資料日期
        actual_data_date = target_row['日期'].iloc[0]

        # 8. 組合成功訊息
        summary = f"三大法人-臺股期貨-外資淨未平倉口數: {net_oi} (來源: TAIFEX, 日期: {actual_data_date})"

        return {
            "module": "f02_institutional_investors_latest", # 假設模組代號
            "query_date": query_date, # 我們用來查詢的日期
            "data_date": actual_data_date, # 資料本身的日期
            "status": "success",
            "summary": summary,
            "data": {
                "net_open_interest": net_oi
            }
        }

    except Exception as e:
        # 9. 統一的錯誤回報
        return {
            "module": "f02_institutional_investors_latest",
            "query_date": query_date,
            "status": "fail",
            "error": str(e)
        }

# 當這個 .py 檔案被直接執行時，會執行以下區塊，方便進行單獨測試
if __name__ == "__main__":
    # 執行抓取最新資料的函式
    result = fetch_latest_institutional_investors_data()
    print(result)
