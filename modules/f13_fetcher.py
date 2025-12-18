"""
f13_fetcher_dev.py
F13: 台灣加權股價指數與 20 日均線距離

功能：
- 以 TWSE 的 MI_INDEX API 擷取台灣加權指數（TAIEX）收盤價
- 計算查詢日與過去 20 個交易日收盤價的算術平均距離
- 處理假日/資料缺漏、網路錯誤與 API 回傳變化

輸出格式：
2025.12.11  F13: 台灣股票大盤與 20 日均線距離 : -45.20 點 [twse.com.tw]
"""

from __future__ import annotations

import io
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

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

MODULE_ID = "f13"
MODULE_NAME = "f13_fetcher"
SOURCE = "https://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX.html"
TWSE_MI_URL = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX"  # API endpoint
REQUEST_TIMEOUT = 15
WINDOW_SIZE = 20
MAX_LOOKBACK_DAYS = 60
TARGET_KEYWORDS = (
    "發行量加權股價指數",
    "加權股價指數",
    "加權指數",
    "TAIEX",
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


def format_f13_output(
    date: str,
    status: str,
    data: Optional[Dict] = None,
    error: Optional[str] = None,
) -> str:
    formatted_date = date.replace("-", ".")

    if status == "success" and data:
        distance = data.get("distance", "0.00")
        source = data.get("source", SOURCE)
        actual_date = data.get("actual_date")
        actual_label = ""
        if actual_date and actual_date != date:
            actual_label = f" (實際: {actual_date})"
        return (
            f"{formatted_date}  F13: 台灣加權股價指數與 20 日均線距離{actual_label} : {distance} 點 [{source}]"
        )

    error_msg = error or "未知錯誤"
    return f"{formatted_date}  F13 錯誤: {error_msg} [{SOURCE}]"


def _normalize_date(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    cleaned = value.replace("/", "").replace("-", "").strip()
    if len(cleaned) == 8:
        try:
            return datetime.strptime(cleaned, "%Y%m%d").strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def _find_closing_index(fields: List[str]) -> Optional[int]:
    for idx, field in enumerate(fields):
        lowered = str(field).replace(" ", "").lower()
        if "收盤" in lowered:
            return idx
    return None


def _extract_closing(payload: Dict, fallback_date: str) -> Optional[Tuple[float, str]]:
    if payload.get("stat") != "OK":
        return None

    tables = payload.get("tables") or []
    for table in tables:
        fields = table.get("fields") or []
        closing_idx = _find_closing_index(fields)
        if closing_idx is None:
            continue

        for row in table.get("data") or []:
            if not isinstance(row, list) or len(row) <= closing_idx:
                continue

            label = str(row[0])
            if not any(keyword in label for keyword in TARGET_KEYWORDS):
                continue

            closing_value = str(row[closing_idx]).strip()
            if not closing_value or closing_value in {"-", "--"}:
                continue

            try:
                numeric = float(closing_value.replace(",", ""))
            except ValueError:
                continue

            actual = _normalize_date(payload.get("date")) or fallback_date
            return numeric, actual

    return None


def _build_url(date_str: str) -> Tuple[str, Dict[str, str]]:
    payload_date = date_str.replace("-", "")
    params = {"response": "json", "date": payload_date, "type": "IND"}
    return TWSE_MI_URL, params


def _fetch_closing(date_str: str, session: requests.Session) -> Optional[Tuple[float, str]]:
    url, params = _build_url(date_str)
    response = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    return _extract_closing(payload, date_str)


def _collect_closings(date_str: str, session: requests.Session) -> Tuple[List[float], Optional[str], bool]:
    closings: List[float] = []
    actual_target_date: Optional[str] = None
    target_found = False
    cursor = datetime.strptime(date_str, "%Y-%m-%d")
    attempts = 0

    while len(closings) < WINDOW_SIZE and attempts < MAX_LOOKBACK_DAYS:
        current = cursor.strftime("%Y-%m-%d")
        try:
            result = _fetch_closing(current, session)
        except requests.RequestException:
            raise

        if result:
            value, actual = result
            closings.append(value)
            if current == date_str:
                target_found = True
                actual_target_date = actual

        cursor -= timedelta(days=1)
        attempts += 1

    return closings, actual_target_date, target_found


def fetch(date: str) -> str:
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_f13_output(date, "error", error="日期格式錯誤（請使用 YYYY-MM-DD）")

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
        }
    )

    try:
        closings, actual_target_date, target_found = _collect_closings(date, session)
    except requests.RequestException as exc:
        logger.error("TWSE MI_INDEX 請求失敗", exc_info=exc)
        return format_f13_output(date, "error", error="無法連線 TWSE MI_INDEX")
    finally:
        session.close()

    if not target_found:
        return format_f13_output(
            date,
            "failed",
            error="該日無交易資料（可能是假日或尚未公布）",
        )

    if len(closings) < WINDOW_SIZE:
        return format_f13_output(
            date,
            "failed",
            error="過去 20 個交易日資料不足，無法計算均線距離",
        )

    target_closing = closings[0]
    ma20 = sum(closings[:WINDOW_SIZE]) / WINDOW_SIZE
    distance = ma20 - target_closing
    distance_str = f"{distance:,.2f}"

    data = {
        "distance": distance_str,
        "source": SOURCE,
        "actual_date": actual_target_date or date,
        "ma20": f"{ma20:,.2f}",
        "closing": f"{target_closing:,.2f}",
    }

    return format_f13_output(date, "success", data=data)


def main() -> None:
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = datetime.now().strftime("%Y-%m-%d")
    print(fetch(target))


if __name__ == "__main__":
    main()