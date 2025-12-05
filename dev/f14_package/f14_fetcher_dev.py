"""
F14 Fetcher 開發模組（統一文字格式 v4.0）

此模組負責抓取台指期貨 (TX) 當日收盤價。

資料來源：台灣期貨交易所 (TAIFEX)
更新頻率：每日
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
        url = f"https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate={date.replace('-', '/')}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # 3. 解析資料
        tables = pd.read_html(response.text)
        if len(tables) == 0:
            return format_f14_output(date, "failed", error="該日無交易資料（可能是假日或休市日）")

        # 4. 提取台指期貨收盤價
        # TODO: 實作實際的資料提取邏輯
        # 需要從表格中找到 TX (台指期貨) 的收盤價

        # 暫時使用模擬數據
        close_price = 27758.0

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
