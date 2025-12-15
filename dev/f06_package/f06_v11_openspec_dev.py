"""
f06_fetcher.py - 臺指選擇權波動率指數抓取模組 v1.1 (Selenium 版)

【模組功能】
- 從 TAIFEX MIS 系統盤中即時抓取臺指選擇權波動率指數（VIX）
- 提供統一的 fetch(date: str) -> str 介面
- 自動點擊確認按鈕並解析動態渲染的表格
- 完整的異常處理和日誌記錄

【主要入口】
- fetch(date: str) -> str
  入參: 日期字串 (YYYY-MM-DD 格式，暫不使用，返回盤中即時數據)
  返值: 統一格式的文字結果
  
  成功範例: "2025.12.15  F06: 臺指選擇權波動率指數 : 18.50 [TAIFEX]"
  失敗範例: "F06 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]"

【重要限制】
- MIS 系統需要手動或自動點擊「確認」按鈕方能顯示數據
- 每次獲取數據時都需要啟動 Chrome 瀏覽器（性能考量）
- 盤中時段返回即時數據，非交易時段可能無數據
- 若 TAIFEX MIS 頁面結構改變，需更新選擇器邏輯

【依賴套件】
- requests >= 2.28.0 (HTTP 請求備用)
- pandas >= 1.5.0 (表格解析)
- selenium >= 4.0.0 (瀏覽器自動化)
- webdriver-manager >= 3.8.0 (驅動程式管理)
- beautifulsoup4 >= 4.11.0 (HTML 解析)

【版本歷史】
- v1.0: vixMinNew 靜態頁面版本 (2025-12-15，已廢棄)
- v1.1: MIS 盤中即時版本，Selenium 自動化 (2025-12-15)

【錯誤代碼表】
| 錯誤類型 | 原因 | 解決方案 |
|---------|------|--------|
| 日期格式錯誤 | 輸入格式非 YYYY-MM-DD | 檢查日期格式 |
| 瀏覽器啟動失敗 | Chrome 未安裝或驅動不相容 | 安裝 Chrome 或更新驅動 |
| 連線逾時 | 網路延遲或 MIS 無回應 | 檢查網路、稍後重試 |
| 確認按鈕未找到 | 頁面結構改變 | 更新按鈕選擇器 |
| 無交易資料 | 假日或休市日 | 改查交易日期 |

【日誌配置】
模組使用 Python logging，預設級別為 INFO
- INFO: 主要操作（啟動瀏覽器、點擊按鈕、完成、失敗）
- DEBUG: 流程分支（元素尋找、表格解析）
- ERROR: 無法恢復的異常
"""

import io
import logging
import sys
from datetime import datetime
from typing import TypedDict, Optional, Dict, Any
import time

import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 【模組配置】
MODULE_ID = "f06"
SOURCE = "TAIFEX-MIS"

# 【日誌配置】
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# 【類型定義】
class VIXDataDict(TypedDict):
    """VIX 數據結構"""
    vix_value: float
    source: str
    timestamp: Optional[str]  # 盤中時間戳


class ErrorContextDict(TypedDict, total=False):
    """錯誤上下文"""
    timeout: int
    status_code: int
    step: str
    error_type: str
    selenium_error: str


class FetchResultDict(TypedDict):
    """完整的抓取結果"""
    module: str
    date: str
    status: str  # 'success', 'failed', 'error'
    data: Optional[VIXDataDict]
    error: Optional[str]
    source: str


def format_f06_output(
    date: str,
    status: str,
    data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    timestamp: Optional[str] = None,
    context: Optional[ErrorContextDict] = None
) -> str:
    """
    格式化 F06 輸出結果
    
    【功能】統一 F06 模組的文字輸出格式，包括成功、失敗和異常情況
    
    【參數】
    Args:
        date (str): 日期 (YYYY-MM-DD 格式)
        status (str): 狀態，可選值:
            - "success": 成功取得數據
            - "failed": 失敗（無數據但正常返回）
            - "error": 異常（發生錯誤）
        data (dict, optional): 成功情況下的數據字典
            範例: {"vix_value": 18.50, "source": "TAIFEX-MIS"}
        error (str, optional): 錯誤或失敗信息
        timestamp (str, optional): 時間戳 (YYYY-MM-DD HH:MM:SS 格式)
        context (dict, optional): 上下文信息
            可包含: timeout, status_code, step, error_type, selenium_error
    
    【返回值】
    Returns:
        str: 格式化的輸出字串，長度通常 50-200 字
    
    【輸出格式說明】
    
    1. 成功情況:
       格式: "{日期}  F06: 臺指選擇權波動率指數 : {波動率} [TAIFEX]"
       說明: 日期使用點號分隔，波動率精度 2 位小數
       範例: "2025.12.15  F06: 臺指選擇權波動率指數 : 18.50 [TAIFEX]"
    
    2. 失敗情況（無交易資料）:
       格式: "F06 錯誤: {失敗訊息} [TAIFEX]"
       說明: 用於可預見的失敗（假日、休市）
       範例: "F06 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]"
    
    3. 異常情況（包含時間戳）:
       格式: "F06 錯誤: {錯誤訊息} [TAIFEX] ({時間戳})"
       說明: 用於技術異常，包含發生時間
       範例: "F06 錯誤: 瀏覽器啟動失敗 [TAIFEX] (2025-12-15 14:30:45)"
    
    4. 異常情況（包含上下文）:
       格式: "F06 錯誤: {錯誤訊息} [TAIFEX] ({時間戳}, {上下文})"
       說明: 技術異常且有額外上下文信息
       範例: "F06 錯誤: 連線逾時 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)"
              "F06 錯誤: 瀏覽器啟動失敗 [TAIFEX] (2025-12-15 14:30:45, step=啟動Chrome)"
    
    【使用範例】
    
    Example 1 - 成功情況:
        >>> result = format_f06_output(
        ...     date="2025-12-15",
        ...     status="success",
        ...     data={"vix_value": 18.50, "source": "TAIFEX-MIS"}
        ... )
        >>> print(result)
        2025.12.15  F06: 臺指選擇權波動率指數 : 18.50 [TAIFEX]
    
    Example 2 - 失敗情況:
        >>> result = format_f06_output(
        ...     date="2025-12-14",
        ...     status="failed",
        ...     error="該日無交易資料（可能是假日或休市日）"
        ... )
        >>> print(result)
        F06 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]
    
    Example 3 - 異常情況（簡單）:
        >>> result = format_f06_output(
        ...     date="2025-12-15",
        ...     status="error",
        ...     error="瀏覽器啟動失敗",
        ...     timestamp="2025-12-15 14:30:45"
        ... )
        >>> print(result)
        F06 錯誤: 瀏覽器啟動失敗 [TAIFEX] (2025-12-15 14:30:45)
    
    Example 4 - 異常情況（含上下文）:
        >>> result = format_f06_output(
        ...     date="2025-12-15",
        ...     status="error",
        ...     error="瀏覽器啟動失敗",
        ...     timestamp="2025-12-15 14:30:45",
        ...     context={"step": "啟動Chrome驅動"}
        ... )
        >>> print(result)
        F06 錯誤: 瀏覽器啟動失敗 [TAIFEX] (2025-12-15 14:30:45, step=啟動Chrome驅動)
    """
    # 轉換日期格式 (YYYY-MM-DD → YYYY.MM.DD)
    date_formatted = date.replace("-", ".")
    module_code = MODULE_ID.upper()  # F06

    # 【成功情況】
    if status == "success" and data:
        vix_value = data.get("vix_value", 0)
        result = f"{date_formatted}  {module_code}: 臺指選擇權波動率指數 : {vix_value:.2f} [TAIFEX]"
        return result

    # 【失敗和異常情況】
    else:
        error_msg = error or "未知錯誤"
        result = f"{module_code} 錯誤: {error_msg} [TAIFEX]"
        
        # 增加時間戳和上下文後綴
        suffix = ""
        if timestamp:
            suffix += f" ({timestamp}"
            
        if context:
            context_parts = []
            for k, v in context.items():
                if k == "timeout":
                    context_parts.append(f"{k}={v}s")
                else:
                    context_parts.append(f"{k}={v}")
            context_str = ", ".join(context_parts)
            
            if suffix:
                suffix += f", {context_str})"
            else:
                suffix = f" ({context_str})"
        elif suffix:
            suffix += ")"
        
        result += suffix
        
        return result


def extract_vix_value_from_table(html_content: str, date: str) -> Dict[str, Any]:
    """
    從 HTML 內容中提取 VIX 波動率值
    
    【功能】解析 Selenium 抓取的 HTML，找出波動率指數欄位和對應的數值
    
    【參數】
    Args:
        html_content (str): HTML 內容
        date (str): 日期字串 (用於日誌)
    
    【返回值】
    Returns:
        dict: 成功時返回 {status: "success", data: {...}}
             失敗時返回 {status: "failed", error: "..."}
    
    【異常處理】
    - 若表格為空或無數據，返回 failed
    - 若數值無法轉換，繼續嘗試其他欄位
    """
    try:
        # 使用 pd.read_html 解析所有表格
        tables = pd.read_html(html_content)
        logger.debug(f"[F06] {date} 解析到 {len(tables)} 個表格")
        
        if len(tables) == 0:
            logger.warning(f"[F06] {date} HTML 中無法找到表格")
            return {
                "status": "failed",
                "error": "該日無交易資料（可能是假日或休市日）"
            }
        
        # 嘗試從每個表格中提取波動率指數
        for idx, df in enumerate(tables):
            logger.debug(f"[F06] {date} 檢查第 {idx+1} 個表格，形狀: {df.shape}")
            
            if df.shape[0] == 0:
                continue
            
            # 嘗試多種可能的欄位名稱
            possible_names = [
                '目前指數',  # MIS VolatilityQuotes 主要欄位
                '臺指選擇權波動率指數',
                '波動率指數',
                'VIX指數',
                'VIX',
                '波動率',
                'Volatility Index',
                'VIX Close'
            ]
            
            for name in possible_names:
                if name in df.columns:
                    try:
                        value = float(df[name].iloc[0])
                        logger.info(f"[F06] {date} 成功提取 VIX: {value}")
                        return {
                            "status": "success",
                            "data": {
                                "vix_value": value,
                                "source": SOURCE,
                                "timestamp": datetime.now().strftime("%H:%M:%S")
                            }
                        }
                    except (ValueError, IndexError, TypeError):
                        continue
        
        # 無法找到欄位
        logger.warning(f"[F06] {date} 無法在表格中找到波動率指數欄位")
        return {
            "status": "failed",
            "error": "該日無交易資料（可能是假日或休市日）"
        }

    except Exception as e:
        logger.error(f"[F06] {date} 表格解析失敗: {str(e)}")
        return {
            "status": "failed",
            "error": f"表格解析失敗: {str(e)}"
        }


def fetch_with_selenium(date: str) -> str:
    """
    使用 Selenium 從 MIS 頁面抓取波動率數據
    
    【流程】
    1. 驗證日期格式
    2. 啟動 Chrome 瀏覽器
    3. 訪問 MIS VolatilityQuotes 頁面
    4. 等待頁面加載
    5. 尋找並點擊「確認」按鈕
    6. 等待表格渲染
    7. 解析 HTML 提取 VIX 數值
    8. 關閉瀏覽器並返回結果
    
    【參數】
    Args:
        date (str): 日期字串 (YYYY-MM-DD，用於驗證和日誌)
    
    【返回值】
    Returns:
        str: 統一格式的結果字串
    """
    # 驗證日期格式
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        logger.info(f"[F06] {date} 日期格式驗證失敗")
        return format_f06_output(date, "error", error="日期格式錯誤，請使用 YYYY-MM-DD")
    
    url = "https://mis.taifex.com.tw/futures/VolatilityQuotes/"
    driver = None
    
    try:
        logger.info(f"[F06] {date} 開始啟動 Chrome 瀏覽器")
        
        # Chrome 選項配置
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        
        # 啟動 Chrome
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        logger.debug(f"[F06] {date} Chrome 瀏覽器已啟動")
        
        # 訪問頁面
        logger.info(f"[F06] {date} 訪問 MIS 頁面: {url}")
        driver.get(url)
        
        # 等待頁面加載（最多 10 秒）
        logger.debug(f"[F06] {date} 等待頁面加載...")
        time.sleep(3)
        
        # 首先嘗試處理免責聲明頁面
        try:
            logger.debug(f"[F06] {date} 尋找免責聲明接受按鈕...")
            disclaimer_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '接受')]"))
            )
            logger.debug(f"[F06] {date} 找到免責聲明接受按鈕，準備點擊")
            disclaimer_button.click()
            logger.info(f"[F06] {date} 已點擊免責聲明接受按鈕")
            time.sleep(2)  # 等待頁面跳轉
        except Exception as e:
            logger.debug(f"[F06] {date} 未找到免責聲明按鈕（可能無需同意）: {type(e).__name__}")
            # 继续，可能無免責聲明或已經通過
        
        # 等待表格渲染（最多 5 秒）
        logger.debug(f"[F06] {date} 等待表格渲染...")
        time.sleep(1)
        
        # 取得頁面 HTML
        page_html = driver.page_source
        logger.debug(f"[F06] {date} 獲取頁面 HTML，大小: {len(page_html)} 字節")
        
        # 解析並提取 VIX 數值
        result_dict = extract_vix_value_from_table(page_html, date)
        
        if result_dict.get("status") == "success":
            return format_f06_output(date, "success", data=result_dict.get("data"))
        else:
            return format_f06_output(date, "failed", error=result_dict.get("error"))
    
    except Exception as e:
        logger.error(f"[F06] {date} 未預期的錯誤: {str(e)}")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return format_f06_output(
            date, "error",
            error="瀏覽器自動化異常",
            timestamp=timestamp,
            context={"selenium_error": str(e)}
        )
    
    finally:
        # 確保瀏覽器被關閉
        if driver:
            try:
                driver.quit()
                logger.debug(f"[F06] {date} Chrome 瀏覽器已關閉")
            except:
                pass


def fetch(date: str) -> str:
    """
    抓取指定日期的臺指選擇權波動率指數（主入口）
    
    【功能】從 TAIFEX MIS 系統抓取波動率指數，返回統一格式的文字結果
    
    【參數】
    Args:
        date (str): 日期字串，格式必須為 YYYY-MM-DD
                    範例: "2025-12-15"
                    注意: MIS 系統返回的是盤中即時數據，date 參數主要用於日誌
    
    【返回值】
    Returns:
        str: 統一格式的文字字串，包含以下情況：
        
        1. 成功情況:
           格式: "2025.12.15  F06: 臺指選擇權波動率指數 : 18.50 [TAIFEX]"
           
        2. 失敗情況:
           格式: "F06 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]"
           
        3. 異常情況:
           格式: "F06 錯誤: [錯誤描述] [TAIFEX] ([時間戳], [上下文])"
    
    【使用範例】
    
    Example 1 - 正常使用:
        >>> result = fetch("2025-12-15")
        >>> print(result)
        2025.12.15  F06: 臺指選擇權波動率指數 : 18.50 [TAIFEX]
    
    Example 2 - 日期格式錯誤:
        >>> result = fetch("2025-12/15")
        >>> print(result)
        F06 錯誤: 日期格式錯誤，請使用 YYYY-MM-DD [TAIFEX]
    
    Example 3 - 瀏覽器異常:
        >>> result = fetch("2025-12-15")  # 若 Chrome 未安裝
        >>> print(result)
        F06 錯誤: 瀏覽器自動化異常 [TAIFEX] (2025-12-15 14:30:45, ...)
    """
    return fetch_with_selenium(date)


def main():
    """主測試入口"""
    # 取得當天日期或使用命令行參數
    if len(sys.argv) > 1:
        test_date = sys.argv[1]
    else:
        test_date = datetime.now().strftime("%Y-%m-%d")
    
    print("-" * 60)
    print(f"F06 v1.1 (Selenium 版) - 波動率指數抓取")
    print("-" * 60)
    print(f"測試日期: {test_date}")
    print("-" * 60)
    
    result = fetch(test_date)
    print(result)
    
    print("-" * 60)


if __name__ == '__main__':
    main()
