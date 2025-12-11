"""
f15_fetcher_dev.py
F15: 台積電當日漲跌價差

功能：
- 讀取 TWSE STOCK_DAY 的台積電資料表，從查詢日 row 採集 `漲跌價差`
- 將結果保留兩位小數並帶上符號（+/-），作為統一 v5 輸出
- 若該日是假日或資料延遲則回報 `failed`，網路/解析錯誤回報 `error`

輸出格式：
2025.12.11  F15: 台積電當日漲跌價差 : +20.00 點 [twse.com.tw]
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

MODULE_ID = "f15"
MODULE_NAME = "f15_fetcher"
SOURCE = "twse.com.tw"
STOCK_URL = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
REQUEST_TIMEOUT = 20

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


def format_f15_output(
    date: str,
    status: str,
    data: Optional[Dict] = None,
    error: Optional[str] = None,
) -> str:
    formatted_date = date.replace("-", ".")

    if status == "success" and data:
        change = data.get("change")
        source = data.get("source", SOURCE)
        return f"{formatted_date}  F15: 台積電當日漲跌價差 : {change} 點 [{source}]"

    error_msg = error or "未知錯誤"
    return f"{formatted_date}  F15 錯誤: {error_msg} [{SOURCE}]"


def _sanitize_number(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    cleaned = re.sub(r"[^0-9+\.-]", "", str(value))
    if not cleaned or cleaned in {"", "-", "+"}:
        return None
    try:
        return float(cleaned)
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
    if "日期" not in df.columns or "收盤價" not in df.columns:
        return None

    df["normalized"] = df["日期"].apply(_convert_roc_date)
    df["closing"] = df["收盤價"].apply(_sanitize_number)
    df = df.dropna(subset=["normalized", "closing"]).copy()
    if df.empty:
        return None

    df.sort_values(by="normalized", inplace=True)
    df.reset_index(drop=True, inplace=True)
    matches = df[df["normalized"] == target]
    if matches.empty:
        return None

    current = matches.iloc[0]
    change_value: Optional[float] = None
    column_change = _sanitize_number(current.get("漲跌價差"))
    if column_change is not None:
        change_value = column_change
    else:
        idx = matches.index[0]
        if idx > 0:
            previous = df.iloc[idx - 1]["closing"]
            if previous is not None:
                change_value = current["closing"] - previous
            else:
                change_value = None
        else:
            change_value = None

    if change_value is None:
        return None

    return {
        "change": f"{change_value:+,.2f}",
        "source": SOURCE,
        "actual_date": current["normalized"],
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
        return format_f15_output(date, "error", error="日期格式錯誤（YYYY-MM-DD）")

    try:
        df = _fetch_data(date)
    except requests.RequestException as exc:
        logger.error("TWSE STOCK_DAY 請求失敗", exc_info=exc)
        return format_f15_output(date, "error", error="無法連線 TWSE STOCK_DAY")
    except Exception as exc:
        logger.error("解析股票資料失敗", exc_info=exc)
        return format_f15_output(date, "error", error=str(exc))

    row_data = _extract_row(df, date)
    if row_data is None:
        return format_f15_output(date, "failed", error="該日資料不存在（假日或資料延遲）")

    return format_f15_output(date, "success", data=row_data)


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    print(fetch(target))


if __name__ == "__main__":
    main()