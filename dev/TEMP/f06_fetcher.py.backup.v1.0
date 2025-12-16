"""
f06_fetcher.py - 臺指選擇權波動率指數抓取模組 v1.0

【模組功能】
- 從 TAIFEX 網站抓取臺指選擇權波動率指數（VIX）
- 提供統一的 fetch(date: str) -> str 介面
- 自動偵測 HTML 表格格式
- 完整的錯誤處理和日誌記錄

【主要入口】
- fetch(date: str) -> str
  入參: 日期字串 (YYYY-MM-DD 格式)
  返值: 統一格式的文字結果
  
  成功範例: "2025.12.15  F06: 臺指選擇權波動率指數 : 18.50 [TAIFEX]"
  失敗範例: "F06 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]"

【重要限制】
- TAIFEX API 端點無視日期參數，永遠返回當天波動率資料
- 非交易日無波動率數據，無法查詢歷史波動率
- 若要支援歷史查詢，需使用 Selenium 或其他瀏覽器自動化
- 表格格式可能隨 TAIFEX 網站更新而改變，需定期驗證

【依賴套件】
- requests >= 2.28.0 (HTTP 請求)
- pandas >= 1.5.0 (表格解析)
- lxml >= 4.9.0 (HTML 解析，可選)
- beautifulsoup4 >= 4.11.0 (HTML 解析備選)

【版本歷史】
- v1.0: 初始版本，OpenSpec 實現 (2025-12-15)

【錯誤代碼表】
| 錯誤類型 | 原因 | 解決方案 |
|---------|------|--------|
| 日期格式錯誤 | 輸入格式非 YYYY-MM-DD | 檢查日期格式 |
| 連線逾時 | 網路延遲或 TAIFEX 無回應 | 檢查網路、稍後重試 |
| HTTP 錯誤 | 伺服器返回 4xx/5xx | 檢查 API 端點 |
| HTML 解析失敗 | 表格格式改變 | 更新欄位搜尋邏輯 |
| 無交易資料 | 假日或休市日 | 改查交易日期 |

【日誌配置】
模組使用 Python logging，預設級別為 INFO
- INFO: 主要操作（開始抓取、完成、失敗）
- DEBUG: 流程分支（格式偵測、欄位搜尋）
- ERROR: 無法恢復的異常
"""

import io
import logging
import sys
from datetime import datetime
from typing import Optional, TypedDict

import pandas as pd
import requests


class VIXDataDict(TypedDict):
    """波動率指數資料字典結構（用於 format_f06_output 的 data 參數）"""
    vix_value: float       # 波動率指數數值 (必須)
    source: str           # 資料來源（通常為 "TAIFEX"）


class ErrorContextDict(TypedDict, total=False):
    """錯誤上下文字典結構（用於 format_f06_output 的 context 參數）
    
    total=False 表示所有欄位都是可選的，因為不同錯誤類型記錄不同上下文。
    """
    timeout: int          # 逾時秒數 (requests.Timeout 時)
    status_code: int      # HTTP 狀態碼 (requests.HTTPError 時)
    step: str             # 失敗步驟名稱 (自訂異常時)
    error_type: str       # 異常類型名稱


class FetchResultDict(TypedDict, total=False):
    """fetch() 的結果字典結構，用於內部返回複雜的資料結構"""
    module: str           # 模組 ID ("f06")
    date: str             # 查詢日期
    status: str           # "success" / "failed" / "error"
    summary: str          # 成功時的摘要訊息
    error: str            # 失敗時的錯誤訊息
    data: VIXDataDict     # 成功時的資料
    source: str           # 資料來源


# 設定 UTF-8 輸出（解決 Windows 終端亂碼，PyInstaller 已處理打包的情境）
# 只在尚未包裝時才進行包裝，避免重複包裝導致 I/O 錯誤
if sys.platform == 'win32' and not getattr(sys, "frozen", False):
    if not hasattr(sys.stdout, '_wrapped_for_utf8'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stdout._wrapped_for_utf8 = True

# 設定日誌記錄器
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# 模組識別
MODULE_ID = "f06"  # 小寫，用於內部
SOURCE = "TAIFEX"


def format_f06_output(
    date: str,
    status: str,
    data: Optional[VIXDataDict] = None,
    error: Optional[str] = None,
    timestamp: Optional[str] = None,
    context: Optional[ErrorContextDict] = None
) -> str:
    """
    格式化輸出為統一文字格式
    
    【功能說明】
    將 fetch() 的各種返回情況（成功、失敗、異常）統一格式化為文字字串。
    支援三種輸出格式：成功、失敗、異常（帶時間戳和上下文）。
    
    【參數說明】
    Args:
        date (str): 查詢日期 (YYYY-MM-DD 格式)
                   範例: "2025-12-15"
        
        status (str): 返回狀態，必須為以下三種之一
                    - "success": 成功抓取資料
                    - "failed": 失敗，但不拋出異常（如假日無資料）
                    - "error": 異常情況（網路錯誤、解析失敗等）
        
        data (Optional[VIXDataDict]): 成功時的資料字典
                    - vix_value: float，波動率指數數值
                    - source: str，資料來源
                    僅在 status="success" 時使用
                    範例: {"vix_value": 18.50, "source": "TAIFEX"}
        
        error (Optional[str]): 失敗或異常時的錯誤訊息
                    - 應為使用者友善的簡短訊息
                    - 範例: "連線逾時，請檢查網路連線"
                    - 範例: "該日無交易資料（可能是假日或休市日）"
        
        timestamp (Optional[str]): [v1.0 新增] 異常發生時間戳
                    只在 status="error" 時使用，搭配 error 使用
                    格式: "YYYY-MM-DD HH:MM:SS"
                    範例: "2025-12-15 14:30:45"
                    生成方式: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        context (Optional[Dict]): [v1.0 新增] 異常上下文字典
                    只在 status="error" 時使用，記錄詳細信息便於追蹤
                    常見欄位:
                    - "timeout": 整數，逾時秒數 (如 30)
                    - "status_code": 整數，HTTP 狀態碼 (如 404)
                    - "step": 字串，失敗步驟 (如 "html_parsing")
                    範例: {"timeout": 30}
                    範例: {"status_code": 404}
    
    【返回值】
    Returns:
        str: 格式化後的統一文字字串
        
        格式化規則:
        
        1. 成功 (status="success" + data):
           格式: "{date}  F06: 臺指選擇權波動率指數 : {vix:.2f} [TAIFEX]"
           說明: 日期用點號分隔 (2025.12.15 格式)，數字保留小數後 2 位
           範例: "2025.12.15  F06: 臺指選擇權波動率指數 : 18.50 [TAIFEX]"
        
        2. 失敗 (status="failed" + error):
           格式: "F06 錯誤: {error} [TAIFEX]"
           說明: 無時間戳和上下文
           範例: "F06 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]"
        
        3. 異常 (status="error" + error + timestamp):
           基礎格式: "F06 錯誤: {error} [TAIFEX] ({timestamp}"
           說明: 包含時間戳，用於精確定位
           範例: "F06 錯誤: 連線逾時 [TAIFEX] (2025-12-15 14:30:45)"
        
        4. 異常+上下文 (status="error" + error + timestamp + context):
           完整格式: "F06 錯誤: {error} [TAIFEX] ({timestamp}, context_str)"
           說明: 包含時間戳和詳細上下文
           上下文格式化規則:
           - "timeout" 值後加 "s" (如 timeout=30s)
           - 其他值直接格式化 (如 status_code=404)
           - 多個欄位用逗號分隔
           範例: "F06 錯誤: 連線逾時 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)"
           範例: "F06 錯誤: HTTP 錯誤 404 [TAIFEX] (2025-12-15 14:30:45, status_code=404)"
    
    【內部行為】
    - 成功情況：不記錄日誌
    - failed 情況：logger.warning() 記錄警告
    - error 情況：logger.error() 記錄錯誤信息
    - 敏感信息過濾：URL 和完整 traceback 不寫入日誌
    
    【使用範例】
    
    Example 1 - 成功情況:
        >>> result = format_f06_output(
        ...     date="2025-12-15",
        ...     status="success",
        ...     data={"vix_value": 18.50, "source": "TAIFEX"}
        ... )
        >>> print(result)
        2025.12.15  F06: 臺指選擇權波動率指數 : 18.50 [TAIFEX]
    
    Example 2 - 失敗情況（假日）:
        >>> result = format_f06_output(
        ...     date="2025-12-14",
        ...     status="failed",
        ...     error="該日無交易資料（可能是假日或休市日）"
        ... )
        >>> print(result)
        F06 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]
    
    Example 3 - 異常情況（逾時，只有時間戳）:
        >>> result = format_f06_output(
        ...     date="2025-12-15",
        ...     status="error",
        ...     error="連線逾時，請檢查網路連線",
        ...     timestamp="2025-12-15 14:30:45"
        ... )
        >>> print(result)
        F06 錯誤: 連線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45)
    
    Example 4 - 異常情況（逾時+上下文）:
        >>> result = format_f06_output(
        ...     date="2025-12-15",
        ...     status="error",
        ...     error="連線逾時，請檢查網路連線",
        ...     timestamp="2025-12-15 14:30:45",
        ...     context={"timeout": 30}
        ... )
        >>> print(result)
        F06 錯誤: 連線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)
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
        # v1.0 錯誤格式：簡潔風格
        result = f"{module_code} 錯誤: {error_msg} [TAIFEX]"
        
        # [NEW] 增加時間戳和上下文後綴
        suffix = ""
        if timestamp:
            suffix += f" ({timestamp}"
            
        if context:
            # 【上下文格式化】
            # timeout 需要特殊處理（加 "s" 單位表示秒數）
            # 其他欄位直接拼接（如 status_code=404）
            context_parts = []
            for k, v in context.items():
                if k == "timeout":
                    context_parts.append(f"{k}={v}s")  # timeout 特殊處理：加 s 單位
                else:
                    context_parts.append(f"{k}={v}")    # 其他欄位直接拼接
            context_str = ", ".join(context_parts)
            
            if suffix:
                suffix += f", {context_str})"
            else:
                suffix = f" ({context_str})"
        elif suffix:
            suffix += ")"
        
        result += suffix
        
        # [NEW] 記錄到日誌
        if status == "error":
            logger.error(
                f"[F06] {date} 異常",
                extra={"error": error, "timestamp": timestamp, "context": context}
            )
        elif status == "failed":
            logger.warning(
                f"[F06] {date} 無交易資料或解析失敗",
                extra={"error": error}
            )
        
        return result


def extract_vix_value(df: pd.DataFrame, date: str) -> Optional[FetchResultDict]:
    """
    從 DataFrame 中提取波動率指數數值
    
    【功能說明】
    尋找 DataFrame 中的波動率指數欄位，提取數值。
    適應多種表格格式（MultiIndex、單層表頭）。
    
    【參數說明】
    Args:
        df (pd.DataFrame): 從 HTML 表格解析後的 DataFrame
        date (str): 查詢日期，用於日誌記錄
    
    【返回值】
    Returns:
        Optional[FetchResultDict]: 成功時返回結果字典，失敗時返回 None
    """
    try:
        # 【策略 1】MultiIndex 表頭（複雜表格）
        if isinstance(df.columns, pd.MultiIndex):
            logger.debug(f"[F06] {date} 偵測到 MultiIndex 表頭")
            # 尋找包含「波動率」或「VIX」的欄位
            for col in df.columns:
                col_str = ''.join(str(c) for c in col)
                if '波動率' in col_str or 'vix' in col_str.lower():
                    try:
                        value = float(df[col].iloc[0])
                        return {
                            "module": MODULE_ID,
                            "date": date,
                            "status": "success",
                            "data": {"vix_value": value, "source": SOURCE},
                            "source": SOURCE
                        }
                    except (ValueError, IndexError, TypeError):
                        continue
        
        # 【策略 2】單層表頭（扁平表格）
        else:
            logger.debug(f"[F06] {date} 偵測到單層表頭")
            # 可能的欄位名稱（優先級排列）
            possible_names = [
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
                        logger.debug(f"[F06] {date} 找到欄位: {name} = {value}")
                        return {
                            "module": MODULE_ID,
                            "date": date,
                            "status": "success",
                            "data": {"vix_value": value, "source": SOURCE},
                            "source": SOURCE
                        }
                    except (ValueError, IndexError, TypeError):
                        continue
        
        # 【無法找到欄位】
        logger.warning(f"[F06] {date} 無法在表格中找到波動率指數欄位")
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "failed",
            "error": "該日無交易資料（可能是假日或休市日）"
        }

    except Exception as e:
        logger.error(f"[F06] {date} 數據提取失敗: {str(e)}")
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "failed",
            "error": f"資料提取失敗: {str(e)}"
        }


def fetch(date: str) -> str:
    """
    抓取指定日期的臺指選擇權波動率指數
    
    【功能說明】
    從 TAIFEX 網站的 vixMinNew API 抓取臺指選擇權波動率指數。
    由於 API 限制，實際返回的是最新波動率資料，而非指定日期資料。
    
    【參數】
    Args:
        date (str): 日期字串，格式必須為 YYYY-MM-DD
                    範例: "2025-12-15"
                    
    【返回值】
    Returns:
        str: 統一格式的文字字串，包含以下情況：
        
        1. 成功情況 (包含波動率資料):
           格式: "{date}  F06: 臺指選擇權波動率指數 : {vix} [TAIFEX]"
           範例: "2025.12.15  F06: 臺指選擇權波動率指數 : 18.50 [TAIFEX]"
           
        2. 失敗情況 (可恢復的異常):
           格式: "F06 錯誤: {錯誤訊息} [TAIFEX]"
           範例: "F06 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]"
           
        3. 異常情況 (需增強上下文):
           格式: "F06 錯誤: {訊息} [TAIFEX] ({timestamp}, {context})"
           範例: "F06 錯誤: 連線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)"
    
    【異常處理】
    Raises:
        (函數不拋出異常，所有異常都被捕捉並轉為文字返回)
        
        但會記錄以下異常類型到日誌：
        
        1. ValueError - 日期格式驗證失敗
           觸發時機: 輸入不符 YYYY-MM-DD 格式
           日誌級別: INFO
           返回範例: "F06 錯誤: 日期格式錯誤，請使用 YYYY-MM-DD [TAIFEX]"
           
        2. requests.Timeout - 網路連線逾時
           觸發時機: HTTP 請求超過 30 秒無回應
           日誌級別: ERROR + context = {timeout: 30}
           返回範例: "F06 錯誤: 連線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)"
           
        3. requests.HTTPError - HTTP 狀態碼異常 (4xx/5xx)
           觸發時機: TAIFEX 伺服器返回錯誤碼
           日誌級別: ERROR + context = {status_code: xxx}
           返回範例: "F06 錯誤: HTTP 錯誤 404 [TAIFEX] (2025-12-15 14:30:45, status_code=404)"
           
        4. requests.RequestException - 其他網路異常
           觸發時機: DNS 解析失敗、連線被拒等
           日誌級別: ERROR
           返回範例: "F06 錯誤: 網路請求失敗: [Errno 11001] getaddrinfo failed [TAIFEX]"
           
        5. Exception - 未預期的異常
           觸發時機: HTML 解析、邏輯計算等意外錯誤
           日誌級別: ERROR (使用 logger.exception 記錄完整 traceback)
           返回範例: "F06 錯誤: 未預期的錯誤: index out of range [TAIFEX]"
    
    【使用範例】
    
    Example 1 - 正常使用:
        >>> result = fetch("2025-12-15")
        >>> print(result)
        2025.12.15  F06: 臺指選擇權波動率指數 : 18.50 [TAIFEX]
    
    Example 2 - 日期格式錯誤:
        >>> result = fetch("2025-12/15")  # 錯誤格式
        >>> print(result)
        F06 錯誤: 日期格式錯誤，請使用 YYYY-MM-DD [TAIFEX]
    
    Example 3 - 網路異常:
        >>> result = fetch("2025-12-15")  # 當網路無法連接時
        >>> print(result)
        F06 錯誤: 連線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)
    
    Example 4 - 假日查詢:
        >>> result = fetch("2025-12-14")  # 假日
        >>> print(result)
        F06 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]
    
    【注意事項】
    - 函數會自動將日期轉換為 TAIFEX API 格式（日期參數不使用）
    - 由於 API 限制，任何日期輸入都返回最新波動率的資料
    - 函數使用 30 秒逾時設定，用於檢測卡住的連線
    - 所有異常都會記錄到 logger，支援日誌分析和追蹤
    """
    # 驗證日期格式
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        logger.info(f"[F06] {date} 日期格式驗證失敗")
        return format_f06_output(date, "error", error="日期格式錯誤，請使用 YYYY-MM-DD")
    
    # TAIFEX VIX 端點（注意：日期參數通常被忽略，返回最新波動率）
    url = "https://www.taifex.com.tw/cht/7/vixMinNew"
    
    try:
        # 發送 HTTP 請求
        logger.info(f"[F06] {date} 開始抓取資料")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = "utf-8"
        
        # 解析 HTML 表格（使用 BeautifulSoup 作為可靠方案）
        try:
            tables = pd.read_html(response.text, flavor='lxml')
        except ImportError:
            logger.debug("lxml 不可用，改使用 BeautifulSoup...")
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            table_elements = soup.find_all('table')
            if not table_elements:
                return format_f06_output(date, "failed", error="該日無交易資料（可能是假日或休市日）")
            tables = [pd.read_html(str(table))[0] for table in table_elements]
        except Exception as e:
            logger.debug(f"解析失敗，嘗試備選方案: {e}")
            try:
                tables = pd.read_html(response.text)
            except Exception:
                return format_f06_output(date, "error", error=f"無法解析 HTML 表格: {str(e)}")

        if len(tables) == 0:
            return format_f06_output(date, "failed", error="該日無交易資料（可能是假日或休市日）")
        
        # 【表格處理】
        # 嘗試從每個表格中提取波動率指數
        for idx, df in enumerate(tables):
            logger.debug(f"[F06] {date} 處理第 {idx+1} 個表格，形狀: {df.shape}")
            result_dict = extract_vix_value(df, date)
            
            if result_dict and result_dict.get("status") == "success":
                # 成功找到波動率指數
                return format_f06_output(date, "success", data=result_dict.get("data"))
        
        # 所有表格都無法提取波動率指數
        return format_f06_output(date, "failed", error="該日無交易資料（可能是假日或休市日）")

    except requests.Timeout:
        # 網路連線逾時
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context = {"timeout": 30}
        logger.error(
            f"[F06] {date} 連線逾時",
            extra={"timestamp": timestamp, "timeout": 30}
        )
        return format_f06_output(
            date, "error",
            error="連線逾時，請檢查網路連線",
            timestamp=timestamp,
            context=context
        )

    except requests.HTTPError as e:
        # HTTP 錯誤
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context = {"status_code": e.response.status_code}
        logger.error(
            f"[F06] {date} HTTP 錯誤 {e.response.status_code}",
            extra={"timestamp": timestamp, "status_code": e.response.status_code}
        )
        return format_f06_output(
            date, "error",
            error=f"HTTP 錯誤 {e.response.status_code}",
            timestamp=timestamp,
            context=context
        )

    except requests.RequestException as e:
        # 其他網路異常
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.error(
            f"[F06] {date} 網路請求失敗",
            extra={"timestamp": timestamp}
        )
        return format_f06_output(
            date, "error",
            error=f"網路請求失敗: {str(e)}",
            timestamp=timestamp
        )

    except Exception as e:
        # 未預期的異常
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.exception(f"[F06] {date} 未預期的錯誤")
        return format_f06_output(
            date, "error",
            error=f"未預期的錯誤: {str(e)}",
            timestamp=timestamp
        )


def main():
    """主程式進入點，供獨立測試使用"""
    if len(sys.argv) > 1:
        test_date = sys.argv[1]
    else:
        # 預設測試日期（使用當前日期）
        test_date = datetime.now().strftime("%Y-%m-%d")

    print(f"測試日期: {test_date}")
    print("-" * 60)

    result = fetch(test_date)
    # 直接輸出文字（不再使用 json.dumps）
    print(result)

    # 判斷成功/失敗（檢查是否包含「錯誤:」）
    sys.exit(0 if "錯誤:" not in result else 1)


if __name__ == '__main__':
    main()
