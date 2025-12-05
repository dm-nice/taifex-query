"""
_template.py - 模組開發範本（統一文字格式 v4.0）

這是給外包開發者的標準範本。
請複製此檔案，並將檔名修改為指定的模組名稱（例如 f02_fetcher_dev.py）。

開發規範：
1. 檔名必須與 MODULE_ID 對應（例如：f02_fetcher_dev.py → MODULE_ID = "f02"）
2. 必須實作 fetch(date: str) -> str 函式
3. 必須回傳統一文字格式（不可拋出例外）
4. 詳細規範請參考：dev/共同開發規範書_V1.md

統一文字格式：
- 成功: [ YYYY.MM.DD  FXX{描述}   source: {來源} ]
- 失敗: [ YYYY.MM.DD  FXX 錯誤: {錯誤訊息}   source: {來源} ]
"""

import sys
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, Optional

# 模組識別
MODULE_ID = "template"  # 🔧 修改為您的模組代號（小寫，如 f02, f03）
MODULE_NAME = "_template"  # 🔧 修改為檔名（不含 .py）
SOURCE = "TAIFEX"  # 🔧 修改為您的資料來源


def format_template_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
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
    module_code = MODULE_ID.upper()  # template → TEMPLATE

    if status == "success" and data:
        # 🔧 根據您的模組需求客製化這裡的輸出格式
        # 範例：顯示多方、空方口數
        long_pos = data.get("long_position", 0)
        short_pos = data.get("short_position", 0)
        net_pos = long_pos - short_pos

        return f"[ {date_formatted}  {module_code}測試模組 淨額 {net_pos:,} 口（多方 {long_pos:,}，空方 {short_pos:,}）   source: {SOURCE} ]"
    else:
        error_msg = error or "未知錯誤"
        return f"[ {date_formatted}  {module_code} 錯誤: {error_msg}   source: {SOURCE} ]"


def fetch(date: str) -> str:
    """
    抓取指定日期的資料

    Args:
        date: 查詢日期，格式 YYYY-MM-DD

    Returns:
        統一格式的文字字串
    """
    # 1. 驗證日期格式
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_template_output(date, "error", error="日期格式錯誤，請使用 YYYY-MM-DD")

    try:
        # 2. 發送 HTTP 請求
        # 🔧 修改為實際的 API URL
        url = f"https://example.com/api?date={date}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # 3. 解析資料
        # 🔧 根據資料源類型選擇解析方式：
        # - HTML 表格: tables = pd.read_html(response.text)
        # - JSON: data = response.json()
        # - CSV: df = pd.read_csv(...)

        # 範例：解析 HTML 表格
        tables = pd.read_html(response.text)
        if len(tables) == 0:
            return format_template_output(date, "failed", error="該日無交易資料（可能是假日或休市日）")

        # 4. 提取目標資料
        df = tables[0]
        # 🔧 實作您的資料提取邏輯
        # ...

        # 5. 回傳成功結果（範例數據）
        data = {
            "long_position": 12345,  # 🔧 替換為實際欄位
            "short_position": 6789,
        }
        return format_template_output(date, "success", data=data)

    except requests.Timeout:
        return format_template_output(date, "error", error="連線逾時，請檢查網路連線")

    except requests.HTTPError as e:
        return format_template_output(date, "error", error=f"HTTP 錯誤 {e.response.status_code}")

    except Exception as e:
        return format_template_output(date, "error", error=f"未預期的錯誤: {str(e)}")


def main():
    """獨立測試用"""
    test_date = sys.argv[1] if len(sys.argv) > 1 else '2025-12-03'
    result = fetch(test_date)
    print(result)


if __name__ == '__main__':
    main()
