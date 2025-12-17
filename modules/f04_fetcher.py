"""
f04_fetcher.py
台指期貨當日收盤價 (Day N Close) 抓取模組

功能：
- 從 TAIFEX 網站抓取台指期貨 (TX) 當日收盤價 (最後成交價)
- 提供 fetch(date: str) -> str 統一介面
- 自動選取近月合約

資料來源：
- 期貨每日交易行情查詢
- https://www.taifex.com.tw/cht/3/futDailyMarketReport
"""

import sys
import io
import logging
import requests
import pandas as pd
from typing import Dict, Optional
from datetime import datetime

# 設定 UTF-8 輸出（解決 Windows 終端亂碼，PyInstaller 已處理打包的情境）
# 只在尚未包裝時才進行包裝，避免重複包裝導致 I/O 錯誤
if sys.platform == 'win32' and not getattr(sys, "frozen", False):
    if not hasattr(sys.stdout, '_wrapped_for_utf8'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stdout._wrapped_for_utf8 = True
    if not hasattr(sys.stderr, '_wrapped_for_utf8'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        sys.stderr._wrapped_for_utf8 = True

# 模組識別
MODULE_ID = "f04"
MODULE_NAME = "f04_fetcher"

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def format_f04_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
    """
    格式化 F04 輸出為統一文字格式 v5.0

    Args:
        date: 日期 (YYYY-MM-DD)
        status: 狀態 ("success" / "failed" / "error")
        data: 成功時的資料字典
        error: 失敗時的錯誤訊息

    Returns:
        成功時: F04: 台指期貨當日收盤價 (Day N Close) : 23,450 [TAIFEX]
        失敗時: F04 錯誤: {錯誤訊息} [TAIFEX]
    """
    if status == "success" and data:
        price = data.get("close_price", 0)
        source = data.get("source", "TAIFEX")
        
        # 格式化數值：如果是整數，加千分位；如果有小數，保留顯示
        if isinstance(price, (int, float)):
             price_str = f"{price:,}"
        else:
             price_str = str(price)

        formatted_date = date.replace("-", ".")
        return f"{formatted_date}  F04: 台指期貨當日收盤價 (Day N Close) : {price_str} [TAIFEX]"
    else:
        error_msg = error or "未知錯誤"
        return f"F04 錯誤: {error_msg} [TAIFEX]"


def convert_to_number(value) -> Optional[float]:
    """將字串轉換為數值 (float 或 int)"""
    if pd.isna(value) or str(value).strip() == '-':
        return None
    try:
        # 移除逗號
        clean_val = str(value).replace(',', '').strip()
        if '.' in clean_val:
            return float(clean_val)
        return int(clean_val)
    except (ValueError, AttributeError):
        return None


def find_column(df: pd.DataFrame, keywords: list) -> Optional[str]:
    """尋找包含特定關鍵字的欄位"""
    for col in df.columns:
        col_str = str(col)
        if any(keyword in col_str for keyword in keywords):
            return col
    return None


def extract_close_price(df: pd.DataFrame, date: str) -> Dict:
    """從表格中提取 TX 近月合約收盤價"""
    
    # 1. 尋找並篩選合約 (TX)
    contract_col = find_column(df, ['契約', 'Contract'])
    if contract_col is None:
         # 嘗試直接假設第一欄是契約
         contract_col = df.columns[0]
    
    # 清理並篩選 TX
    # 有些時候契約欄位可能有空格，或是 "TX "
    df['clean_contract'] = df[contract_col].astype(str).str.strip()
    tx_rows = df[df['clean_contract'] == 'TX']
    
    if len(tx_rows) == 0:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "failed",
            "error": "找不到台指期(TX)資料"
        }
    
    # 2. 排序取近月 (通常 API 回傳已經是排序好的，第一筆即為近月)
    # 若要保險，可以找 '到期月份' 進行排序，但這裡先取第一筆 (Front Month)
    target_row = tx_rows.iloc[0]
    
    # 3. 找成交價欄位
    price_col = find_column(df, ['最後成交價', '最後 成交價', '收盤價', 'Close', 'Last Price'])
    settle_col = find_column(df, ['結算價', 'Settlement'])
    
    final_price = None
    
    if price_col:
        final_price = convert_to_number(target_row[price_col])
    
    # 若無成交價 (例如無交易)，嘗試取結算價
    if final_price is None and settle_col:
        final_price = convert_to_number(target_row[settle_col])
        
    if final_price is None:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "failed",
            "error": "無法取得收盤價或結算價"
        }
        
    return {
        "module": MODULE_ID,
        "date": date,
        "status": "success",
        "data": {
            "close_price": final_price,
            "source": "TAIFEX"
        },
        "source": "TAIFEX"
    }


def fetch(date: str) -> str:
    """
    抓取指定日期的台指期貨當日收盤價

    Args:
        date: 日期字串 (YYYY-MM-DD)
    """
    # 驗證日期格式
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_f04_output(date, "error", error="日期格式錯誤，請使用 YYYY-MM-DD")
    
    # 轉換日期格式為 TAIFEX 查詢格式 (YYYY/MM/DD)
    query_date = dt.strftime("%Y/%m/%d")
    
    # URL: 期貨每日交易行情查詢
    url = f"https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate={query_date}&marketCode=0&commodity_id=TX"
    
    try:
        logger.info(f"正在抓取 {date} 的資料: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = "utf-8"  # TAIFEX 每日行情通常是 UTF-8
        
        # 解析 HTML 表格
        try:
            # 使用 lxml 解析
            dfs = pd.read_html(io.StringIO(response.text), flavor='lxml')
        except ImportError:
            dfs = pd.read_html(io.StringIO(response.text))
            
        if not dfs:
             return format_f04_output(date, "failed", error="找不到表格資料")
             
        # 通常主要資料在第一個表格，但也許要檢查一下
        df = dfs[0]
        
        # 檢查是否為空表
        if len(df) < 2:
             return format_f04_output(date, "failed", error="查無資料 (可能是假日)")

        result_dict = extract_close_price(df, date)

        if result_dict.get("status") == "success":
            return format_f04_output(date, "success", data=result_dict.get("data"))
        else:
            return format_f04_output(date, "failed", error=result_dict.get("error", "未知錯誤"))

    except requests.Timeout:
        return format_f04_output(date, "error", error="連線逾時")
    except Exception as e:
        logger.exception("執行過程發生錯誤")
        return format_f04_output(date, "error", error=f"系統錯誤: {str(e)}")


def main():
    if len(sys.argv) > 1:
        test_date = sys.argv[1]
    else:
        test_date = '2025-12-04'
    print(f"測試日期: {test_date}")
    print(fetch(test_date))

if __name__ == '__main__':
    main()
