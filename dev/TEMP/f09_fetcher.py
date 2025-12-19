"""
f09_openspec_dev.py
台指期貨夜盤漲跌點數 (Night Session Change) 抓取模組

功能：
- 從 TAIFEX 網站抓取台指期貨 (TX) 夜盤漲跌點數（相對於日盤收盤價）
- 提供 fetch(date: str) -> str 統一介面
- 自動選取近月合約
- 正負號顯示

資料來源：
- 期貨每日交易行情查詢 (盤後交易時段)
- https://www.taifex.com.tw/cht/3/futDailyMarketReport
- 關鍵參數: queryType=2 (盤後交易時段)
- 關鍵欄位: 「漲跌點數」或「漲跌」
"""

import sys
import io
import logging
import requests
import pandas as pd
from typing import Dict, Optional
from datetime import datetime

# 設定 UTF-8 輸出（解決 Windows 終端亂碼，PyInstaller 已處理打包的情境）
# 只在尚未包裝時才進行包裝，避免重複包裝導致 I/O 錯誤
# 注意：測試時會暫時跳過此包裝
if sys.platform == 'win32' and not getattr(sys, "frozen", False) and 'pytest' not in sys.modules:
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

# 模組識別
MODULE_ID = "f09"
MODULE_NAME = "f09_fetcher"
SOURCE = "https://www.taifex.com.tw/cht/3/futDailyMarketReport"

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def format_f09_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
    """
    格式化 F09 輸出為統一文字格式 v5.0

    Args:
        date: 日期 (YYYY-MM-DD)
        status: 狀態 ("success" / "failed" / "error")
        data: 成功時的資料字典
        error: 失敗時的錯誤訊息

    Returns:
        成功時: 2025.12.18  F09: 台指期貨夜盤漲跌點數 : +108 點  [https://www.taifex.com.tw/cht/3/futDailyMarketReport]
        失敗時: 2025.12.18  F09 錯誤: {錯誤訊息} [https://www.taifex.com.tw/cht/3/futDailyMarketReport]
    """
    if status == "success" and data:
        change_points = data.get("change_points", 0)

        # 格式化正負號
        if change_points > 0:
            # 正數：加上 + 號，並包含千分位
            change_str = f"+{change_points:,.0f}"
        elif change_points < 0:
            # 負數：保留 - 號（自動包含），並包含千分位
            change_str = f"{change_points:,.0f}"
        else:
            # 零：不加正負號
            change_str = "0"

        formatted_date = date.replace("-", ".")
        return f"{formatted_date}  F09: 台指期貨夜盤漲跌點數 : {change_str} 點  [{SOURCE}]"
    else:
        error_msg = error or "未知錯誤"
        formatted_date = date.replace("-", ".")
        return f"{formatted_date}  F09 錯誤: {error_msg} [{SOURCE}]"


def convert_to_number(value) -> Optional[float]:
    """將字串轉換為數值 (float 或 int)"""
    if pd.isna(value) or str(value).strip() == '-':
        return None
    try:
        # 移除逗號、空白、以及特殊符號（如 ▲▼）
        clean_val = str(value).replace(',', '').replace('▲', '').replace('▼', '').strip()
        if '.' in clean_val:
            return float(clean_val)
        return int(clean_val)
    except (ValueError, AttributeError):
        return None


def find_column(df: pd.DataFrame, keywords: list) -> Optional[str]:
    """尋找包含特定關鍵字的欄位"""
    for col in df.columns:
        col_str = str(col)
        if any(keyword in col_str for keyword in keywords):
            return col
    return None


def extract_change_points(df: pd.DataFrame, date: str) -> Dict:
    """從表格中提取 TX 近月合約漲跌點數"""

    # 1. 尋找並篩選合約 (TX)
    contract_col = find_column(df, ['契約', 'Contract'])
    if contract_col is None:
         # 嘗試直接假設第一欄是契約
         contract_col = df.columns[0]

    # 清理並篩選 TX
    df['clean_contract'] = df[contract_col].astype(str).str.strip()
    tx_rows = df[df['clean_contract'] == 'TX']

    if len(tx_rows) == 0:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "failed",
            "error": "找不到台指期(TX)資料"
        }

    # 2. 排序取近月（第一筆）
    target_row = tx_rows.iloc[0]

    # 3. 找漲跌點數欄位
    change_col = find_column(df, ['漲跌點數', '漲跌', 'Change', '漲跌 (點)'])

    if change_col is None:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "failed",
            "error": "無法取得漲跌點數"
        }

    # 4. 提取漲跌數值
    change_value = convert_to_number(target_row[change_col])

    if change_value is None:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "failed",
            "error": "無法解析漲跌點數"
        }

    return {
        "module": MODULE_ID,
        "date": date,
        "status": "success",
        "data": {
            "change_points": change_value,
            "source": "TAIFEX"
        },
        "source": "TAIFEX"
    }


def fetch(date: str) -> str:
    """
    抓取指定日期的台指期貨夜盤漲跌點數

    Args:
        date: 日期字串 (YYYY-MM-DD)

    Returns:
        成功時: "2025.12.18  F09: 台指期貨夜盤漲跌點數 : +108 點  [來源]"
        失敗時: "2025.12.18  F09 錯誤: 錯誤訊息 [來源]"
    """
    # 驗證日期格式
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_f09_output(date, "error", error="日期格式錯誤，請使用 YYYY-MM-DD")

    # 轉換日期格式為 TAIFEX 查詢格式 (YYYY/MM/DD)
    query_date = dt.strftime("%Y/%m/%d")

    # URL: 期貨每日交易行情查詢 (盤後交易時段)
    # 關鍵參數: queryType=2 指定「盤後交易時段」
    url = f"{SOURCE}?queryDate={query_date}&marketCode=0&commodity_id=TX&queryType=2"

    try:
        logger.info(f"[F09] {date} 開始抓取夜盤漲跌資料")
        logger.info(f"[F09] 正在抓取 {date} 的資料: {url}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = "utf-8"

        # 解析 HTML 表格
        try:
            dfs = pd.read_html(io.StringIO(response.text), flavor='lxml')
        except ImportError:
            dfs = pd.read_html(io.StringIO(response.text))

        if not dfs:
             return format_f09_output(date, "failed", error="找不到表格資料")

        df = dfs[0]

        # 檢查是否為空表
        if len(df) < 2:
             return format_f09_output(date, "failed", error="查無資料 (可能是假日)")

        result_dict = extract_change_points(df, date)

        if result_dict.get("status") == "success":
            change_points = result_dict.get('data', {}).get('change_points')
            logger.info(f"[F09] {date} 夜盤漲跌點數: {change_points}")
            return format_f09_output(date, "success", data=result_dict.get("data"))
        else:
            logger.warning(f"[F09] {date} 抓取失敗: {result_dict.get('error')}")
            return format_f09_output(date, "failed", error=result_dict.get("error", "未知錯誤"))

    except requests.Timeout:
        logger.error(f"[F09] {date} 連線逾時")
        return format_f09_output(date, "error", error="連線逾時")
    except requests.HTTPError as e:
        logger.error(f"[F09] {date} HTTP 錯誤: {e.response.status_code}")
        return format_f09_output(date, "error", error=f"HTTP {e.response.status_code}")
    except Exception as e:
        logger.exception(f"[F09] {date} 執行過程發生錯誤")
        return format_f09_output(date, "error", error=f"系統錯誤: {str(e)}")


def main():
    """獨立測試用"""
    if len(sys.argv) > 1:
        test_date = sys.argv[1]
    else:
        test_date = '2025-12-17'

    print(f"測試日期: {test_date}")
    print(fetch(test_date))


if __name__ == '__main__':
    main()
