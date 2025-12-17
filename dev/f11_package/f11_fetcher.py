"""
F11 Module: Taiwan Weighted Stock Index (加權股價收盤指數)
=========================================================

This module provides real-time Taiwan Weighted Stock Index (TAIEX) data extraction
from the Taiwan Stock Exchange (TWSE) official website.

Functions:
    fetch_taiex_index() -> str
        Fetches the latest TAIEX closing index from TWSE.
        Returns a formatted string with the index value or error message.

Output Format:
    Success: "YYYY.MM.DD  F11: 加權股價收盤指數 : [VALUE] [TWSE]"
    Error:   "F11 錯誤: [ERROR_MESSAGE] [TWSE]"

Dependencies:
    requests >= 2.28.0
    beautifulsoup4 >= 4.11.0

Author: F11 Development Team
Version: 1.0.0
Created: 2025-12-17
"""

import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# ============================================================================
# LOGGING CONFIGURATION (Task 2.1)
# ============================================================================

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 禁用向上傳播，避免 run.py 環境中的 stdout 問題
logger.propagate = False

# Create console handler if not already present (僅在獨立執行時使用)
if not logger.handlers and __name__ == "__main__":
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create formatter with [F11] prefix
    formatter = logging.Formatter(
        fmt='[F11] %(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# ============================================================================
# CONSTANTS AND CONFIGURATION (Task 2.1)
# ============================================================================

TWSE_URL = "https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html"
HTTP_TIMEOUT = 10  # seconds
MAX_RETRIES = 1
COLUMN_VARIANTS = [
    '目前指數',           # Primary column name
    '臺指選擇權波動率指數',
    '波動率指數',
    'VIX指數',
    'VIX',
    '波動率',
    'Volatility Index',
    'VIX Close'
]

# ============================================================================
# MAIN FUNCTION: fetch_taiex_index() (Tasks 2.2, 2.3, 2.4, 2.5)
# ============================================================================

def fetch_taiex_index() -> str:
    """
    Fetch the latest Taiwan Weighted Stock Index (TAIEX) from TWSE.
    
    This function uses Selenium to load the dynamic TWSE webpage, wait for the
    data table to load, and extract the closing index value. The result is 
    returned in a standardized format. All exceptions are caught and converted 
    to error messages.
    
    Returns:
        str: Formatted result string
            - Success: "YYYY.MM.DD  F11: 加權股價收盤指數 : [VALUE] [TWSE]"
            - Error:   "F11 錯誤: [ERROR_MESSAGE] [TWSE]"
    
    Raises:
        None - All exceptions are caught internally and returned as error strings
    
    Examples:
        >>> result = fetch_taiex_index()
        >>> print(result)
        2025.12.17  F11: 加權股價收盤指數 : 18254.50 [TWSE]
        
        >>> result = fetch_taiex_index()  # On non-trading day
        >>> print(result)
        F11 錯誤: 該日無交易資料（可能是假日或休市日） [TWSE]
    """
    
    logger.info("開始抓取加權股價收盤指數...")
    
    driver = None
    try:
        # ====================================================================
        # Task 2.2: Selenium 初始化與頁面載入
        # ====================================================================
        
        logger.debug(f"初始化 Selenium WebDriver...")
        
        # Setup Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Initialize WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        logger.debug(f"向 TWSE 發送請求: {TWSE_URL}")
        driver.get(TWSE_URL)
        
        logger.debug("等待數據表格加載...")
        
        # Wait for table to load (max 10 seconds)
        wait = WebDriverWait(driver, HTTP_TIMEOUT)
        
        # Try to find and wait for the data table
        try:
            table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            logger.debug("數據表格已加載")
        except Exception as e:
            logger.warning(f"無法找到表格，嘗試替代方法：{str(e)}")
            # Try alternative: look for divs with data
            html_source = driver.page_source
            driver.quit()
            driver = None
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_source, 'html.parser')
            
            # Try to find data in divs or other structures
            # TWSE 可能使用 JavaScript 動態載入，無法從靜態 HTML 解析
            logger.error("頁面結構異常：無法找到數據表格")
            return f"F11 錯誤: 無法解析頁面結構 [TWSE]"
        
        # ====================================================================
        # Task 2.3: 提取指數值
        # ====================================================================
        
        # Get page source and parse with BeautifulSoup
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        
        # Find the data table
        table = soup.find('table')
        if not table:
            logger.error("未找到數據表格")
            return f"F11 錯誤: 無法解析頁面結構 [TWSE]"
        
        logger.debug("找到數據表格")
        
        # Get all table rows
        rows = table.find_all('tr')
        if not rows or len(rows) < 2:
            logger.warning("表格為空或數據不足，無交易數據")
            return f"F11 錯誤: 該日無交易資料（可能是假日或休市日） [TWSE]"
        
        logger.debug(f"表格包含 {len(rows)} 行資料")
        
        # Get table headers to find the index column
        header_row = rows[0]
        headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        
        logger.debug(f"表格標題: {headers}")
        
        # Find the index column - look for variants
        # For TAIEX, the column might be "現在指數", "目前指數", etc.
        index_col = None
        search_names = ['現在指數', '目前指數', '收盤指數', '指數', 'Index', '加權股價']
        
        for col_name in search_names:
            for i, header in enumerate(headers):
                if col_name in header:
                    index_col = i
                    logger.debug(f"找到指數列：'{header}' (列 {index_col})")
                    break
            if index_col is not None:
                break
        
        if index_col is None:
            logger.error(f"無法找到指數列，可用列: {headers}")
            return f"F11 錯誤: 無法解析頁面結構 [TWSE]"
        
        # Extract index value from the last row (most recent data)
        last_row = rows[-1]
        cells = last_row.find_all(['td', 'th'])
        
        if index_col >= len(cells):
            logger.error(f"列索引越界：{index_col} >= {len(cells)}")
            return f"F11 錯誤: 無法解析頁面結構 [TWSE]"
        
        index_str = cells[index_col].get_text(strip=True)
        logger.debug(f"提取的原始值: '{index_str}'")
        
        # Clean up the value (remove commas, spaces, etc.)
        index_str = index_str.replace(',', '').replace(' ', '').strip()
        
        # Remove any non-numeric characters except decimal point
        index_str = re.sub(r'[^\d.]', '', index_str)
        
        if not index_str:
            logger.warning("無法解析指數值，表格可能無數據")
            return f"F11 錯誤: 該日無交易資料（可能是假日或休市日） [TWSE]"
        
        # Try to convert to float
        try:
            index_value = float(index_str)
        except ValueError as e:
            logger.error(f"無法轉換指數值為浮點數：'{index_str}' - {str(e)}")
            return f"F11 錯誤: 數據格式異常 [TWSE]"
        
        logger.debug(f"成功轉換指數值: {index_value}")
        
        # ====================================================================
        # Task 2.4: 格式化輸出
        # ====================================================================
        
        # Get current date
        today = datetime.now()
        date_str = today.strftime("%Y.%m.%d")
        
        # Format the index value to 2 decimal places
        formatted_value = f"{index_value:.2f}"
        
        # Create the success output string
        output = f"{date_str}  F11: 加權股價收盤指數 : {formatted_value} [TWSE]"
        
        logger.info(f"成功提取指數值：{formatted_value}")
        logger.info(f"輸出: {output}")
        
        return output
    
    # ========================================================================
    # Task 2.5: 異常處理
    # ========================================================================
    
    except Exception as e:
        # Catch-all for all exceptions
        error_type = type(e).__name__
        logger.error(f"{error_type}：{str(e)}", exc_info=True)
        return f"F11 錯誤: 系統異常 [TWSE]"
    
    finally:
        # Clean up WebDriver
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.debug(f"WebDriver 清理時出錯：{str(e)}")


# ============================================================================
# HELPER FUNCTION: format_taiex_output() (Task 2.4)
# ============================================================================

def format_taiex_output(index_value: float, date: datetime = None) -> str:
    """
    Format TAIEX index value into standardized output string.
    
    Args:
        index_value (float): The TAIEX closing index value
        date (datetime, optional): The date for the index. Defaults to today.
    
    Returns:
        str: Formatted string in the format:
             "YYYY.MM.DD  F11: 加權股價收盤指數 : [VALUE] [TWSE]"
    
    Examples:
        >>> format_taiex_output(18254.50)
        '2025.12.17  F11: 加權股價收盤指數 : 18254.50 [TWSE]'
    """
    
    if date is None:
        date = datetime.now()
    
    date_str = date.strftime("%Y.%m.%d")
    formatted_value = f"{index_value:.2f}"
    
    return f"{date_str}  F11: 加權股價收盤指數 : {formatted_value} [TWSE]"


# ============================================================================
# HELPER FUNCTION: format_taiex_error() (Task 2.4)
# ============================================================================

def format_taiex_error(error_msg: str, include_timestamp: bool = False) -> str:
    """
    Format error message into standardized error output string.
    
    Args:
        error_msg (str): The error message
        include_timestamp (bool): Whether to include timestamp in error. Default False.
    
    Returns:
        str: Formatted error string in the format:
             "F11 錯誤: [ERROR_MSG] [TWSE]"
             or with timestamp:
             "F11 錯誤: [ERROR_MSG] [TWSE] (YYYY-MM-DD HH:MM:SS)"
    
    Examples:
        >>> format_taiex_error("網路連線失敗")
        'F11 錯誤: 網路連線失敗 [TWSE]'
        
        >>> format_taiex_error("網路連線失敗", include_timestamp=True)
        'F11 錯誤: 網路連線失敗 [TWSE] (2025-12-17 14:30:45)'
    """
    
    if include_timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"F11 錯誤: {error_msg} [TWSE] ({timestamp})"
    else:
        return f"F11 錯誤: {error_msg} [TWSE]"


# ============================================================================
# STANDARD INTERFACE: fetch(date) (run.py 兼容)
# ============================================================================

def fetch(date: str) -> str:
    """
    標準介面函數，供 run.py 調用

    Args:
        date (str): 查詢日期 (YYYY-MM-DD 格式)
                   注意: F11 模組返回即時數據，不使用此日期參數

    Returns:
        str: 格式化的結果字串

    Examples:
        >>> result = fetch("2025-12-17")
        >>> print(result)
        2025.12.17  F11: 加權股價收盤指數 : 18254.50 [TWSE]
    """
    # F11 模組返回即時數據，忽略 date 參數
    return fetch_taiex_index()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    Test the F11 module directly
    """
    logger.info("開始 F11 模組測試...")
    result = fetch_taiex_index()
    print(result)
    logger.info("測試完成")
