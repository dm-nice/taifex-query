"""
f25_openspec_dev.py
台指期盤後 指數夜盤資料抓取模組

功能：
- 從玩股網抓取 台指期盤後 指數夜盤資料
- 提供 fetch(date: str) -> str 統一介面
- 使用 Selenium 處理 JavaScript 動態載入

資料來源：
- 玩股網全球股市
- https://www.wantgoo.com/global
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
MODULE_ID = "f25"
MODULE_NAME = "f25_fetcher"
SOURCE = "https://www.wantgoo.com/global"

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def format_f25_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
    """
    格式化 F21 輸出為統一文字格式 v5.0

    Args:
        date: 日期 (YYYY-MM-DD)
        status: 狀態 ("success" / "failed" / "error")
        data: 成功時的資料字典
        error: 失敗時的錯誤訊息

    Returns:
        成功時: 2025.12.19  F25: 台指期盤後 : 23,006.36 (漲跌 +313.04, +1.38%)  [https://www.wantgoo.com/global]
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

        return f"{formatted_date}  F25: 台指期盤後 : {price:,.2f} (漲跌 {change_str}, {pct_str})  [{SOURCE}]"
    else:
        error_msg = error or "未知錯誤"
        return f"{formatted_date}  F21 錯誤: {error_msg} [{SOURCE}]"


def extract_tw_futures_data(driver, date: str) -> Dict:
    """
    從頁面中提取 台指期盤後 數據

    Args:
        driver: Selenium WebDriver
        date: 日期字串

    Returns:
        Dict: 成功返回 {status: "success", data: {...}}
              失敗返回 {status: "failed", error: "..."}
    """
    try:
        # 嘗試多種可能的選擇器
        tw_futures_selectors = [
            "//tr[contains(., '台指期盤後')]",
            "//tr[contains(., 'Nasdaq')]",
            "//div[contains(text(), '台指期盤後')]//ancestor::tr[1]",
            "//*[contains(@class, 'nasdaq')]//ancestor::tr[1]",
        ]

        tw_futures_row = None
        for selector in tw_futures_selectors:
            try:
                tw_futures_row = driver.find_element(By.XPATH, selector)
                if tw_futures_row:
                    logger.debug(f"[F25] {date} 使用選擇器找到 台指期盤後: {selector}")
                    break
            except:
                continue

        if not tw_futures_row:
            return {
                "status": "failed",
                "error": "找不到台指期盤後資料"
            }

        # 提取該行所有 td
        tds = tw_futures_row.find_elements(By.TAG_NAME, "td")
        row_text = tw_futures_row.text
        logger.debug(f"[F25] {date} 台指期盤後 行文字: {row_text}")

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
            logger.error(f"[F25] {date} 解析數值失敗: {e}, row_text={row_text}")
            return {
                "status": "failed",
                "error": "無法解析數值"
            }

    except Exception as e:
        logger.exception(f"[F25] {date} 提取數據時發生錯誤")
        return {
            "status": "failed",
            "error": f"提取失敗: {str(e)}"
        }


def fetch(date: str) -> str:
    """
    抓取指定日期的 台指期盤後 指數夜盤資料

    Args:
        date: 日期字串 (YYYY-MM-DD)

    Returns:
        成功時: "2025.12.19  F25: 台指期盤後 : 23,006.36 (漲跌 +313.04, +1.38%)  [來源]"
        失敗時: "2025.12.19  F21 錯誤: 錯誤訊息 [來源]"
    """
    # 驗證日期格式
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_f25_output(date, "error", error="日期格式錯誤，請使用 YYYY-MM-DD")

    driver = None

    try:
        logger.info(f"[F25] {date} 開始啟動 Chrome 瀏覽器")

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
        logger.debug(f"[F25] {date} Chrome 瀏覽器已啟動")

        # 訪問頁面
        logger.info(f"[F25] {date} 訪問頁面: {SOURCE}")
        driver.get(SOURCE)

        # 等待頁面加載（JavaScript 動態內容）- 使用動態等待
        logger.debug(f"[F25] {date} 等待頁面加載...")
        try:
            # 直接等待包含台指期的行出現（最多等待 15 秒）
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//tr[contains(., '台指期') or contains(., 'TW')]"))
            )
            logger.debug(f"[F25] {date} 台指期盤後資料已載入")
        except:
            logger.warning(f"[F25] {date} 等待台指期盤後資料逾時，嘗試繼續執行")

        # 提取 台指期盤後 數據
        result_dict = extract_tw_futures_data(driver, date)

        if result_dict.get("status") == "success":
            data = result_dict.get("data")
            logger.info(f"[F25] {date} 台指期盤後: {data.get('price')}")
            return format_f25_output(date, "success", data=data)
        else:
            logger.warning(f"[F25] {date} 抓取失敗: {result_dict.get('error')}")
            return format_f25_output(date, "failed", error=result_dict.get("error", "未知錯誤"))

    except Exception as e:
        logger.exception(f"[F25] {date} 執行過程發生錯誤")
        return format_f25_output(date, "error", error=f"系統錯誤: {str(e)}")

    finally:
        # 確保瀏覽器被關閉
        if driver:
            try:
                driver.quit()
                logger.debug(f"[F25] {date} Chrome 瀏覽器已關閉")
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
