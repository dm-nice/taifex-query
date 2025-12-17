"""
f07_fetcher.py
F07: 臺指選擇權(TXO)買賣權未平倉量比率% 抓取模組

功能：
- 抓取 TAIFEX 每日 Put/Call Ratio (未平倉量比率)
- 來源: https://www.taifex.com.tw/cht/3/pcRatio

輸出格式：
2025.12.10  F07: 臺指選擇權(TXO)買賣權未平倉量比率% : 142.73% [TAIFEX]
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
MODULE_ID = "f07"
MODULE_NAME = "f07_fetcher"

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def format_f07_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
    """
    格式化 output v5.0
    """
    formatted_date = date.replace("-", ".")
    
    if status == "success" and data:
        value = data.get("pcr", 0)
        # PCR 通常有小數點，且需加上 %
        return f"{formatted_date}  F07: 臺指選擇權(TXO)買賣權未平倉量比率% : {value}% [TAIFEX]"
    else:
        error_msg = error or "未知錯誤"
        return f"{formatted_date}  F07 錯誤: {error_msg} [TAIFEX]"


def fetch(date: str) -> str:
    """
    抓取 F07 Data
    """
    url = "https://www.taifex.com.tw/cht/3/pcRatio"
    
    # 驗證日期並轉換格式 YYYY/MM/DD
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        query_date = dt.strftime("%Y/%m/%d")
    except ValueError:
        return format_f07_output(date, "error", error="日期格式錯誤")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36'
        }
        params = {'queryDate': query_date}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return format_f07_output(date, "error", error=f"HTTP {response.status_code}")
            
        dfs = pd.read_html(response.text)
        if not dfs:
            return format_f07_output(date, "error", error="找不到表格")
            
        df = dfs[0]
        
        # 尋找目標欄位
        target_col = None
        for col in df.columns:
            # 關鍵字: 未平倉量比率 (Open Interest Ratio)
            if "未平倉量比率" in str(col):
                target_col = col
                break
        
        if not target_col:
            # 可能是無資料頁面
            if "查無資料" in response.text:
                return format_f07_output(date, "error", error="該日無交易資料")
            return format_f07_output(date, "error", error="找不到目標欄位(未平倉量比率)")

        # 檢查日期欄位 (確認抓到的是該日資料)
        # 此 API 支援指定日期，通常第一列就是該日
        # 但需確認第一欄是否為日期
        if df.empty:
             return format_f07_output(date, "error", error="該日無交易資料")
             
        row = df.iloc[0]
        val = row[target_col]
        
        if pd.isna(val):
             return format_f07_output(date, "error", error="數值為空 (NaN)")
             
        return format_f07_output(date, "success", data={"pcr": val})
            
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        return format_f07_output(date, "error", error=str(e))


def main():
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = datetime.now().strftime("%Y-%m-%d")
    print(fetch(date))

if __name__ == "__main__":
    main()
