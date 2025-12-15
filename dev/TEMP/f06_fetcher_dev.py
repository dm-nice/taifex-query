"""
f06_fetcher.py
F06: 台指期貨選擇權波動率指數 (TVIX) 抓取模組

功能：
- 抓取 TAIFEX 每日收盤之 VIX 指數
- 支援多種 URL 來源嘗試 (MinNew, HistoryDates)

資料來源：
- https://www.taifex.com.tw/cht/7/vixMinNew (優先)
- https://www.taifex.com.tw/cht/7/vixHistoryDates (備援)
"""

import sys
import io
import logging
import requests
import pandas as pd
from typing import Dict, Optional
from datetime import datetime

# 設定 UTF-8 輸出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 模組識別
MODULE_ID = "f06"
MODULE_NAME = "f06_fetcher"

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def format_f06_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
    """
    格式化 output v5.0
    [YYYY.MM.DD]  F06: 台指期貨選擇權波動率指數 (TVIX) : [數值] [TAIFEX]
    """
    formatted_date = date.replace("-", ".")
    
    if status == "success" and data:
        value = data.get("vix", 0)
        # 如果是浮點數，保留小數點；如果是 NaN 或 0，需注意
        return f"{formatted_date}  F06: 臺指選擇權波動率指數 : {value} [TAIFEX]"
    else:
        error_msg = error or "未知錯誤"
        return f"{formatted_date}  F06 錯誤: {error_msg} [TAIFEX]"


def fetch_vix_min_new(date: str, url_date: str) -> Optional[float]:
    """
    嘗試從 vixMinNew 抓取
    策略：
    1. 檢查是否有 '下載' 按鈕 (getVixData?filesname=YYYYMMDD)
    2. 若有，下載該文字檔並讀取最後一行數值
    3. 若無，嘗試解析表格數值
    """
    url = "https://www.taifex.com.tw/cht/7/vixMinNew"
    base_url = "https://www.taifex.com.tw/cht/7/"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None

        # 1. 嘗試尋找下載連結 getVixData?filesname=YYYYMMDD
        # 目標日期格式 YYYYMMDD
        target_ymd = date.replace("-", "")
        download_marker = f"getVixData?filesname={target_ymd}"
        
        if download_marker in response.text:
            logger.info(f"Found VIX download link for {target_ymd}")
            file_url = f"{base_url}{download_marker}"
            
            file_resp = requests.get(file_url, headers=headers, timeout=10)
            file_resp.encoding = 'big5' # 通常是 Big5
            
            lines = file_resp.text.strip().split('\n')
            # 格式: 交易日期 時間 指數
            # 檔案最後一行可能是 "Last 1 min AVG" 統計
            # 範例: 20251210       Last 1 min AVG                  20.15
            # 因此取 parts[-1] 作為數值
            if len(lines) > 2:
                # 從最後一行往回找，直到找到有效數值
                for i in range(1, 6): # 檢查最後 5 行
                    if len(lines) < i: break
                    last_line = lines[-i].strip()
                    parts = last_line.split()
                    if len(parts) >= 3:
                        try:
                            val_str = parts[-1] # 取最後一欄
                            return float(val_str)
                        except ValueError:
                            continue # 非數字，繼續往上找？
                            
                # Fallback to last line blindly if loop fails
                last_line = lines[-1].strip()
                parts = last_line.split()
                if len(parts) >= 2:
                   return float(parts[-1])

        # 2. 原有表格解析邏輯 (備援)
        dfs = pd.read_html(response.text)
        if not dfs:
            return None
            
        df = dfs[0]
        # 尋找日期
        target_dates = [date, url_date]
        
        # 尋找 VIX 欄位
        val_col = None
        for col in df.columns:
            if "指數" in str(col) or "VIX" in str(col):
                val_col = col
                break
        
        if not val_col:
            return None
            
        # 尋找日期欄位
        date_col = df.columns[0]
        df[date_col] = df[date_col].astype(str)
        
        row = df[df[date_col].isin(target_dates)]
        if not row.empty:
            val = row.iloc[0][val_col]
            if pd.isna(val):
                return None
            return float(val)
            
    except Exception as e:
        logger.debug(f"vixMinNew failed: {e}")
        
    return None


def fetch(date: str) -> str:
    """
    抓取 F06 VIX Data
    """
    # 驗證日期
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        url_date = dt.strftime("%Y/%m/%d")
    except ValueError:
        return format_f06_output(date, "error", error="日期格式錯誤")
        
    # 策略 1: VIX Min New
    vix_val = fetch_vix_min_new(date, url_date)
    
    if vix_val is not None:
        return format_f06_output(date, "success", data={"vix": vix_val})
        
    # 策略 2: 如果策略 1 失敗 (NaN 或找不到)，回報無資料
    # 因為 History 404，暫時無法依賴
    
    return format_f06_output(date, "failed", error="該日無交易資料 (VIX)")


def main():
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = datetime.now().strftime("%Y-%m-%d")
    print(fetch(date))

if __name__ == "__main__":
    main()
