"""
f17_fetcher_dev.py
F17: 台灣股票外資及陸資買賣差額

功能：
- 擷取 TWSE 針對三大法人買賣金額的 BFI82U JSON（單位：元）
- 找出「外資及陸資」身份的買賣差額並轉為億元，輸出兩位小數與符號
- 確保失敗原因（假日、欄位變動、網路錯誤）會回傳 `failed` / `error`

輸出格式：
2025.12.11  F17: 台灣股票外資及陸資買賣差額 : -189.77 億元 [twse.com.tw]
"""

from __future__ import annotations

import io
import logging
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

# 設定 UTF-8 輸出（解決 Windows 終端亂碼，PyInstaller 已處理打包的情境）
# 只在尚未包裝時才進行包裝，避免重複包裝導致 I/O 錯誤
if sys.platform == 'win32' and not getattr(sys, "frozen", False):
    if not hasattr(sys.stdout, '_wrapped_for_utf8') and hasattr(sys.stdout, 'buffer'):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            sys.stdout._wrapped_for_utf8 = True
        except (AttributeError, ValueError):
            pass
    if not hasattr(sys.stderr, '_wrapped_for_utf8') and hasattr(sys.stderr, 'buffer'):
        try:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
            sys.stderr._wrapped_for_utf8 = True
        except (AttributeError, ValueError):
            pass

MODULE_ID = "f17"
MODULE_NAME = "f17_fetcher"
SOURCE = "https://www.twse.com.tw/fund/BFI82U"
API_URL = "https://www.twse.com.tw/fund/BFI82U"
REQUEST_TIMEOUT = 20
REFERER = "https://www.twse.com.tw/zh/trading/foreign/bfi82u.html"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


def format_f17_output(
    date: str,
    status: str,
    data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
) -> str:
    formatted_date = date.replace("-", ".")

    if status == "success" and data:
        diff = data.get("difference")
        source = data.get("source", SOURCE)
        return f"{formatted_date}  F17: 台灣股票外資及陸資買賣差額 : {diff} 億元 [{source}]"

    error_msg = error or "未知錯誤"
    return f"{formatted_date}  F17 錯誤: {error_msg} [{SOURCE}]"


def _parse_numeric(value: Any) -> Optional[int]:
    if value is None:
        return None

    raw = str(value).strip()
    if not raw:
        return None

    neg = False
    if raw.startswith("(") and raw.endswith(")"):
        neg = True
        raw = raw[1:-1]

    raw = raw.replace("−", "-")
    if raw.startswith("-"):
        neg = True
        raw = raw[1:]

    cleaned = re.sub(r"[^0-9]", "", raw)
    if not cleaned:
        return None

    try:
        numeric = int(cleaned)
    except ValueError:
        return None

    return -numeric if neg else numeric


def _format_billions(value: int) -> str:
    billions = value / 100_000_000
    return f"{billions:+,.2f}"


def _normalize_label(label: str) -> str:
    return re.sub(r"[\s　（）()]+", "", label)


def _find_difference_index(fields: List[str]) -> Optional[int]:
    normalized = [_normalize_label(str(f)) for f in fields]

    for idx, field in enumerate(normalized):
        if "買賣差額" in field:
            return idx
    return None


def _find_foreign_row(data: List[List[Any]]) -> Optional[List[Any]]:
    for row in data:
        if not row:
            continue
        label = _normalize_label(str(row[0]))
        if "外資" in label and "陸資" in label:
            return row
    return None


def _parse_response_date(raw_date: Optional[str]) -> Optional[str]:
    if not raw_date:
        return None
    try:
        return datetime.strptime(raw_date, "%Y%m%d").strftime("%Y-%m-%d")
    except ValueError:
        return None


def fetch(date: str) -> str:
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_f17_output(date, "error", error="日期格式錯誤（YYYY-MM-DD）")

    params = {
        "response": "json",
        "date": date.replace("-", ""),
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": REFERER,
    }

    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        logger.error("TWSE BFI82U 請求失敗", exc_info=exc)
        return format_f17_output(date, "error", error="無法連線 TWSE BFI82U")
    except ValueError as exc:
        logger.error("BFI82U 回傳無效 JSON", exc_info=exc)
        return format_f17_output(date, "error", error="TWSE 回傳格式解析失敗")

    if payload.get("stat") != "OK":
        return format_f17_output(date, "failed", error=f"API stat={payload.get('stat')}")

    fields = payload.get("fields") or []
    data = payload.get("data") or []
    if not data:
        return format_f17_output(date, "failed", error="TWSE 未提供資料（可能是假日或停開市）")

    difference_index = _find_difference_index(fields)
    if difference_index is None:
        return format_f17_output(date, "failed", error="找不到買賣差額欄位")

    row = _find_foreign_row(data)
    if row is None or difference_index >= len(row):
        return format_f17_output(date, "failed", error="找不到外資及陸資差額資料")

    parsed = _parse_numeric(row[difference_index])
    if parsed is None:
        return format_f17_output(date, "failed", error="差額欄位內容非數值")

    formatted_value = _format_billions(parsed)
    actual_date = _parse_response_date(payload.get("date")) or date

    return format_f17_output(actual_date, "success", data={
        "difference": formatted_value,
        "source": SOURCE,
    })


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    print(fetch(target))


if __name__ == "__main__":
    main()
