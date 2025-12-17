"""
F12 Module: Taiwan Stock Market Daily Turnover (台股每日成交金額)
=========================================================

This module fetches daily stock market turnover data from TWSE (Taiwan Stock Exchange).

Functions:
    fetch(date: str) -> str
        Fetches the daily turnover for the specified date from TWSE.
        Returns a formatted string with the turnover value or error message.

Output Format:
    Success: "YYYY.MM.DD  F12: 台股每日成交金額 : [VALUE] [TWSE]"
    Error:   "F12 錯誤: [ERROR_MESSAGE] [TWSE]"

Dependencies:
    requests >= 2.28.0

Author: F12 Development Team
Version: 1.0.0
Created: 2025-12-17
"""

import logging
import requests
from datetime import datetime
from typing import Optional
import sys
import io

# ============================================================================
# UTF-8 OUTPUT CONFIGURATION
# ============================================================================

# 設定 UTF-8 輸出（解決 Windows 終端亂碼）
# 只在非測試環境下執行（避免與 pytest 衝突）
if sys.platform == 'win32' and not getattr(sys, "frozen", False):
    if 'pytest' not in sys.modules:  # 避免在 pytest 環境中執行
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

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 禁用向上傳播，避免 run.py 環境中的 stdout 問題
logger.propagate = False

# Create console handler if not already present (僅在獨立執行時使用)
if not logger.handlers and __name__ == "__main__":
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create formatter with [F12] prefix
    formatter = logging.Formatter(
        fmt='[F12] %(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

TWSE_URL = "https://www.twse.com.tw/rwd/zh/afterTrading/FMTQIK"
HTTP_TIMEOUT = 10  # seconds
MAX_RETRIES = 1

# 可能的欄位名稱變異（依優先級排序）
COLUMN_VARIANTS = [
    '成交金額(億元)',
    '成交金額',
    '成 交金額',  # 可能有不規則空白
    '金額',
    'Turnover',
    '成交金額(億)',
]

# ============================================================================
# MAIN FUNCTION: fetch()
# ============================================================================

def fetch(date: str) -> str:
    """
    抓取指定日期的台股每日成交金額

    Args:
        date: 查詢日期，格式 YYYY-MM-DD（例如："2025-12-17"）

    Returns:
        統一格式的文字字串：
        - 成功：「2025.12.17  F12: 台股每日成交金額 : 4,567.89 [TWSE]」
        - 失敗：「F12 錯誤: [錯誤訊息] [TWSE]」

    Examples:
        >>> fetch("2025-12-17")
        "2025.12.17  F12: 台股每日成交金額 : 4,567.89 [TWSE]"

        >>> fetch("2025-12-14")  # 週六假日
        "F12 錯誤: 該日無交易資料 [TWSE]"
    """
    logger.info(f"[F12] {date} 開始抓取資料")

    try:
        # 1. 驗證並轉換日期格式
        date_formatted = _validate_and_format_date(date)
        query_date = date.replace("-", "")  # "2025-12-17" → "20251217"

        # 2. 發送 HTTP 請求（使用 JSON API）
        url = f"{TWSE_URL}?date={query_date}&response=json"
        logger.debug(f"[F12] 請求 URL: {url}")

        response = requests.get(url, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        logger.info(f"[F12] HTTP 請求成功，狀態碼 {response.status_code}")

        # 3. 解析 JSON 回應
        data = response.json()

        if data.get('stat') != 'OK':
            logger.warning(f"[F12] API 回應狀態非 OK: {data.get('stat')}")
            return format_error("該日無交易資料")

        # 4. 提取成交金額數據
        turnover_value = _extract_turnover_from_json(data, query_date)

        if turnover_value is None:
            logger.error(f"[F12] 無法提取成交金額數據")
            return format_error("欄位缺失或資料格式異常")

        # 5. 格式化輸出
        result = format_success(date_formatted, turnover_value)
        logger.info(f"[F12] 成功提取成交金額: {turnover_value}")
        logger.info(f"[F12] 回傳結果: {result}")

        return result

    except requests.Timeout:
        logger.error(f"[F12] 連線逾時")
        return format_error("連線逾時")

    except requests.HTTPError as e:
        status_code = e.response.status_code if e.response else "Unknown"
        logger.error(f"[F12] HTTP 錯誤: {status_code}")
        return format_error(f"HTTP {status_code}")

    except requests.ConnectionError:
        logger.error(f"[F12] 網路連線失敗")
        return format_error("網路連線失敗")

    except ValueError as e:
        logger.error(f"[F12] 資料解析失敗: {e}")
        return format_error("資料解析失敗")

    except KeyError as e:
        logger.error(f"[F12] 欄位缺失: {e}")
        return format_error("欄位缺失")

    except IndexError as e:
        logger.error(f"[F12] 索引錯誤: {e}")
        return format_error("資料格式異常")

    except Exception as e:
        logger.error(f"[F12] 未預期錯誤: {str(e)}")
        return format_error(str(e))

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _validate_and_format_date(date: str) -> str:
    """
    驗證並轉換日期格式

    Args:
        date: 輸入日期 YYYY-MM-DD

    Returns:
        輸出日期 YYYY.MM.DD

    Raises:
        ValueError: 日期格式無效
    """
    try:
        # 驗證日期格式
        datetime.strptime(date, "%Y-%m-%d")
        # 轉換為輸出格式
        return date.replace("-", ".")
    except ValueError:
        raise ValueError("日期格式無效")

def _extract_turnover_from_json(data: dict, query_date: str = None) -> Optional[float]:
    """
    從 JSON 回應提取成交金額數值

    Args:
        data: TWSE API JSON 回應
        query_date: 查詢日期 YYYYMMDD 格式（例如："20251217"）

    Returns:
        成交金額數值（億元），若提取失敗則回傳 None
    """
    try:
        # 檢查 fields 找到成交金額的索引
        fields = data.get('fields', [])
        data_rows = data.get('data', [])

        if not fields or not data_rows:
            logger.warning("[F12] JSON 回應缺少 fields 或 data")
            return None

        # 找到「成交金額」欄位的索引
        turnover_index = None
        for idx, field in enumerate(fields):
            if '成交金額' in field:
                turnover_index = idx
                logger.debug(f"[F12] 找到成交金額欄位於索引 {idx}: {field}")
                break

        if turnover_index is None:
            logger.error("[F12] 找不到成交金額欄位")
            return None

        # 如果有提供查詢日期，找到對應日期的資料列
        target_row = None
        if query_date:
            # 將 YYYYMMDD 轉換為民國年格式 YYY/MM/DD
            # 例如：20251217 → 114/12/17
            year = int(query_date[:4]) - 1911  # 2025 - 1911 = 114
            month = query_date[4:6]
            day = query_date[6:8]
            target_date_str = f"{year}/{month.lstrip('0')}/{day.lstrip('0')}"

            logger.debug(f"[F12] 尋找日期: {target_date_str}")

            # 在資料列中找到匹配的日期
            for row in data_rows:
                if len(row) > 0 and row[0] == target_date_str:
                    target_row = row
                    logger.debug(f"[F12] 找到匹配日期: {row[0]}")
                    break

        # 如果沒找到匹配日期，使用最後一筆資料（通常是最新的）
        if target_row is None:
            target_row = data_rows[-1]
            logger.debug(f"[F12] 使用最後一筆資料: {target_row[0]}")

        # 提取成交金額
        if len(target_row) > turnover_index:
            value_str = str(target_row[turnover_index])

            # 移除逗號並轉換為 float
            value_str = value_str.replace(',', '').strip()

            # 處理空值
            if value_str in ['', '-', '--', 'nan', 'None']:
                return None

            # 轉換為億元（原始單位是元）
            value_yuan = float(value_str)
            value_yi = value_yuan / 100000000  # 轉換為億元

            logger.debug(f"[F12] 提取數值: {value_yuan} 元 = {value_yi} 億元")
            return value_yi

    except (ValueError, IndexError, KeyError) as e:
        logger.error(f"[F12] JSON 解析失敗: {e}")
        return None

    return None

def format_success(date: str, value: float) -> str:
    """
    格式化成功輸出

    Args:
        date: 日期 YYYY.MM.DD
        value: 成交金額（億元）

    Returns:
        統一格式字串
    """
    # 格式化數值：千分位逗號 + 兩位小數
    value_formatted = f"{value:,.2f}"
    return f"{date}  F12: 台股每日成交金額 : {value_formatted} [TWSE]"

def format_error(error_msg: str) -> str:
    """
    格式化錯誤輸出

    Args:
        error_msg: 錯誤訊息

    Returns:
        統一格式錯誤字串
    """
    return f"F12 錯誤: {error_msg} [TWSE]"

# ============================================================================
# COMMAND LINE INTERFACE (獨立測試用)
# ============================================================================

def main():
    """
    命令列介面 - 供獨立測試使用

    Usage:
        python f12_openspec_dev.py                    # 查詢今天
        python f12_openspec_dev.py 2025-12-17         # 查詢指定日期
    """
    import sys

    if len(sys.argv) > 1:
        test_date = sys.argv[1]
    else:
        test_date = datetime.now().strftime("%Y-%m-%d")

    print(f"\n{'='*70}")
    print(f"  F12 模組測試 - 台股每日成交金額")
    print(f"{'='*70}")
    print(f"  查詢日期: {test_date}")
    print(f"{'='*70}\n")

    result = fetch(test_date)
    print(f"結果: {result}\n")

if __name__ == '__main__':
    main()
