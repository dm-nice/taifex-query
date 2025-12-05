"""
_template.py - F14 模組開發範本（統一文字格式 v4.0）

這是 F14 模組的標準範本。

開發規範：
1. MODULE_ID = "f14"（固定）
2. 必須實作 fetch(date: str) -> str 函式
3. 必須回傳統一文字格式（不可拋出例外）
4. 詳細規範請參考：../共同開發規範書_V1.md 和 f14_fetcher_spec.md

統一文字格式：
- 成功: [ YYYY.MM.DD  F14台指期貨收盤價 27,758.0   source: TAIFEX ]
- 失敗: [ YYYY.MM.DD  F14 錯誤: {錯誤訊息}   source: TAIFEX ]
"""

import sys
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, Optional

# 模組識別
MODULE_ID = "f14"
MODULE_NAME = "f14_fetcher_dev"
SOURCE = "TAIFEX"


def format_f14_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
    """
    格式化輸出為統一文字格式

    Args:
        date: 日期 (YYYY-MM-DD)
        status: 狀態 ("success" / "failed" / "error")
        data: 成功時的資料字典
        error: 失敗時的錯誤訊息

    Returns:
        統一格式文字字串
    """
    date_formatted = date.replace("-", ".")  # 2025-12-03 → 2025.12.03

    if status == "success" and data:
        close_price = data.get("台指期貨收盤價", 0.0)
        return f"[ {date_formatted}  F14台指期貨收盤價 {close_price:,.1f}   source: {SOURCE} ]"
    else:
        error_msg = error or "未知錯誤"
        return f"[ {date_formatted}  F14 錯誤: {error_msg}   source: {SOURCE} ]"


def fetch(date: str) -> str:
    """
    抓取指定日期的台指期貨收盤價

    Args:
        date: 查詢日期，格式 YYYY-MM-DD

    Returns:
        統一格式的文字字串
    """
    # 1. 驗證日期格式
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_f14_output(date, "error", error="日期格式錯誤，請使用 YYYY-MM-DD")

    try:
        # 2. 發送 HTTP 請求
        # 替換為實際的 TAIFEX URL
        url = f"https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate={date.replace('-', '/')}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # 3. 解析資料
        tables = pd.read_html(response.text)
        if len(tables) == 0:
            return format_f14_output(date, "failed", error="該日無交易資料（可能是假日或休市日）")

        # 4. 提取台指期貨收盤價
        # 🔧 實作您的資料提取邏輯
        # 尋找 TX (台指期貨) 的收盤價
        # ...

        # 範例：假設找到收盤價
        close_price = 27758.0  # 🔧 替換為實際提取的值

        # 5. 回傳成功結果
        data = {
            "台指期貨收盤價": close_price
        }
        return format_f14_output(date, "success", data=data)

    except requests.Timeout:
        return format_f14_output(date, "error", error="連線逾時，請檢查網路連線")

    except requests.HTTPError as e:
        return format_f14_output(date, "error", error=f"HTTP 錯誤 {e.response.status_code}")

    except Exception as e:
        return format_f14_output(date, "error", error=f"未預期的錯誤: {str(e)}")


def main():
    """獨立測試用"""
    test_date = sys.argv[1] if len(sys.argv) > 1 else '2025-12-03'
    result = fetch(test_date)
    print(result)


if __name__ == '__main__':
    main()
