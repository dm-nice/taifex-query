"""
f11_fetcher.py
F11: 台灣股票大盤當日收盤價抓取模組

功能：
- 利用 TWSE 的即時行情 API 取得台灣加權指數 (TAIEX) 收盤價
- 格式化為 v5.0 統一文字輸出
- 處理網路錯誤、資料缺失以及非交易日情況

輸出格式：
2025.12.10  F11: 台灣股票大盤當日收盤價 : 28,400.73 [mis.twse.com.tw]
"""

import sys
import io
import logging
from typing import Dict, Optional
from datetime import datetime

import requests

# 設定 UTF-8 輸出（解決 Windows 終端亂碼）
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

MODULE_ID = "f11"
MODULE_NAME = "f11_fetcher"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)

TWSE_SOURCE = "mis.twse.com.tw"
TWSE_API = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"


def format_f11_output(
    date: str,
    status: str,
    data: Optional[Dict] = None,
    error: Optional[str] = None,
) -> str:
    formatted_date = date.replace("-", ".")

    if status == "success" and data:
        value = data.get("closing")
        source = data.get("source", TWSE_SOURCE)
        actual_date = data.get("actual_date")
        actual_label = ""
        if actual_date and actual_date != date:
            actual_label = f" (實際: {actual_date})"
        return f"{formatted_date}  F11: 台灣股票大盤當日收盤價{actual_label} : {value} [{source}]"

    error_msg = error or "未知錯誤"
    return f"{formatted_date}  F11 錯誤: {error_msg} [TAIFEX]"


def fetch(date: str) -> str:
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_f11_output(date, "error", error="日期格式錯誤（請使用 YYYY-MM-DD）")

    try:
        params = {"ex_ch": "tse_t00.tw", "json": "1", "delay": "0"}
        response = requests.get(TWSE_API, params=params, timeout=10)

        if response.status_code != 200:
            return format_f11_output(date, "error", error=f"HTTP {response.status_code}")

        payload = response.json()
        msg_array = payload.get("msgArray")

        if not msg_array:
            stat = payload.get("stat", "未知")
            message = payload.get("rtmessage", "無法取得資料")
            return format_f11_output(
                date,
                "error",
                error=f"TWSE API 無資料（{stat}: {message}）",
            )

        info = msg_array[0]
        closing_str = info.get("z")
        payload_date = info.get("d")

        if not closing_str or not payload_date:
            return format_f11_output(date, "error", error="TWSE API 回傳資料不完整")

        closing_value = float(closing_str.replace(",", ""))
        closing_formatted = f"{closing_value:,.2f}"

        data_date = datetime.strptime(payload_date, "%Y%m%d").strftime("%Y-%m-%d")

        return format_f11_output(
            date,
            "success",
            data={
                "closing": closing_formatted,
                "source": TWSE_SOURCE,
                "actual_date": data_date,
            },
        )

    except requests.RequestException as exc:
        logger.error("TWSE API 請求失敗", exc_info=exc)
        return format_f11_output(date, "error", error="無法連線 TWSE API")
    except Exception as exc:
        logger.error("處理資料時發生例外", exc_info=exc)
        return format_f11_output(date, "error", error=str(exc))


def main() -> None:
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = datetime.now().strftime("%Y-%m-%d")
    print(fetch(target))


if __name__ == "__main__":
    main()
