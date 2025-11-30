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

        # 核心修正：指定 header=[0, 1, 2] 來讀取多層標題
        # 並且選擇第二個表格（未平倉口數與契約金額）
        dfs = pd.read_html(resp.text, header=[0, 1, 2])
        if len(dfs) < 2:
             raise ValueError("TAIFEX 網頁表格數量不足，無法取得未平倉餘額表格")

        # 選擇「未平倉口數與契約金額」表格，通常是第二個表格
        df = dfs[1] 
        
        # 1. 處理多層欄位名稱 (MultiIndex)，將其扁平化
        # 範例： ('未平倉餘額', '多方', '口數') -> '未平倉餘額-多方-口數'
        df.columns = ['-'.join(col).strip() for col in df.columns.values]

        # 2. 修正交易人名稱欄位，確保第一欄是身份別
        df = df.rename(columns={df.columns[0]: '身份別'})

        # 3. 數值轉換工具 (排除掉 DataFrame 中所有非字串的 NaN)
        def to_int(val):
            return int(str(val).replace(",", "").strip())

        # 4. 篩選外資資料
        foreign = df[df['身份別'].str.contains("外資", na=False)]
        if foreign.empty:
            raise ValueError(f"找不到日期 {date} 的外資資料。")

        # 5. 精確定位目標欄位（所有期貨商品未平倉淨口數）
        # 根據圖片，淨口數在 '未平倉餘額-多空淨額-口數-期貨' 欄位
        net_col = '未平倉餘額-多空淨額-口數-期貨'
        
        # 根據您上傳的圖片 (image_025e3b.png)， TAIFEX 總表格式可能不同
        # 我們改抓多方和空方，自己計算淨口數，以提高穩定性
        long_col = '未平倉餘額-多方-口數-期貨' 
        short_col = '未平倉餘額-空方-口數-期貨' 
        
        # 檢查欄位是否存在
        if long_col not in df.columns or short_col not in df.columns:
            # 如果是舊版 pandas 讀取，可能不需要 '未平倉餘額' 前綴
            long_col = '多方-口數-期貨' 
            short_col = '空方-口數-期貨'
            
            if long_col not in df.columns or short_col not in df.columns:
                # 再次檢查若欄位仍不存在，則回報所有欄位名稱
                 raise ValueError(f"找不到關鍵欄位 '{long_col}' 或 '{short_col}'，現有欄位：{list(df.columns)}")

        # 6. 計算淨口數
        foreign_long = to_int(foreign[long_col].values[0])
        foreign_short = to_int(foreign[short_col].values[0])
        foreign_net = foreign_long - foreign_short

        # 組合輸出
        summary = f"F1: TAIFEX 外資期貨淨口數 (OI): {foreign_net}（來源：TAIFEX 總表）"

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
    # 測試日期 '2025-11-28'
    print("--- 測試 '2025-11-28' ---")
    result = fetch("2025-11-28")
    print(result)

    # 測試 '2025-11-30' (假日或無資料日期)
    print("\n--- 測試 '2025-11-30' (假日或未來日期) ---")
    result_fail = fetch("2025-11-30")
    print(result_fail)