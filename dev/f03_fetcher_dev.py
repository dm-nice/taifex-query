"""
f03_fetcher_dev.py
台指期貨外資未平倉「空方」口數抓取模組 (開發驗收版)
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

MODULE_ID = "f03"
MODULE_NAME = "f03_fetcher_dev"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def format_f03_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
    if status == "success" and data:
        short_pos = data.get("short_position", 0)
        source = data.get("source", "TAIFEX")
        formatted_date = date.replace("-", ".")
        return f"{formatted_date}  F03: 台指期貨外資 [未平倉] [空方] : {short_pos:,} 口 [TAIFEX]"
    else:
        error_msg = error or "未知錯誤"
        return f"F03 錯誤: {error_msg} [TAIFEX]"


def convert_to_int(value) -> int:
    if pd.isna(value):
        return 0
    try:
        return int(str(value).replace(',', '').strip())
    except (ValueError, AttributeError):
        return 0


def find_column_multiindex(df: pd.DataFrame, keywords: list) -> Optional[tuple]:
    for col in df.columns:
        col_str = ''.join(str(c) for c in col)
        if all(keyword in col_str for keyword in keywords):
            return col
    return None


def find_column_single(df: pd.DataFrame, possible_names: list) -> Optional[str]:
    for name in possible_names:
        if name in df.columns:
            return name
    return None


def extract_foreign_data_multiindex(df: pd.DataFrame, date: str) -> Dict:
    trader_col = None
    for col in df.columns:
        if any('身份別' in str(c) or '身份' in str(c) for c in col):
            trader_col = col
            break
    
    if trader_col is None:
        return {"module": MODULE_ID, "date": date, "status": "failed", "error": "找不到身份別欄位"}
    
    foreign_rows = df[df[trader_col].isin(['外資及陸資', '外資'])]
    
    if len(foreign_rows) == 0:
        return {"module": MODULE_ID, "date": date, "status": "failed", "error": "找不到外資資料"}
    
    short_col = find_column_multiindex(df, ['未平倉', '空方', '口'])
    
    if short_col is None:
        return {"module": MODULE_ID, "date": date, "status": "failed", "error": "找不到未平倉空方口數欄位"}
    
    try:
        short_pos = convert_to_int(foreign_rows[short_col].values[0])
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "success",
            "data": {"short_position": short_pos, "source": "TAIFEX"},
            "source": "TAIFEX"
        }
    except Exception as e:
        return {"module": MODULE_ID, "date": date, "status": "failed", "error": f"資料提取失敗: {str(e)}"}


def extract_foreign_data_single(df: pd.DataFrame, date: str) -> Dict:
    trader_col = find_column_single(df, ['身份別', '身份', '交易人', '交易人名稱', '身分別'])
    if trader_col is None:
        return {"module": MODULE_ID, "date": date, "status": "failed", "error": "找不到身份別欄位"}
    
    foreign_rows = df[df[trader_col].isin(['外資及陸資', '外資'])]
    if len(foreign_rows) == 0:
        return {"module": MODULE_ID, "date": date, "status": "failed", "error": "找不到外資資料"}
    
    short_col = find_column_single(df, ['未平倉餘額-空方-口數', '空方-口數', '空方口數', '空方', '空單口數'])
    if short_col is None:
        return {"module": MODULE_ID, "date": date, "status": "failed", "error": "找不到空方口數欄位"}
    
    try:
        short_pos = convert_to_int(foreign_rows.iloc[0][short_col])
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "success",
            "data": {"short_position": short_pos, "source": "TAIFEX"},
            "source": "TAIFEX"
        }
    except Exception as e:
        return {"module": MODULE_ID, "date": date, "status": "failed", "error": f"資料提取失敗: {str(e)}"}


def fetch(date: str) -> str:
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_f03_output(date, "error", error="日期格式錯誤")
    
    url_date = date.replace('-', '/')
    url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={url_date}"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = "utf-8"
        
        try:
            from lxml import html as lxml_html
            tables = pd.read_html(response.text, flavor='lxml')
        except ImportError:
            tables = pd.read_html(response.text)

        if len(tables) == 0:
            return format_f03_output(date, "failed", error="該日無交易資料")
        
        df = tables[0]
        if isinstance(df.columns, pd.MultiIndex):
            result_dict = extract_foreign_data_multiindex(df, date)
        else:
            result_dict = extract_foreign_data_single(df, date)

        if result_dict.get("status") == "success":
            return format_f03_output(date, "success", data=result_dict.get("data"))
        else:
            return format_f03_output(date, "failed", error=result_dict.get("error"))

    except Exception as e:
        return format_f03_output(date, "error", error=f"錯誤: {str(e)}")


def main():
    if len(sys.argv) > 1:
        test_date = sys.argv[1]
    else:
        test_date = '2025-12-04'
    print(fetch(test_date))

if __name__ == '__main__':
    main()
