"""
f23_openspec_dev.py
EM-ND 指數夜盤資料抓取模組

功能：
- 從玩股網抓取 EM-ND 指數夜盤資料
- 提供 fetch(date: str) -> str 統一介面
- 使用 Selenium 處理 JavaScript 動態載入

資料來源：
- 玩股網全球股市
- https://www.wantgoo.com/global
"""

import sys
import io
import logging
import time
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
MODULE_ID = "f23"
MODULE_NAME = "f23_fetcher"
SOURCE = "https://www.wantgoo.com/global"

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def format_f23_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
    """
    格式化 F21 輸出為統一文字格式 v5.0

    Args:
        date: 日期 (YYYY-MM-DD)
        status: 狀態 ("success" / "failed" / "error")
        data: 成功時的資料字典
        error: 失敗時的錯誤訊息

    Returns:
        成功時: 2025.12.19  F23: EM-ND期指數 : 23,006.36 (漲跌 +313.04, +1.38%)  [https://www.wantgoo.com/global]
        失敗時: 2025.12.19  F21 錯誤: {錯誤訊息} [https://www.wantgoo.com/global]
    """
    formatted_date = date.replace("-", ".")

    if status == "success" and data:
        price = data.get("price", 0)
        change = data.get("change", 0)
        change_pct = data.get("change_pct", 0)

        # 格式化正負號
        change_str = f"+{change:,.2f}" if change > 0 else f"{change:,.2f}"
        pct_str = f"+{change_pct:.2f}%" if change_pct > 0 else f"{change_pct:.2f}%"

        return f"{formatted_date}  F23: EM-ND期指數 : {price:,.2f} (漲跌 {change_str}, {pct_str})  [{SOURCE}]"
    else:
        error_msg = error or "未知錯誤"
        return f"{formatted_date}  F21 錯誤: {error_msg} [{SOURCE}]"


def extract_emnd_data(driver, date: str) -> Dict:
    """
    從頁面中提取 EM-ND 數據

    Args:
        driver: Selenium WebDriver
        date: 日期字串

    Returns:
        Dict: 成功返回 {status: "success", data: {...}}
              失敗返回 {status: "failed", error: "..."}
    """
    try:
        # 嘗試多種可能的選擇器
        emnd_selectors = [
            "//tr[contains(., 'EM-ND')]",
            "//tr[contains(., 'Nasdaq')]",
            "//div[contains(text(), 'EM-ND')]//ancestor::tr[1]",
            "//*[contains(@class, 'nasdaq')]//ancestor::tr[1]",
        ]

        emnd_row = None
        for selector in emnd_selectors:
            try:
                emnd_row = driver.find_element(By.XPATH, selector)
                if emnd_row:
                    logger.debug(f"[F23] {date} 使用選擇器找到 EM-ND: {selector}")
                    break
            except:
                continue

        if not emnd_row:
            return {
                "status": "failed",
                "error": "找不到EM-ND資料"
            }

        # 提取該行所有 td
        tds = emnd_row.find_elements(By.TAG_NAME, "td")
        row_text = emnd_row.text
        logger.debug(f"[F23] {date} EM-ND 行文字: {row_text}")

        if len(tds) < 3:
            return {
                "status": "failed",
                "error": "資料格式異常"
            }

        # 嘗試解析數據（假設格式：名稱, 價格, 漲跌, 漲跌幅）
        try:
            # 通常格式: [名稱][價格][漲跌][漲跌幅][時間]
            price_text = tds[1].text.strip().replace(',', '')
            change_text = tds[2].text.strip().replace(',', '').replace('+', '').replace('▲', '').replace('▼', '-')
            change_pct_text = tds[3].text.strip().replace('%', '').replace('+', '')

            price = float(price_text)
            change = float(change_text)
            change_pct = float(change_pct_text)

            return {
                "status": "success",
                "data": {
                    "price": price,
                    "change": change,
                    "change_pct": change_pct,
                    "source": "WantGoo"
                }
            }

        except (ValueError, IndexError) as e:
            logger.error(f"[F23] {date} 解析數值失敗: {e}, row_text={row_text}")
            return {
                "status": "failed",
                "error": "無法解析數值"
            }

    except Exception as e:
        logger.exception(f"[F23] {date} 提取數據時發生錯誤")
        return {
            "status": "failed",
            "error": f"提取失敗: {str(e)}"
        }


def fetch(date: str) -> str:
    """
    抓取指定日期的 EM-ND 指數夜盤資料

    Args:
        date: 日期字串 (YYYY-MM-DD)

    Returns:
        成功時: "2025.12.19  F23: EM-ND期指數 : 23,006.36 (漲跌 +313.04, +1.38%)  [來源]"
        失敗時: "2025.12.19  F21 錯誤: 錯誤訊息 [來源]"
    """
    # 驗證日期格式
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_f23_output(date, "error", error="日期格式錯誤，請使用 YYYY-MM-DD")

    driver = None

    try:
        logger.info(f"[F23] {date} 開始啟動 Chrome 瀏覽器")

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
        logger.debug(f"[F23] {date} Chrome 瀏覽器已啟動")

        # 訪問頁面
        logger.info(f"[F23] {date} 訪問頁面: {SOURCE}")
        driver.get(SOURCE)

        # 等待頁面加載（JavaScript 動態內容）
        logger.debug(f"[F23] {date} 等待頁面加載...")
        time.sleep(8)  # 等待 AJAX 完成

        # 嘗試等待表格出現
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            logger.debug(f"[F23] {date} 表格已載入")
        except:
            logger.warning(f"[F23] {date} 未檢測到表格")

        # 提取 EM-ND 數據
        result_dict = extract_emnd_data(driver, date)

        if result_dict.get("status") == "success":
            data = result_dict.get("data")
            logger.info(f"[F23] {date} EM-ND: {data.get('price')}")
            return format_f23_output(date, "success", data=data)
        else:
            logger.warning(f"[F23] {date} 抓取失敗: {result_dict.get('error')}")
            return format_f23_output(date, "failed", error=result_dict.get("error", "未知錯誤"))

    except Exception as e:
        logger.exception(f"[F23] {date} 執行過程發生錯誤")
        return format_f23_output(date, "error", error=f"系統錯誤: {str(e)}")

    finally:
        # 確保瀏覽器被關閉
        if driver:
            try:
                driver.quit()
                logger.debug(f"[F23] {date} Chrome 瀏覽器已關閉")
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
