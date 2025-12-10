"""
f05_fetcher.py
台指期貨選擇權總成交量抓取模組

功能：
- 從 TAIFEX 網站抓取台指選擇權 (TXO) 每日交易行情
- 計算當日所有合約的總成交量
- 提供 fetch(date: str) -> str 統一介面

資料來源：
https://www.taifex.com.tw/cht/3/optDailyMarketReport
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
MODULE_ID = "f05"
MODULE_NAME = "f05_fetcher"

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def format_f05_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
    """
    格式化 F05 輸出為統一文字格式 v5.0

    Args:
        date: 日期 (YYYY-MM-DD)
        status: 狀態 ("success" / "failed" / "error")
        data: 成功時的資料字典
        error: 失敗時的錯誤訊息

    Returns:
        統一格式文字字串 v5.0
        成功時: [YYYY.MM.DD]  F05: 台指期貨選擇權總成交量 : 430,688 口 [TAIFEX]
        失敗時: [YYYY.MM.DD]  F05 錯誤: {錯誤訊息} [TAIFEX]
    """
    formatted_date = date.replace("-", ".")
    
    if status == "success" and data:
        volume = data.get("total_volume", 0)
        source = data.get("source", "TAIFEX")
        return f"{formatted_date}  F05: 台指期貨選擇權總成交量 : {volume:,.0f} 口 [TAIFEX]"
    else:
        error_msg = error or "未知錯誤"
        return f"{formatted_date}  F05 錯誤: {error_msg} [TAIFEX]"


def find_volume_column(df: pd.DataFrame) -> Optional[str]:
    """
    尋找成交量欄位 (名稱可能包含 * 或空白)
    """
    keywords = ['成交量', '交易量']
    for col in df.columns:
        col_str = str(col)
        # 排除 "未沖銷" 相關欄位，只找成交量
        if any(k in col_str for k in keywords) and "未沖銷" not in col_str:
            return col
    return None


def fetch(date: str) -> str:
    """
    抓取指定日期的台指選擇權總成交量

    Args:
        date: 日期字串 (YYYY-MM-DD)

    Returns:
        統一格式的文字字串 v5.0
    """
    # 驗證日期格式
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_f05_output(date, "error", error="日期格式錯誤，請使用 YYYY-MM-DD")
    
    # 轉換日期格式
    url_date = date.replace('-', '/')
    url = f"https://www.taifex.com.tw/cht/3/optDailyMarketReport?queryDate={url_date}&marketCode=0&commodity_id=TXO"
    
    try:
        logger.info(f"正在抓取 {date} 的資料: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = "utf-8"
        
        # 解析表格
        try:
            tables = pd.read_html(response.text)
        except ValueError:
             return format_f05_output(date, "failed", error="找不到表格資料")
            
        if len(tables) == 0:
            return format_f05_output(date, "failed", error="該日無交易資料")
        
        df = tables[0]
        
        # 尋找成交量欄位
        vol_col = find_volume_column(df)
        
        if vol_col is None:
            # 嘗試列出所有欄位供 debug
            logger.warning(f"找不到成交量欄位，可用欄位: {df.columns.tolist()}")
            return format_f05_output(date, "failed", error="找不到成交量欄位")
        
        # 計算總成交量
        try:
            # 1. 轉為字串
            # 2. 移除逗號
            # 3. 處理 '-' 為 0
            # 4. 轉為浮點數
            series = df[vol_col].astype(str).str.replace(',', '').str.strip()
            series = series.replace('-', '0')
            # 過濾非數字 (例如空字串或其他符號)
            series = pd.to_numeric(series, errors='coerce').fillna(0)
            
            total_volume = series.sum()
            
            if total_volume == 0 and len(df) > 0:
                 logger.warning("警告：計算出的總成交量為 0")

            return format_f05_output(date, "success", data={
                "total_volume": total_volume,
                "source": "TAIFEX"
            })
            
        except Exception as e:
            return format_f05_output(date, "error", error=f"資料計算失敗: {str(e)}")

    except requests.Timeout:
        return format_f05_output(date, "error", error="連線逾時")
    except requests.RequestException as e:
        return format_f05_output(date, "error", error=f"網路請求失敗: {str(e)}")
    except Exception as e:
        logger.exception("未預期的錯誤")
        return format_f05_output(date, "error", error=f"未預期的錯誤: {str(e)}")


def main():
    """獨立測試用"""
    if len(sys.argv) > 1:
        test_date = sys.argv[1]
    else:
        test_date = datetime.now().strftime('%Y-%m-%d')

    print(f"測試日期: {test_date}")
    print(fetch(test_date))


if __name__ == '__main__':
    main()
