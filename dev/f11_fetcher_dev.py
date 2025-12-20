"""
f11_fetcher.py
加權股價指數收盤資料抓取模組

功能：
- 從台灣證券交易所抓取加權股價指數收盤資料
- 提供 fetch(date: str) -> str 統一介面
- 使用 Selenium 處理 JavaScript 動態載入

資料來源：
- 台灣證券交易所
- https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html
"""

import sys
import io
import logging
from typing import Dict, Optional
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 設定 UTF-8 輸出
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
MODULE_ID = "f11"
MODULE_NAME = "f11_fetcher"
SOURCE = "https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html"

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def format_f11_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
    """
    格式化 F11 輸出為統一文字格式 v5.0

    Args:
        date: 日期 (YYYY-MM-DD)
        status: 狀態 ("success" / "failed" / "error")
        data: 成功時的資料字典
        error: 失敗時的錯誤訊息

    Returns:
        成功時: 2025.12.19  F11: 加權股價指數收盤 : 23,456.78  [https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html]
        失敗時: 2025.12.19  F11 錯誤: {錯誤訊息} [https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html]
    """
    formatted_date = date.replace("-", ".")

    if status == "success" and data:
        closing_index = data.get("closing_index", 0)
        return f"{formatted_date}  F11: 加權股價指數收盤 : {closing_index:,.2f}  [{SOURCE}]"
    else:
        error_msg = error or "未知錯誤"
        return f"{formatted_date}  F11 錯誤: {error_msg} [{SOURCE}]"


def extract_taiex_closing_index(driver, date: str) -> Dict:
    """
    從頁面中提取加權股價指數收盤數據

    Args:
        driver: Selenium WebDriver
        date: 日期字串

    Returns:
        Dict: 成功返回 {status: "success", data: {...}}
              失敗返回 {status: "failed", error: "..."}
    """
    try:
        # 等待表格載入
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            logger.debug(f"[F11] {date} 表格已載入")
        except:
            logger.warning(f"[F11] {date} 等待表格逾時")
            return {
                "status": "failed",
                "error": "頁面載入逾時"
            }

        # 尋找表格
        try:
            table = driver.find_element(By.TAG_NAME, "table")
        except:
            return {
                "status": "failed",
                "error": "找不到數據表格"
            }

        # 取得所有行
        rows = table.find_elements(By.TAG_NAME, "tr")
        if len(rows) < 2:
            return {
                "status": "failed",
                "error": "該日無交易資料（可能是假日或休市日）"
            }

        logger.debug(f"[F11] {date} 表格包含 {len(rows)} 行資料")

        # 取得表頭，找出收盤指數欄位
        header_row = rows[0]
        headers = [th.text.strip() for th in header_row.find_elements(By.TAG_NAME, "th")]
        logger.debug(f"[F11] {date} 表格標題: {headers}")

        # 尋找收盤指數欄位（可能的欄位名稱）
        closing_index_col = None
        search_names = ['收盤指數', '現在指數', '目前指數', '指數', 'Index', '加權股價']

        for col_name in search_names:
            for i, header in enumerate(headers):
                if col_name in header:
                    closing_index_col = i
                    logger.debug(f"[F11] {date} 找到指數欄位：'{header}' (欄 {closing_index_col})")
                    break
            if closing_index_col is not None:
                break

        if closing_index_col is None:
            logger.error(f"[F11] {date} 無法找到指數欄位，可用欄位: {headers}")
            return {
                "status": "failed",
                "error": "無法解析頁面結構"
            }

        # 取得最後一行（最新收盤資料）
        last_row = rows[-1]
        cells = last_row.find_elements(By.TAG_NAME, "td")

        if closing_index_col >= len(cells):
            logger.error(f"[F11] {date} 欄位索引越界：{closing_index_col} >= {len(cells)}")
            return {
                "status": "failed",
                "error": "無法解析頁面結構"
            }

        # 提取收盤指數值
        index_str = cells[closing_index_col].text.strip()
        logger.debug(f"[F11] {date} 提取的原始值: '{index_str}'")

        # 清理數值（移除逗號、空格等）
        index_str = index_str.replace(',', '').replace(' ', '').strip()

        # 移除非數字字符（保留小數點）
        import re
        index_str = re.sub(r'[^\d.]', '', index_str)

        if not index_str:
            logger.warning(f"[F11] {date} 無法解析指數值")
            return {
                "status": "failed",
                "error": "該日無交易資料（可能是假日或休市日）"
            }

        # 轉換為浮點數
        try:
            closing_index = float(index_str)
            logger.debug(f"[F11] {date} 成功轉換指數值: {closing_index}")

            return {
                "status": "success",
                "data": {
                    "closing_index": closing_index,
                    "source": "TWSE"
                }
            }

        except (ValueError, IndexError) as e:
            logger.error(f"[F11] {date} 解析數值失敗: {e}, index_str={index_str}")
            return {
                "status": "failed",
                "error": "無法解析數值"
            }

    except Exception as e:
        logger.exception(f"[F11] {date} 提取數據時發生錯誤")
        return {
            "status": "failed",
            "error": f"提取失敗: {str(e)}"
        }


def fetch(date: str) -> str:
    """
    抓取指定日期的加權股價指數收盤資料

    Args:
        date: 日期字串 (YYYY-MM-DD)

    Returns:
        成功時: "2025.12.19  F11: 加權股價指數收盤 : 23,456.78  [來源]"
        失敗時: "2025.12.19  F11 錯誤: 錯誤訊息 [來源]"
    """
    # 驗證日期格式
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_f11_output(date, "error", error="日期格式錯誤，請使用 YYYY-MM-DD")

    driver = None

    try:
        logger.info(f"[F11] {date} 開始啟動 Chrome 瀏覽器")

        # Chrome 選項配置
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 無頭模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        # 啟動 Chrome
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.debug(f"[F11] {date} Chrome 瀏覽器已啟動")

        # 訪問頁面
        logger.info(f"[F11] {date} 訪問頁面: {SOURCE}")
        driver.get(SOURCE)

        # 等待並處理聲明彈出視窗
        logger.debug(f"[F11] {date} 等待頁面加載並檢查聲明視窗...")
        try:
            # 等待聲明按鈕出現（最多等待 10 秒）
            disclaimer_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '我已了解以上聲明')]"))
            )
            logger.debug(f"[F11] {date} 找到聲明按鈕，準備點擊")
            disclaimer_button.click()
            logger.debug(f"[F11] {date} 已點擊聲明按鈕")
        except:
            logger.debug(f"[F11] {date} 未找到聲明按鈕，可能已接受或不存在")

        # 等待頁面加載（JavaScript 動態內容）- 使用動態等待
        logger.debug(f"[F11] {date} 等待數據表格載入...")
        try:
            # 等待表格出現（最多等待 15 秒）
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            logger.debug(f"[F11] {date} 數據表格已載入")
        except:
            logger.warning(f"[F11] {date} 等待數據表格逾時，嘗試繼續執行")

        # 提取收盤指數數據
        result_dict = extract_taiex_closing_index(driver, date)

        if result_dict.get("status") == "success":
            data = result_dict.get("data")
            logger.info(f"[F11] {date} 收盤指數: {data.get('closing_index')}")
            return format_f11_output(date, "success", data=data)
        else:
            logger.warning(f"[F11] {date} 抓取失敗: {result_dict.get('error')}")
            return format_f11_output(date, "failed", error=result_dict.get("error", "未知錯誤"))

    except Exception as e:
        logger.exception(f"[F11] {date} 執行過程發生錯誤")
        return format_f11_output(date, "error", error=f"系統錯誤: {str(e)}")

    finally:
        # 確保瀏覽器被關閉
        if driver:
            try:
                driver.quit()
                logger.debug(f"[F11] {date} Chrome 瀏覽器已關閉")
            except:
                pass


def main():
    """獨立測試用"""
    if len(sys.argv) > 1:
        test_date = sys.argv[1]
    else:
        test_date = datetime.now().strftime("%Y-%m-%d")

    print(f"測試日期: {test_date}")
    print(fetch(test_date))


if __name__ == '__main__':
    main()
