"""
f01_fetcher.py
台指期貨外資未平倉淨口數抓取模組

功能：
- 從 TAIFEX 網站抓取台指期貨外資未平倉資料
- 提供 fetch(date: str) -> dict 統一介面
- 支援 MultiIndex 和單層表頭兩種格式
- 完整錯誤處理和日誌記錄
"""

import sys
import json
import logging
import requests
import pandas as pd
from typing import Dict, Optional
from datetime import datetime

# 模組識別
MODULE_ID = "f01"
MODULE_NAME = "f01_fetcher"

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def convert_to_int(value) -> int:
    """
    將字串轉換為整數，處理千分位逗號和空值
    
    Args:
        value: 待轉換的值
        
    Returns:
        整數值，無法轉換時返回 0
    """
    if pd.isna(value):
        return 0
    try:
        return int(str(value).replace(',', '').strip())
    except (ValueError, AttributeError):
        return 0


def find_column_multiindex(df: pd.DataFrame, keywords: list) -> Optional[tuple]:
    """
    在 MultiIndex 欄位中尋找包含特定關鍵字的欄位
    
    Args:
        df: DataFrame
        keywords: 關鍵字列表
        
    Returns:
        找到的欄位 tuple，找不到返回 None
    """
    for col in df.columns:
        col_str = ''.join(str(c) for c in col)
        if all(keyword in col_str for keyword in keywords):
            return col
    return None


def find_column_single(df: pd.DataFrame, possible_names: list) -> Optional[str]:
    """
    在單層欄位中尋找可能的欄位名稱
    
    Args:
        df: DataFrame
        possible_names: 可能的欄位名稱列表
        
    Returns:
        找到的欄位名稱，找不到返回 None
    """
    for name in possible_names:
        if name in df.columns:
            return name
    return None


def extract_foreign_data_multiindex(df: pd.DataFrame, date: str) -> Dict:
    """
    從 MultiIndex 表格中提取外資資料
    
    Args:
        df: MultiIndex DataFrame
        date: 查詢日期
        
    Returns:
        結果字典
    """
    # 尋找身份別欄位
    trader_col = None
    for col in df.columns:
        if any('身份別' in str(c) or '身份' in str(c) for c in col):
            trader_col = col
            break
    
    if trader_col is None:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "failed",
            "error": "找不到身份別欄位"
        }
    
    # 篩選外資（可能是「外資及陸資」或「外資」）
    foreign_rows = df[df[trader_col].isin(['外資及陸資', '外資'])]
    
    if len(foreign_rows) == 0:
        available_traders = df[trader_col].unique().tolist()
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "failed",
            "error": f"找不到外資資料，可用身份別: {available_traders}"
        }
    
    # 尋找未平倉多方口數欄位
    long_col = find_column_multiindex(df, ['未平倉', '多方', '口'])
    short_col = find_column_multiindex(df, ['未平倉', '空方', '口'])
    
    if long_col is None or short_col is None:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "failed",
            "error": "找不到未平倉餘額的多/空口數欄位"
        }
    
    # 提取數據
    try:
        long_pos = convert_to_int(foreign_rows[long_col].values[0])
        short_pos = convert_to_int(foreign_rows[short_col].values[0])
        net_pos = long_pos - short_pos
        
        summary = f"台指期外資淨額 {net_pos:,} 口（多方 {long_pos:,}，空方 {short_pos:,}）"
        
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "success",
            "summary": summary,
            "data": {
                "long_position": long_pos,
                "short_position": short_pos,
                "net_position": net_pos
            },
            "source": "TAIFEX"
        }
        
    except (IndexError, KeyError) as e:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "failed",
            "error": f"資料提取失敗: {str(e)}"
        }


def extract_foreign_data_single(df: pd.DataFrame, date: str) -> Dict:
    """
    從單層欄位表格中提取外資資料
    
    Args:
        df: 單層欄位 DataFrame
        date: 查詢日期
        
    Returns:
        結果字典
    """
    # 尋找身份別欄位
    trader_col = find_column_single(
        df, 
        ['身份別', '身份', '交易人', '交易人名稱', '身分別']
    )
    
    if trader_col is None:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "failed",
            "error": f"找不到身份別欄位，可用欄位: {df.columns.tolist()}"
        }
    
    # 篩選外資
    foreign_rows = df[df[trader_col].isin(['外資及陸資', '外資'])]
    
    if len(foreign_rows) == 0:
        available_traders = df[trader_col].unique().tolist()
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "failed",
            "error": f"找不到外資資料，可用身份別: {available_traders}"
        }
    
    # 尋找多方和空方口數欄位
    long_col = find_column_single(
        df,
        ['未平倉餘額-多方-口數', '多方-口數', '多方口數', '多方', '多單口數']
    )
    short_col = find_column_single(
        df,
        ['未平倉餘額-空方-口數', '空方-口數', '空方口數', '空方', '空單口數']
    )
    
    if long_col is None or short_col is None:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "failed",
            "error": f"找不到多/空口數欄位，可用欄位: {df.columns.tolist()}"
        }
    
    # 提取數據
    try:
        long_pos = convert_to_int(foreign_rows.iloc[0][long_col])
        short_pos = convert_to_int(foreign_rows.iloc[0][short_col])
        net_pos = long_pos - short_pos
        
        summary = f"台指期外資淨額 {net_pos:,} 口（多方 {long_pos:,}，空方 {short_pos:,}）"
        
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "success",
            "summary": summary,
            "data": {
                "long_position": long_pos,
                "short_position": short_pos,
                "net_position": net_pos
            },
            "source": "TAIFEX"
        }
        
    except (IndexError, KeyError) as e:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "failed",
            "error": f"資料提取失敗: {str(e)}"
        }


def fetch(date: str) -> dict:
    """
    抓取指定日期的台指期貨外資未平倉資料
    
    Args:
        date: 日期字串 (YYYY-MM-DD)
        
    Returns:
        結果字典，格式:
        {
            "module": "f01",
            "date": "2025-12-01",
            "status": "success|failed|error",
            "summary": "摘要訊息（中文）",
            "data": {...},
            "source": "TAIFEX"
        }
    """
    # 驗證日期格式
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": "日期格式錯誤，請使用 YYYY-MM-DD"
        }
    
    # 轉換日期格式為 TAIFEX 格式
    url_date = date.replace('-', '/')
    url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={url_date}"
    
    try:
        # 發送 HTTP 請求
        logger.info(f"正在抓取 {date} 的資料...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = "utf-8"
        
        # 解析 HTML 表格（使用 BeautifulSoup 作為可靠方案）
        try:
            from lxml import html as lxml_html
            tree = lxml_html.fromstring(response.text.encode('utf-8'))
            tables = pd.read_html(response.text, flavor='lxml')
        except ImportError:
            logger.debug("lxml 不可用，改使用 BeautifulSoup...")
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            table_elements = soup.find_all('table')
            if not table_elements:
                return {
                    "module": MODULE_ID,
                    "date": date,
                    "status": "failed",
                    "error": "該日無交易資料（可能是假日或休市日）"
                }
            tables = [pd.read_html(str(table))[0] for table in table_elements]
        except Exception as e:
            logger.debug(f"解析失敗，嘗試備選方案: {e}")
            try:
                tables = pd.read_html(response.text)
            except Exception:
                return {
                    "module": MODULE_ID,
                    "date": date,
                    "status": "error",
                    "error": f"無法解析 HTML 表格: {str(e)}"
                }
        
        if len(tables) == 0:
            return {
                "module": MODULE_ID,
                "date": date,
                "status": "failed",
                "error": "該日無交易資料（可能是假日或休市日）"
            }
        
        # 取得第一個表格（通常是主要資料表）
        df = tables[0]
        
        # 根據表格類型處理
        if isinstance(df.columns, pd.MultiIndex):
            logger.debug("偵測到 MultiIndex 表頭")
            return extract_foreign_data_multiindex(df, date)
        else:
            logger.debug("偵測到單層表頭")
            return extract_foreign_data_single(df, date)
    
    except requests.Timeout:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": "連線逾時，請檢查網路連線"
        }
    
    except requests.HTTPError as e:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": f"HTTP 錯誤 {e.response.status_code}"
        }
    
    except requests.RequestException as e:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": f"網路請求失敗: {str(e)}"
        }
    
    except ValueError as e:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": f"HTML 解析失敗: {str(e)}"
        }
    
    except Exception as e:
        logger.exception("未預期的錯誤")
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": f"未預期的錯誤: {str(e)}"
        }


def main():
    """主程式進入點，供獨立測試使用"""
    if len(sys.argv) > 1:
        test_date = sys.argv[1]
    else:
        # 預設測試日期
        test_date = '2025-11-28'
    
    print(f"測試日期: {test_date}")
    print("-" * 60)
    
    result = fetch(test_date)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 根據狀態設定退出碼
    sys.exit(0 if result.get("status") == "success" else 1)


if __name__ == '__main__':
    main()