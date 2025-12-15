"""
f15_fetcher_dev.py - 台積電當日漲跌價差抓取模組 v1.0

【模組功能】
- 從 TWSE 台灣證券交易所網站抓取台積電 (2330) 股票資料
- 提供統一的 fetch(date: str) -> str 介面
- 返回當日漲跌價差資訊
- 完整的錯誤處理和日誌記錄

【主要入口】
- fetch(date: str) -> str
  入參: 日期字串 (YYYY-MM-DD 格式)
  返值: 統一格式的文字結果

  成功範例: "2025.12.15  F15: 台積電當日漲跌價差 : -30 元 [TWSE]"
  失敗範例: "F15 錯誤: 該日無交易資料（可能是假日或休市日） [TWSE]"
  異常範例: "F15 錯誤: 連線逾時，請檢查網路連線 [TWSE] (2025-12-15 14:30:45, timeout=30s)"

【資料來源】
- API: https://www.twse.com.tw/exchangeReport/STOCK_DAY
- 參數: response=json&date=YYYYMMDD&stockNo=2330
- 資料欄位:
  - 日期: 交易日期 (114/12/15 格式)
  - 開盤價: 當日開盤價格
  - 最高價: 當日最高價格
  - 最低價: 當日最低價格
  - 收盤價: 當日收盤價格
  - 漲跌價差: 相對前日的價格變化 (+30, -30, X)

【依賴套件】
- requests >= 2.28.0 (HTTP 請求)

【版本歷史】
- v1.0: 初始版本，基於 F01 v7.0 架構

【錯誤代碼表】
| 錯誤類型 | 原因 | 解決方案 |
|---------|------|--------|
| 日期格式錯誤 | 輸入格式非 YYYY-MM-DD | 檢查日期格式 |
| 連線逾時 | 網路延遲或 TWSE 無回應 | 檢查網路、稍後重試 |
| HTTP 錯誤 | 伺服器返回 4xx/5xx | 檢查 API 端點 |
| JSON 解析失敗 | 資料格式改變 | 更新解析邏輯 |
| 無交易資料 | 假日或休市日 | 改查交易日期 |

【日誌配置】
模組使用 Python logging，預設級別為 INFO
- INFO: 主要操作（開始抓取、完成、失敗）
- DEBUG: 流程分支（API調用、資料解析）
- ERROR: 無法恢復的異常
"""

import io
import logging
import sys
from datetime import datetime
from typing import Optional, TypedDict

import requests


class StockDataDict(TypedDict):
    """股票資料字典結構（用於 format_f15_output 的 data 參數）

    用於表示從 TWSE 抓取的台積電股票資料。
    """
    price_change: str          # 漲跌價差 (必須，可能是 +30, -30, 或 X)
    open_price: str           # 開盤價
    high_price: str           # 最高價
    low_price: str            # 最低價
    close_price: str          # 收盤價
    source: str               # 資料來源（通常為 "TWSE"）


class ErrorContextDict(TypedDict, total=False):
    """錯誤上下文字典結構（用於 format_f15_output 的 context 參數）

    total=False 表示所有欄位都是可選的，因為不同錯誤類型記錄不同上下文。
    """
    timeout: int              # 逾時秒數 (requests.Timeout 時)
    status_code: int          # HTTP 狀態碼 (requests.HTTPError 時)
    step: str                 # 失敗步驟名稱 (自訂異常時)
    error_type: str           # 異常類型名稱


class FetchResultDict(TypedDict, total=False):
    """fetch() 和提取函數的結果字典結構

    用於內部返回複雜的資料結構。包含成功和失敗情況。
    """
    module: str               # 模組 ID ("f15")
    date: str                 # 查詢日期
    status: str               # "success" / "failed" / "error"
    summary: str              # 成功時的摘要訊息
    error: str                # 失敗時的錯誤訊息
    data: StockDataDict       # 成功時的資料
    source: str               # 資料來源


# 設定 UTF-8 輸出（解決 Windows 終端亂碼，PyInstaller 已處理打包的情境）
# 只在尚未包裝時才進行包裝，避免重複包裝導致 I/O 錯誤
if sys.platform == 'win32' and not getattr(sys, "frozen", False):
    if not hasattr(sys.stdout, '_wrapped_for_utf8'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stdout._wrapped_for_utf8 = True
    if not hasattr(sys.stderr, '_wrapped_for_utf8'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        sys.stderr._wrapped_for_utf8 = True

# 模組識別
MODULE_ID = "f15"
MODULE_NAME = "f15_fetcher"

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def format_f15_output(
    date: str,
    status: str,
    data: Optional[StockDataDict] = None,
    error: Optional[str] = None,
    timestamp: Optional[str] = None,
    context: Optional[ErrorContextDict] = None
) -> str:
    """
    格式化 F15 輸出為統一文字格式 v1.0

    【功能說明】
    將抓取結果（成功/失敗/異常）轉換為標準化的文字格式。
    支援多層級的錯誤上下文記錄，便於問題追蹤和日誌分析。

    【參數說明】
    Args:
        date (str): 查詢日期 (YYYY-MM-DD 格式)
        status (str): 操作狀態，可選值：
                    - "success": 成功抓取資料
                    - "failed": 可恢復的失敗（假日、無資料等）
                    - "error": 無法恢復的異常（網路、解析等）
        data (Optional[Dict]): 成功時的資料字典
        error (Optional[str]): 失敗或異常時的錯誤訊息
        timestamp (Optional[str]): 異常發生時間戳
        context (Optional[Dict]): 異常上下文字典

    【返回值】
    Returns:
        str: 格式化後的統一文字字串

        格式化規則:
        1. 成功: "{date}  F15: 台積電當日漲跌價差 : {change} 元 [TWSE]"
        2. 失敗: "F15 錯誤: {error} [TWSE]"
        3. 異常: "F15 錯誤: {error} [TWSE] ({timestamp})"
        4. 異常+上下文: "F15 錯誤: {error} [TWSE] ({timestamp}, {context})"
    """
    if status == "success" and data:
        price_change = data.get("price_change", "0")
        source = data.get("source", "TWSE")

        # 處理漲跌價差格式
        if price_change == "X" or price_change == "0":
            change_display = "0"
        else:
            change_display = price_change

        # v1.0 成功格式：增加日期前綴
        formatted_date = date.replace("-", ".")
        return f"{formatted_date}  F15: 台積電當日漲跌價差 : {change_display} 元 [TWSE]"
    else:
        error_msg = error or "未知錯誤"
        # v1.0 錯誤格式
        result = f"F15 錯誤: {error_msg} [TWSE]"

        # 增加時間戳和上下文後綴
        suffix = ""
        if timestamp:
            suffix += f" ({timestamp}"

        if context:
            # 上下文格式化
            context_parts = []
            for k, v in context.items():
                if k == "timeout":
                    context_parts.append(f"{k}={v}s")  # timeout 特殊處理：加 s 單位
                else:
                    context_parts.append(f"{k}={v}")    # 其他欄位直接拼接

            if suffix:  # 已有時間戳
                suffix += ", " + ", ".join(context_parts)
            else:
                suffix += " (" + ", ".join(context_parts)

        if suffix:
            if not suffix.endswith(")"):
                suffix += ")"
            result += suffix

        # 日誌記錄
        if status == "failed":
            logger.warning(f"F15 失敗: {error_msg}")
        elif status == "error":
            logger.error(f"F15 錯誤: {error_msg} (時間戳: {timestamp}, 上下文: {context})")

        return result


def parse_price_change(value: str) -> str:
    """
    解析漲跌價差值

    Args:
        value: 原始值 (例如 "+30", "-30", "X", "30")

    Returns:
        格式化後的值 ("+30", "-30", "0")
    """
    if not value or value.strip() == "":
        return "0"

    value = value.strip()

    # X 表示不比價（新上市或特殊情況）
    if value == "X":
        return "0"

    # 如果已經有符號，直接返回
    if value.startswith("+") or value.startswith("-"):
        return value

    # 數字視為無變化
    try:
        float(value)
        return "0"
    except ValueError:
        return "0"


def convert_date_format(date_str: str) -> str:
    """
    將 YYYY-MM-DD 格式轉換為 TWSE API 需要的 YYYYMMDD 格式

    Args:
        date_str: YYYY-MM-DD 格式的日期字串

    Returns:
        YYYYMMDD 格式的日期字串
    """
    return date_str.replace("-", "")


def convert_roc_date_to_ad(roc_date: str) -> str:
    """
    將民國年日期轉換為西元年

    Args:
        roc_date: 民國年格式 "114/12/15"

    Returns:
        西元年格式 "2025-12-15"
    """
    try:
        parts = roc_date.split("/")
        if len(parts) == 3:
            year = int(parts[0]) + 1911  # 民國年 + 1911 = 西元年
            month = parts[1].zfill(2)
            day = parts[2].zfill(2)
            return f"{year}-{month}-{day}"
    except Exception:
        pass
    return ""


def fetch_stock_data(date: str, timeout: int = 30) -> FetchResultDict:
    """
    從 TWSE API 抓取台積電股票資料

    Args:
        date: 查詢日期 (YYYY-MM-DD)
        timeout: 請求逾時秒數（預設 30 秒）

    Returns:
        FetchResultDict: 包含狀態和資料的字典
    """
    # 將日期轉換為 API 需要的格式
    api_date = convert_date_format(date)

    # TWSE API 端點
    url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
    params = {
        "response": "json",
        "date": api_date,
        "stockNo": "2330"  # 台積電股票代號
    }

    try:
        logger.info(f"📡 開始抓取台積電股票資料: {date}")
        logger.debug(f"API URL: {url}")
        logger.debug(f"參數: {params}")

        # 發送 HTTP GET 請求
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()  # 檢查 HTTP 錯誤

        # 解析 JSON
        data = response.json()

        # 檢查回應狀態
        if data.get("stat") != "OK":
            error_msg = data.get("stat", "未知錯誤")
            logger.warning(f"⚠️  API 返回非 OK 狀態: {error_msg}")
            return {
                "module": MODULE_ID,
                "date": date,
                "status": "failed",
                "error": f"API 返回錯誤: {error_msg}",
                "source": "TWSE"
            }

        # 檢查是否有資料
        if "data" not in data or not data["data"]:
            logger.warning(f"⚠️  該日無交易資料: {date}")
            return {
                "module": MODULE_ID,
                "date": date,
                "status": "failed",
                "error": "該日無交易資料（可能是假日或休市日）",
                "source": "TWSE"
            }

        # 取得欄位名稱
        fields = data.get("fields", [])
        if not fields:
            logger.error("❌ API 回應缺少 fields 欄位")
            return {
                "module": MODULE_ID,
                "date": date,
                "status": "error",
                "error": "API 資料格式錯誤：缺少欄位定義",
                "source": "TWSE"
            }

        # 找出目標日期的資料（轉換為民國年格式進行比對）
        target_data = None
        target_roc_date = ""

        # 將西元年轉為民國年進行比對
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            roc_year = dt.year - 1911
            target_roc_date = f"{roc_year}/{dt.month:02d}/{dt.day:02d}"
            logger.debug(f"目標民國年日期: {target_roc_date}")
        except ValueError:
            logger.error(f"❌ 日期格式錯誤: {date}")
            return {
                "module": MODULE_ID,
                "date": date,
                "status": "error",
                "error": "日期格式錯誤",
                "source": "TWSE"
            }

        # 在資料中尋找目標日期
        for row in data["data"]:
            if row[0] == target_roc_date:
                target_data = row
                break

        # 如果沒找到，取最後一筆資料（最新交易日）
        if not target_data:
            logger.warning(f"⚠️  找不到 {date} 的資料，使用最後交易日資料")
            target_data = data["data"][-1]  # 最後一筆是最新的

        # 解析資料（依照 fields 順序）
        # fields: ["日期", "成交股數", "成交金額", "開盤價", "最高價", "最低價", "收盤價", "漲跌價差", "成交筆數"]
        date_str = target_data[0] if len(target_data) > 0 else ""
        open_price = target_data[3] if len(target_data) > 3 else ""
        high_price = target_data[4] if len(target_data) > 4 else ""
        low_price = target_data[5] if len(target_data) > 5 else ""
        close_price = target_data[6] if len(target_data) > 6 else ""
        price_change = target_data[7] if len(target_data) > 7 else "0"

        # 處理漲跌價差格式
        price_change = parse_price_change(price_change)

        logger.info(f"✅ 成功抓取台積電資料: 漲跌 {price_change} 元")
        logger.debug(f"開盤: {open_price}, 最高: {high_price}, 最低: {low_price}, 收盤: {close_price}")

        return {
            "module": MODULE_ID,
            "date": date,
            "status": "success",
            "data": {
                "price_change": price_change,
                "open_price": open_price,
                "high_price": high_price,
                "low_price": low_price,
                "close_price": close_price,
                "source": "TWSE"
            },
            "source": "TWSE"
        }

    except requests.Timeout:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.error(f"❌ 連線逾時: {timeout} 秒")
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": "連線逾時，請檢查網路連線",
            "source": "TWSE",
            "timestamp": timestamp,
            "context": {"timeout": timeout}
        }

    except requests.HTTPError as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_code = e.response.status_code if e.response else 0
        logger.error(f"❌ HTTP 錯誤: {status_code}")
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": f"HTTP 錯誤 {status_code}",
            "source": "TWSE",
            "timestamp": timestamp,
            "context": {"status_code": status_code}
        }

    except requests.RequestException as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.error(f"❌ 網路請求失敗: {str(e)}")
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": "網路請求失敗，請檢查網路連線",
            "source": "TWSE",
            "timestamp": timestamp,
            "context": {"error_type": type(e).__name__}
        }

    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.error(f"❌ 未預期的錯誤: {str(e)}")
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": f"系統錯誤: {type(e).__name__}",
            "source": "TWSE",
            "timestamp": timestamp,
            "context": {"error_type": type(e).__name__}
        }


def fetch(date: str) -> str:
    """
    主要抓取函數 - 台積電當日漲跌價差

    【功能說明】
    這是模組的主要入口函數，負責：
    1. 從 TWSE API 抓取台積電股票資料
    2. 提取當日漲跌價差
    3. 格式化為統一的文字格式
    4. 完整的錯誤處理

    【參數說明】
    Args:
        date (str): 查詢日期，格式為 YYYY-MM-DD
                   例如: "2025-12-15"

    【返回值】
    Returns:
        str: 格式化的文字結果

        成功範例:
        "2025.12.15  F15: 台積電當日漲跌價差 : -30 元 [TWSE]"

        失敗範例（假日）:
        "F15 錯誤: 該日無交易資料（可能是假日或休市日） [TWSE]"

        異常範例（逾時）:
        "F15 錯誤: 連線逾時，請檢查網路連線 [TWSE] (2025-12-15 14:30:45, timeout=30s)"

    【使用範例】

    Example 1 - 基本使用:
        >>> result = fetch("2025-12-15")
        >>> print(result)
        2025.12.15  F15: 台積電當日漲跌價差 : -30 元 [TWSE]

    Example 2 - 假日查詢:
        >>> result = fetch("2025-12-14")  # 週六
        >>> print(result)
        F15 錯誤: 該日無交易資料（可能是假日或休市日） [TWSE]

    【錯誤處理】
    - 所有錯誤都以文字訊息返回，不拋出例外
    - 網路錯誤包含時間戳和上下文資訊
    - 日誌完整記錄所有操作和錯誤
    """
    logger.info(f"{'='*60}")
    logger.info(f"📊 F15 模組啟動: 台積電當日漲跌價差")
    logger.info(f"📅 查詢日期: {date}")
    logger.info(f"{'='*60}")

    # 抓取資料
    result = fetch_stock_data(date)

    # 格式化輸出
    if result["status"] == "success":
        output = format_f15_output(
            date=date,
            status="success",
            data=result.get("data")
        )
    elif result["status"] == "failed":
        output = format_f15_output(
            date=date,
            status="failed",
            error=result.get("error")
        )
    else:  # error
        output = format_f15_output(
            date=date,
            status="error",
            error=result.get("error"),
            timestamp=result.get("timestamp"),
            context=result.get("context")
        )

    logger.info(f"📤 輸出結果: {output}")
    logger.info(f"{'='*60}\n")

    return output


def main():
    """
    主程式 - 支援命令列執行

    使用方式:
        python f15_fetcher_dev.py 2025-12-15
        python f15_fetcher_dev.py  # 使用今天日期
    """
    if len(sys.argv) > 1:
        query_date = sys.argv[1]
    else:
        query_date = datetime.now().strftime("%Y-%m-%d")

    result = fetch(query_date)
    print(result)


if __name__ == "__main__":
    main()
