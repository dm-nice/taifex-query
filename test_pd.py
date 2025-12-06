import pandas as pd
import requests
from io import StringIO
from datetime import date, timedelta

# --- 設定常數 ---
TAIFEX_URL = "https://www.taifex.com.tw/cht/3/totalTableDate"
TARGET_COMMODITY = "臺股期貨"
TARGET_INSTITUTION = "外資"
OUTPUT_SOURCE = "臺灣期貨交易所 (TAIFEX) 網站"

def get_latest_trading_date(days_back=0) -> str:
    """計算並返回要查詢的日期，格式為 YYYY/MM/DD"""
    return (date.today() - timedelta(days=days_back)).strftime("%Y/%m/%d")

def fetch_taifex_data(query_date: str) -> pd.DataFrame:
    """
    從 TAIFEX 網頁抓取特定日期的三大法人期貨交易總表數據。
    
    :param query_date: 欲查詢的日期，格式 e.g., "2025/12/05"
    :return: 包含所有法人部位的 DataFrame。
    """
    print(f"-> 正在查詢 {query_date} ({query_date.replace('/', '')}) 的數據...")

    # 設置 POST 請求的表單數據
    form_data = {
        'dateString': query_date.replace('/', ''),  # API 查詢欄位需要 YYYYMMDD 格式
        'queryType': '1'  # 查詢類型 1：依日期查詢
    }

    try:
        # 發送 POST 請求
        response = requests.post(TAIFEX_URL, data=form_data)
        response.raise_for_status()  # 檢查 HTTP 請求是否成功
        
        # 使用 pandas.read_html 直接解析 HTML 中的表格
        # [0] 選擇第一個 (主要的) 表格
        df = pd.read_html(StringIO(response.text), encoding='utf-8')[0]

        # 重新命名欄位以便於存取。根據經驗，這是總表常見的欄位結構
        df.columns = [
            '商品名稱', '身份別', '買方口數', '買方金額', 
            '賣方口數', '賣方金額', '多空淨額口數', '多空淨額金額', '資料狀態'
        ]
        
        return df

    except requests.exceptions.RequestException as e:
        print(f"網路或請求錯誤: {e}")
    except ValueError:
        print("解析 HTML 錯誤：該日期可能無數據或網頁結構已更改。")
    except Exception as e:
        print(f"發生未預期的錯誤: {e}")
        
    return pd.DataFrame()

def format_output_f1(df: pd.DataFrame, query_date: str) -> str:
    """
    從 DataFrame 中提取「臺股期貨」的外資多空淨額口數，並格式化為 F1 格式。
    """
    
    # 1. 篩選出目標身份別 (外資)
    foreign_investors_df = df[df['身份別'].str.contains(TARGET_INSTITUTION, na=False)]

    # 2. 篩選出目標商品 (臺股期貨)
    tx_futures = foreign_investors_df[foreign_investors_df['商品名稱'].str.contains(TARGET_COMMODITY, na=False)]

    if tx_futures.empty:
        return f"[錯誤] 找不到 {query_date} 的 {TARGET_COMMODITY} ({TARGET_INSTITUTION}) 淨部位數據。"

    # 3. 提取多空淨額口數 (通常只需要第一行的數據)
    # 使用 .iloc[0] 取得第一行
    net_position = tx_futures['多空淨額口數'].iloc[0]
    
    # 檢查數據是否為有效數字 (例如 TAIFEX 網站有時會用 '-' 或 '0')
    if pd.isna(net_position):
        net_position = "N/A"
    
    # 格式化輸出
    output = (
        f"F1: 台指期貨外資 [未平倉] [多空淨額] : {net_position} 口 "
        f"[{OUTPUT_SOURCE} | 數據日期: {query_date}]"
    )
    return output

# --- 主程式運行 ---
if __name__ == "__main__":
    
    # 預設查詢今天
    date_to_query = get_latest_trading_date(0)
    data_df = pd.DataFrame()
    found = False
    
    # 嘗試最多回溯 7 天 (涵蓋週末或休假日)
    for days in range(7):
        date_to_query = get_latest_trading_date(days)
        data_df = fetch_taifex_data(date_to_query)
        
        if not data_df.empty:
            # 成功抓到數據後，嘗試解析
            formatted_result = format_output_f1(data_df, date_to_query)
            print("\n" + "="*50)
            print(formatted_result)
            print("="*50)
            found = True
            break
            
        else:
            print(f"-> {date_to_query} 無效或無數據，嘗試回溯...")
            
    if not found:
        print("\n[失敗] 無法在最近 7 個日期內抓取到 TAIFEX 外資多空淨額數據。")