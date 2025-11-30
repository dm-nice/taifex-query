"""
F2 模組需求 (範例) - 固定日期測試版本
- 指標名稱：三大法人-外資及陸資-臺股期貨淨未平倉口數
- 資料來源：台灣期貨交易所 (TAIFEX) 官方網站 - 三大法人
- 說明：此程式會抓取固定日期 (2025-11-28) 的資料，方便進行測試。
"""

import requests
import pandas as pd

def fetch_fixed_date_institutional_data() -> dict:
    """
    抓取三大法人臺股期貨外資淨未平倉口數 (固定日期 2025-11-28)

    輸出: dict: 統一格式 (成功或失敗)
    """
    # 將查詢日期固定為 2025-11-28
    fixed_date = "2025-11-28"
    
    try:
        # 1. 目標 URL
        url = "https://www.taifex.com.tw/cht/3/totalTableDate"

        # 2. 準備 POST 表單資料
        #    - queryType: '2' 代表依日期查詢
        #    - queryDate: 日期，格式需為 YYYY/MM/DD
        form_data = {
            'queryType': '2',
            'queryDate': fixed_date.replace('-', '/')
        }

        # 3. 發送 POST 請求
        response = requests.post(url, data=form_data)
        response.encoding = 'utf-8'

        # 4. 使用 pandas 解析回傳的 HTML 表格
        #    三大法人的資料在第五個表格中 ([4])
        dfs = pd.read_html(response.text)
        if len(dfs) < 5:
            raise ValueError(f"在 {fixed_date} 的 TAIFEX 網站上找不到資料表格。")
        
        df = dfs[4]

        # 5. 清理與重設欄位名稱
        #    原始表格有多層欄位，我們將其簡化以便操作
        df.columns = [col[1] for col in df.columns]

        # 6. 篩選商品為「臺股期貨」且身份別為「外資及陸資」的資料
        target_row = df.loc[(df['商品名稱'] == '臺股期貨') & (df['身份別'] == '外資及陸資')]

        if target_row.empty:
            raise ValueError(f"在 {fixed_date} 找不到 '臺股期貨' 的 '外資及陸資' 資料")

        # 7. 取得「未平倉口數淨額」和實際資料日期
        net_oi = int(target_row['未平倉口數淨額'].iloc[0])
        actual_data_date = target_row['日期'].iloc[0]

        # 8. 組合成功訊息
        summary = f"三大法人-臺股期貨-外資淨未平倉口數: {net_oi} (來源: TAIFEX)"

        return {
            "module": "f02_institutional_investors_fixed_date",
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
            "module": "f02_institutional_investors_fixed_date",
            "query_date": fixed_date, # 記錄我們是用哪天去查詢的
            "status": "fail",
            "error": str(e)
        }

# 當這個 .py 檔案被直接執行時，會執行以下區塊
if __name__ == "__main__":
    print(f"正在抓取固定日期 (2025-11-28) 的資料...")
    result = fetch_fixed_date_institutional_data()
    
    # 美化輸出結果
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
