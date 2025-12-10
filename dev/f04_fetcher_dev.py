"""
f04_fetcher_dev.py
台指期貨當日收盤價 (Day N Close) 抓取模組 (開發版)
"""
# 直接引用 f04_package 的實作，或是完整複製
# 基於之前的經驗，run.py 需要獨立的檔案在 dev/ 下
# 為求簡單穩定，我們複製完整代碼

import sys
import io
import logging
import requests
import pandas as pd
from typing import Dict, Optional
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

MODULE_ID = "f04"
MODULE_NAME = "f04_fetcher_dev"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

def format_f04_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
    if status == "success" and data:
        price = data.get("close_price", 0)
        source = data.get("source", "TAIFEX")
        if isinstance(price, (int, float)):
             price_str = f"{price:,}"
        else:
             price_str = str(price)
        return f"F04: 台指期貨當日收盤價 (Day N Close) : {price_str} [TAIFEX]"
    else:
        error_msg = error or "未知錯誤"
        return f"F04 錯誤: {error_msg} [TAIFEX]"

def convert_to_number(value) -> Optional[float]:
    if pd.isna(value) or str(value).strip() == '-':
        return None
    try:
        clean_val = str(value).replace(',', '').strip()
        if '.' in clean_val:
            return float(clean_val)
        return int(clean_val)
    except (ValueError, AttributeError):
        return None

def find_column(df: pd.DataFrame, keywords: list) -> Optional[str]:
    for col in df.columns:
        col_str = str(col)
        if any(keyword in col_str for keyword in keywords):
            return col
    return None

def extract_close_price(df: pd.DataFrame, date: str) -> Dict:
    contract_col = find_column(df, ['契約', 'Contract'])
    if contract_col is None:
         contract_col = df.columns[0]
    
    df['clean_contract'] = df[contract_col].astype(str).str.strip()
    tx_rows = df[df['clean_contract'] == 'TX']
    
    if len(tx_rows) == 0:
        return {"module": MODULE_ID, "date": date, "status": "failed", "error": "找不到台指期(TX)資料"}
    
    target_row = tx_rows.iloc[0]
    price_col = find_column(df, ['最後成交價', '最後 成交價', '收盤價', 'Close', 'Last Price'])
    settle_col = find_column(df, ['結算價', 'Settlement'])
    
    final_price = None
    if price_col:
        final_price = convert_to_number(target_row[price_col])
    
    if final_price is None and settle_col:
        final_price = convert_to_number(target_row[settle_col])
        
    if final_price is None:
        return {"module": MODULE_ID, "date": date, "status": "failed", "error": "無法取得收盤價"}
        
    return {
        "module": MODULE_ID, "date": date, "status": "success",
        "data": {"close_price": final_price, "source": "TAIFEX"},
        "source": "TAIFEX"
    }

def fetch(date: str) -> str:
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_f04_output(date, "error", error="日期格式錯誤")
    
    query_date = dt.strftime("%Y/%m/%d")
    url = f"https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate={query_date}&marketCode=0&commodity_id=TX"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = "utf-8"
        
        try:
            dfs = pd.read_html(io.StringIO(response.text), flavor='lxml')
        except ImportError:
            dfs = pd.read_html(io.StringIO(response.text))
            
        if not dfs:
             return format_f04_output(date, "failed", error="找不到表格")
             
        df = dfs[0]
        if len(df) < 2:
             return format_f04_output(date, "failed", error="查無資料")

        result_dict = extract_close_price(df, date)

        if result_dict.get("status") == "success":
            return format_f04_output(date, "success", data=result_dict.get("data"))
        else:
            return format_f04_output(date, "failed", error=result_dict.get("error"))

    except Exception as e:
        return format_f04_output(date, "error", error=f"系統錯誤: {str(e)}")

def main():
    if len(sys.argv) > 1:
        test_date = sys.argv[1]
    else:
        test_date = '2025-12-04'
    print(fetch(test_date))

if __name__ == '__main__':
    main()
