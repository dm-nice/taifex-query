"""
f16_fetcher.py
F16: 台積電當日成交股數

功能：
- 讀取 TWSE STOCK_DAY 的台積電資料表，以查詢日的 row 採集 `成交股數`
- 將數字移除千分號，轉為整數，再附上千分位格式與 `張` 單位
- 若資料缺失（假日、延遲、欄位變動）回傳 `failed`，網路/解析錯誤回傳 `error`

輸出格式：
2025.12.11  F16: 台積電當日成交股數 : 31,018,417 張 [twse.com.tw]
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

# Windows 環境強制使用 UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

MODULE_ID = "f16"
MODULE_NAME = "f16_fetcher"
SOURCE = "twse.com.tw"
STOCK_URL = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
REQUEST_TIMEOUT = 20

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


def format_f16_output(
    date: str,
    status: str,
    data: Optional[Dict] = None,
    error: Optional[str] = None,
) -> str:
    formatted_date = date.replace("-", ".")

    if status == "success" and data:
        value = data.get("turnover")
        source = data.get("source", SOURCE)
        return f"{formatted_date}  F16: 台積電當日成交股數 : {value} 張 [{source}]"

    error_msg = error or "未知錯誤"
    return f"{formatted_date}  F16 錯誤: {error_msg} [{SOURCE}]"


def _sanitize_integer(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    cleaned = re.sub(r"[^0-9]", "", str(value))
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except ValueError:
        return None


def _convert_roc_date(value: str) -> Optional[str]:
    if not value:
        return None
    value = str(value).strip()
    parts = value.split("/")
    if len(parts) == 3:
        try:
            year = int(parts[0]) + 1911
            return datetime(year, int(parts[1]), int(parts[2])).strftime("%Y-%m-%d")
        except ValueError:
            pass
    try:
        return datetime.strptime(value, "%Y/%m/%d").strftime("%Y-%m-%d")
    except ValueError:
        return None
    return None


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    flat_columns = []
    for col in df.columns:
        if isinstance(col, tuple):
            flat_columns.append(col[-1])
        else:
            flat_columns.append(col)
    df.columns = [str(col).strip() for col in flat_columns]
    return df


def _extract_row(df: pd.DataFrame, target: str) -> Optional[Dict]:
    df = _flatten_columns(df).copy()
    if "日期" not in df.columns or "成交股數" not in df.columns:
        return None

    df["normalized"] = df["日期"].apply(_convert_roc_date)
    row = df[df["normalized"] == target]
    if row.empty:
        return None

    amount = _sanitize_integer(row.iloc[0]["成交股數"])
    if amount is None:
        return None

    return {
        "turnover": f"{amount:,}",
        "source": SOURCE,
        "actual_date": row.iloc[0]["normalized"],
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
        return format_f16_output(date, "error", error="日期格式錯誤（YYYY-MM-DD）")

    try:
        df = _fetch_data(date)
    except requests.RequestException as exc:
        logger.error("TWSE STOCK_DAY 請求失敗", exc_info=exc)
        return format_f16_output(date, "error", error="無法連線 TWSE STOCK_DAY")
    except Exception as exc:
        logger.error("解析股票資料失敗", exc_info=exc)
        return format_f16_output(date, "error", error=str(exc))

    row_data = _extract_row(df, date)
    if row_data is None:
        return format_f16_output(date, "failed", error="該日資料不存在（假日或資料延遲）")

    return format_f16_output(date, "success", data=row_data)


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    print(fetch(target))


if __name__ == "__main__":
    main()
