"""
f14_fetcher_dev.py
F14: 台積電當日收盤價

功能：
- 讀取 TWSE 的每日成交資訊頁面（STOCK_DAY）
- 將指定日期的收盤價轉換為千分位格式，並輸出統一 v5 文本
- 處理假期、資料缺失與網路錯誤

輸出格式：
2025.12.11  F14: 台積電當日收盤價 : 1,470.00 [twse.com.tw]
"""

from __future__ import annotations

import io
import logging
import re
import sys
from datetime import datetime
from typing import Dict, Optional

import pandas as pd
import requests

# 設定 UTF-8 輸出（解決 Windows 終端亂碼，PyInstaller 已處理打包的情境）
# 只在尚未包裝時才進行包裝，避免重複包裝導致 I/O 錯誤
if sys.platform == 'win32' and not getattr(sys, "frozen", False):
    if not hasattr(sys.stdout, '_wrapped_for_utf8'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stdout._wrapped_for_utf8 = True
    if not hasattr(sys.stderr, '_wrapped_for_utf8'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        sys.stderr._wrapped_for_utf8 = True

MODULE_ID = "f14"
MODULE_NAME = "f14_fetcher"
SOURCE = "twse.com.tw"
STOCK_URL = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
REQUEST_TIMEOUT = 20

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


def format_f14_output(
    date: str,
    status: str,
    data: Optional[Dict] = None,
    error: Optional[str] = None,
) -> str:
    formatted_date = date.replace("-", ".")

    if status == "success" and data:
        closing = data.get("closing")
        source = data.get("source", SOURCE)
        return f"{formatted_date}  F14: 台積電當日收盤價 : {closing} [{source}]"

    error_msg = error or "未知錯誤"
    return f"{formatted_date}  F14 錯誤: {error_msg} [{SOURCE}]"


def _sanitize_number(value: str) -> Optional[float]:
    cleaned = re.sub(r"[^0-9\.-]", "", value)
    if not cleaned or cleaned in {"", "-"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _convert_roc_date(value: str) -> Optional[str]:
    if not value:
        return None
    value = value.strip()
    # 例：114/12/11
    parts = value.split("/")
    if len(parts) == 3:
        try:
            year = int(parts[0]) + 1911
            month = int(parts[1])
            day = int(parts[2])
            return datetime(year, month, day).strftime("%Y-%m-%d")
        except ValueError:
            pass
    try:
        return datetime.strptime(value, "%Y/%m/%d").strftime("%Y-%m-%d")
    except ValueError:
        pass
    return None


def _extract_row(df: pd.DataFrame, target: str) -> Optional[Dict]:
    df = df.copy()
    flat_columns = []
    for col in df.columns:
        if isinstance(col, tuple):
            flat_columns.append(col[-1])
        else:
            flat_columns.append(col)
    df.columns = [str(col).strip() for col in flat_columns]

    if "日期" not in df.columns or "收盤價" not in df.columns:
        return None

    df["normalized_date"] = df["日期"].apply(_convert_roc_date)
    row = df[df["normalized_date"] == target]
    if row.empty:
        return None

    closing_value = str(row.iloc[0]["收盤價"])
    numeric = _sanitize_number(closing_value)
    if numeric is None:
        return None

    return {
        "closing": f"{numeric:,.2f}",
        "source": SOURCE,
        "actual_date": row.iloc[0]["normalized_date"],
    }


def _fetch_data(date_str: str) -> pd.DataFrame:
    params = {
        "response": "html",
        "stockNo": "2330",
        "date": date_str.replace("-", ""),
    }
    response = requests.get(STOCK_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.encoding = "utf-8"
    response.raise_for_status()
    tables = pd.read_html(response.text)
    if not tables:
        raise ValueError("無法解析表格")
    return tables[0]


def fetch(date: str) -> str:
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_f14_output(date, "error", error="日期格式錯誤（YYYY-MM-DD）")

    try:
        df = _fetch_data(date)
    except requests.RequestException as exc:
        logger.error("TWSE STOCK_DAY 請求失敗", exc_info=exc)
        return format_f14_output(date, "error", error="無法連線 TWSE STOCK_DAY")
    except Exception as exc:
        logger.error("解析股票資料失敗", exc_info=exc)
        return format_f14_output(date, "error", error=str(exc))

    row_data = _extract_row(df, date)
    if row_data is None:
        return format_f14_output(date, "failed", error="該日資料不存在（假日或資料延遲）")

    return format_f14_output(date, "success", data=row_data)


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    print(fetch(target))


if __name__ == "__main__":
    main()