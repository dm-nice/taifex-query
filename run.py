"""
===========================================================
 run.py  —  模組統一執行程式
===========================================================

【功能】
- 自動執行指定日期的所有模組
- 將結果統一輸出到 C:\Taifex\data\
- 支援正式模式和驗收模式
- 提供詳細的執行日誌
- 自動往回搜尋最近交易日（當日無資料時）

【使用方式】
  python run.py [日期] [模式] [--module 模組名稱] [--session 時段] [--no-auto-date]

【範例】
  python run.py                              # 執行今天（全部模組，自動找交易日）
  python run.py 2025-12-01                   # 執行指定日期（自動找交易日）
  python run.py 2025-12-01 --session morning   # 僅執行早盤模組 (F01-F17)
  python run.py 2025-12-01 --session night     # 僅執行夜盤模組 (F21-F25)
  python run.py 2025-12-01 --no-auto-date    # 停用自動找交易日功能
  python run.py 2025-12-01 dev               # 驗收模式
  python run.py 2025-12-01 dev --module f01_fetcher_dev
  python run.py --help                       # 顯示說明
===========================================================
"""

import sys
import logging
import importlib
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# ===== 專案路徑設定 =====
if getattr(sys, "frozen", False):
    base_dir = Path(sys.executable).resolve().parent
else:
    base_dir = Path(__file__).resolve().parent

if (base_dir / "modules").exists():
    PROJECT_ROOT = base_dir
elif (base_dir.parent / "modules").exists():
    PROJECT_ROOT = base_dir.parent
else:
    PROJECT_ROOT = base_dir

BASE_DIR = PROJECT_ROOT / "data"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 快取已載入的模組以提升效能（避免重複 import 造成的開銷）
MODULE_CACHE = {}

# 台灣期貨市場分為早盤(09:00-13:45)和夜盤(15:00-05:00)兩個交易時段
MORNING_MODULES = range(1, 18)    # F01-F17 早盤模組
NIGHT_MODULES = range(21, 26)     # F21-F25 夜盤模組

# 自動找交易日的設定
MAX_TRADING_DAY_SEARCH = 10       # 最多往回找幾天
TRADING_DAY_CHECK_MODULE = "f01_fetcher"  # 用來判斷是否為交易日的模組


class ModuleStatus(Enum):
    """模組執行狀態"""
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"
    INVALID = "invalid"
    
    @property
    def icon(self) -> str:
        """取得對應圖示"""
        icons = {
            self.SUCCESS: "✅",
            self.FAILED: "⚠️ ",
            self.ERROR: "❌",
            self.INVALID: "⛔"
        }
        return icons[self]
    
    @property
    def chinese_name(self) -> str:
        """取得中文名稱"""
        names = {
            self.SUCCESS: "成功",
            self.FAILED: "失敗",
            self.ERROR: "錯誤",
            self.INVALID: "無效"
        }
        return names[self]


@dataclass
class ExecutionContext:
    """執行上下文資料"""
    query_date: str
    dev_mode: bool
    only_module: Optional[str]
    session: Optional[str]
    folder: str
    mode: str
    exec_day: str
    exec_time: str
    exec_time_short: str
    log_file: Path


@dataclass
class ExecutionStats:
    """執行統計資料"""
    success: int = 0
    failed: int = 0
    error: int = 0
    invalid: int = 0
    total: int = 0
    
    def increment(self, status: str):
        """增加指定狀態的計數"""
        if hasattr(self, status):
            setattr(self, status, getattr(self, status) + 1)
    
    def get_percentages(self) -> Dict[str, float]:
        """計算各狀態的百分比"""
        if self.total == 0:
            return {'success': 0, 'failed': 0, 'error': 0, 'invalid': 0}
        
        return {
            'success': self.success / self.total * 100,
            'failed': self.failed / self.total * 100,
            'error': self.error / self.total * 100,
            'invalid': self.invalid / self.total * 100
        }


class SafeConsoleHandler(logging.Handler):
    """安全的 Console Handler - 避免因 stdout 被關閉而出錯"""
    
    def __init__(self):
        super().__init__()
        self._last_msg = ''
        self._show_patterns = self._get_display_patterns()
    
    def _get_display_patterns(self) -> List[str]:
        """定義需要顯示的訊息模式"""
        return [
            '═════',              # 標題分隔線
            '📅 查詢日期:',       # 查詢日期
            '⏰ 執行時間:',       # 執行時間
            '🔧 執行模式:',       # 執行模式
            '🎯 指定模組:',       # 指定模組
            '🕐 執行時段:',       # 執行時段
            '⚙️  執行中:',        # 模組執行進度
            '📊 執行統計',        # 執行統計標題
            '總數:',              # 統計資訊
            '✅ 成功:',           # 成功數量
            '⚠️  失敗:',         # 失敗數量
            '❌ 錯誤:',           # 錯誤數量
            '⛔ 無效:',           # 無效數量
            '📝 詳細日誌:',       # 日誌位置
            '⚠️  在'              # 警告訊息
        ]
    
    def _should_display(self, msg: str) -> bool:
        """判斷訊息是否應該顯示"""
        # 避免顯示詳細日誌訊息，只保留使用者關心的摘要資訊
        if any(level in msg for level in ['[INFO]', '[ERROR]', '[WARNING]', '[DEBUG]']):
            return False
        
        if any(pattern in msg for pattern in self._show_patterns):
            return True
        
        if msg.strip() == '' and '═' in self._last_msg:
            return True
        
        return False
    
    def emit(self, record):
        try:
            msg = self.format(record)
            
            if self._should_display(msg):
                print(msg)
            
            self._last_msg = msg
        except Exception:
            pass


def setup_logger(log_file: Path) -> logging.Logger:
    """設定日誌記錄器"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    console_handler = SafeConsoleHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def _scan_python_modules(folder_path: Path, folder: str) -> List[str]:
    """掃描資料夾中的 Python 模組"""
    files = [
        f.stem for f in folder_path.glob("*.py")
        if not f.name.startswith("_")
    ]
    return [f"{folder}.{file}" for file in files]


def _filter_by_module_name(modules: List[str], only_module: Optional[str]) -> List[str]:
    """根據指定模組名稱過濾"""
    if only_module:
        return [module for module in modules if module.endswith(only_module)]
    return modules


def _filter_by_session(modules: List[str], session: Optional[str]) -> List[str]:
    """根據時段過濾模組"""
    if not session:
        return modules
    
    if session == "morning":
        patterns = [f"f{num:02d}_fetcher" for num in MORNING_MODULES]
    elif session == "night":
        patterns = [f"f{num:02d}_fetcher" for num in NIGHT_MODULES]
    else:
        return modules
    
    return [module for module in modules if any(pattern in module for pattern in patterns)]


def get_module_list(folder: str, only_module: Optional[str] = None, 
                    session: Optional[str] = None) -> List[str]:
    """
    取得模組列表

    Args:
        folder: 模組資料夾 ('dev' 或 'modules')
        only_module: 僅執行特定模組
        session: 時段篩選 ('morning' 或 'night')
            - 'morning': F01-F17 (早盤資料)
            - 'night': F21-F25 (夜盤資料)
            - None: 全部模組

    Returns:
        排序後的模組名稱列表
    """
    try:
        folder_path = PROJECT_ROOT / folder
        if not folder_path.exists():
            return []
        
        modules = _scan_python_modules(folder_path, folder)
        modules = _filter_by_module_name(modules, only_module)
        modules = _filter_by_session(modules, session)
        
        return sorted(modules)
    
    except Exception as error:
        print(f"⚠️  讀取模組列表失敗: {error}")
        return []


def extract_module_id(module_name: str) -> str:
    """
    從模組名稱提取模組代號

    Args:
        module_name: 例如 "f01_fetcher", "f02_fetcher_dev"

    Returns:
        例如 "F01", "F02"
    """
    # 從左到右掃描，找到第一組連續的字母+數字組合（如 "f01"、"F25"）
    for index, char in enumerate(module_name):
        if char.isdigit():
            end_index = index + 1
            while end_index < len(module_name) and module_name[end_index].isdigit():
                end_index += 1
            return module_name[:end_index].upper()
    return module_name.upper()[:3]


def convert_dict_to_text(result_dict: Dict, module_name: str, query_date: str) -> str:
    """
    將舊的 dict 格式轉換為文字格式（向後兼容）

    Args:
        result_dict: 舊格式 dict
        module_name: 模組名稱
        query_date: 查詢日期

    Returns:
        統一格式文字
    """
    module_id = extract_module_id(module_name)
    date_formatted = query_date.replace("-", ".")
    status = result_dict.get("status", "error")
    source = result_dict.get("source", "UNKNOWN")

    if status == "success":
        summary = result_dict.get("summary", "")
        if summary:
            summary = summary.replace("台指期", "")
            text = f"[ {date_formatted}  {module_id}{summary}   source: {source} ]"
        else:
            data = result_dict.get("data", {})
            data_str = ", ".join(f"{key}: {value}" for key, value in data.items())
            text = f"[ {date_formatted}  {module_id} {data_str}   source: {source} ]"
    else:
        error_msg = result_dict.get("error", "未知錯誤")
        text = f"[ {date_formatted}  {module_id} 錯誤: {error_msg}   source: {source} ]"

    return text


def _validate_string_format(result: str, module_id: str, 
                           date_formatted: str) -> Tuple[str, str]:
    """驗證字串格式的返回值"""
    # 舊格式：[ YYYY.MM.DD  FXX...   source: XXX ]
    if result.startswith("[") and result.endswith("]"):
        if date_formatted in result and module_id in result:
            status = "failed" if "錯誤:" in result else "success"
            return result, status
    
    # 新格式：FXX: ... [source] 或帶日期的格式
    elif result.startswith(module_id + ":") or (
        date_formatted in result and 
        (f"{module_id}:" in result or f"{module_id} 錯誤:" in result)
    ):
        status = "failed" if "錯誤:" in result else "success"
        return result, status
    
    error_text = f"[ {date_formatted}  {module_id} 錯誤: 模組回傳格式錯誤   source: UNKNOWN ]"
    return error_text, "invalid"


def _validate_dict_format(result: dict, module_short: str, 
                         query_date: str) -> Tuple[str, str]:
    """驗證 dict 格式的返回值（舊版相容）"""
    converted_text = convert_dict_to_text(result, module_short, query_date)
    status = result.get("status", "error")
    return converted_text, status


def _create_invalid_format_error(module_id: str, 
                                date_formatted: str) -> Tuple[str, str]:
    """建立無效格式錯誤訊息"""
    error_text = f"[ {date_formatted}  {module_id} 錯誤: 返回格式錯誤   source: UNKNOWN ]"
    return error_text, "invalid"


def validate_text_format(result: Any, module_name: str, query_date: str) -> Tuple[str, str]:
    """
    驗證並正規化模組返回結果（支援文字和 dict 雙格式）

    Args:
        result: 模組返回的結果（字串或 dict）
        module_name: 模組名稱
        query_date: 查詢日期

    Returns:
        (正規化後的文字, 狀態碼)
    """
    module_short = module_name.split(".")[-1]
    module_id = extract_module_id(module_short)
    date_formatted = query_date.replace("-", ".")

    if isinstance(result, str):
        return _validate_string_format(result, module_id, date_formatted)
    elif isinstance(result, dict):
        return _validate_dict_format(result, module_short, query_date)
    else:
        return _create_invalid_format_error(module_id, date_formatted)


def save_result(result: str, module_name: str, exec_day: str, dev_mode: bool) -> Path:
    """
    儲存執行結果到檔案（統一文字格式）

    Args:
        result: 執行結果（文字字串）
        module_name: 模組名稱
        exec_day: 執行日期
        dev_mode: 是否為驗收模式

    Returns:
        檔案路徑
    """
    suffix = "_dev" if dev_mode else ""
    module_short = module_name.split(".")[-1]
    current_time = datetime.now().strftime("%H%M")

    data_file = BASE_DIR / f"{exec_day}_{current_time}_{module_short}{suffix}.txt"
    data_file.write_text(result, encoding="utf-8")

    return data_file


def execute_module(module_name: str, query_date: str, logger: logging.Logger) -> Tuple[str, str]:
    """
    執行單一模組

    Args:
        module_name: 模組完整名稱
        query_date: 查詢日期
        logger: 日誌記錄器

    Returns:
        (執行結果文字, 狀態碼)
    """
    module_short = module_name.split(".")[-1]

    try:
        logger.info(f"執行模組: {module_name}")

        if module_name not in MODULE_CACHE:
            MODULE_CACHE[module_name] = importlib.import_module(module_name)

        loaded_module = MODULE_CACHE[module_name]

        if not hasattr(loaded_module, 'fetch'):
            module_id = extract_module_id(module_short)
            date_formatted = query_date.replace("-", ".")
            error_text = f"[ {date_formatted}  {module_id} 錯誤: 模組缺少 fetch() 函式   source: UNKNOWN ]"
            return error_text, "error"

        # 暫時禁用 root logger 的 console 輸出，避免模組內部 log 顯示在螢幕上
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]

        for handler in original_handlers:
            if isinstance(handler, (logging.StreamHandler, SafeConsoleHandler)):
                root_logger.removeHandler(handler)

        try:
            result = loaded_module.fetch(query_date)
        finally:
            for handler in original_handlers:
                if handler not in root_logger.handlers:
                    root_logger.addHandler(handler)

        validated_text, status = validate_text_format(result, module_name, query_date)

        return validated_text, status

    except ImportError as error:
        logger.error(f"模組載入失敗: {error}")
        module_id = extract_module_id(module_short)
        date_formatted = query_date.replace("-", ".")
        error_text = f"[ {date_formatted}  {module_id} 錯誤: 無法載入模組   source: UNKNOWN ]"
        return error_text, "error"

    except Exception as error:
        logger.error(f"執行異常: {str(error)}")
        logger.error(traceback.format_exc())

        module_id = extract_module_id(module_short)
        date_formatted = query_date.replace("-", ".")
        error_text = f"[ {date_formatted}  {module_id} 錯誤: 執行失敗   source: UNKNOWN ]"
        return error_text, "error"


def print_summary(result: str, status: str, logger: logging.Logger):
    """
    顯示執行摘要（文字格式）

    Args:
        result: 執行結果文字
        status: 狀態碼
        logger: 日誌記錄器
    """
    try:
        module_status = ModuleStatus(status)
        icon = module_status.icon
        status_name = module_status.chinese_name
    except ValueError:
        icon = "❓"
        status_name = status

    logger.info(f"  {icon} 狀態: {status_name}")
    logger.info(f"  📄 輸出: {result}")


def _setup_environment():
    """設定執行環境"""
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))


def _create_execution_context(query_date: str, dev_mode: bool,
                              only_module: Optional[str],
                              session: Optional[str]) -> ExecutionContext:
    """建立執行上下文資訊"""
    folder = "dev" if dev_mode else "modules"
    mode = "驗收模式" if dev_mode else "正式模式"
    exec_day = datetime.now().strftime("%Y-%m-%d")
    exec_time = datetime.now().strftime(DATE_FORMAT)
    exec_time_short = datetime.now().strftime("%H%M")
    
    log_suffix = '_dev' if dev_mode else ''
    log_file = BASE_DIR / f"{exec_day}_{exec_time_short}_run{log_suffix}.log"
    
    return ExecutionContext(
        query_date=query_date,
        dev_mode=dev_mode,
        only_module=only_module,
        session=session,
        folder=folder,
        mode=mode,
        exec_day=exec_day,
        exec_time=exec_time,
        exec_time_short=exec_time_short,
        log_file=log_file
    )


def _print_execution_header(logger: logging.Logger, context: ExecutionContext):
    """顯示執行標題資訊"""
    logger.info("")
    logger.info("=" * 70)
    logger.info(f"  📅 查詢日期: {context.query_date}")
    logger.info(f"  ⏰ 執行時間: {context.exec_time}")
    logger.info(f"  🔧 執行模式: {context.mode}")
    
    if context.only_module:
        logger.info(f"  🎯 指定模組: {context.only_module}")
    if context.session:
        session_name = "早盤 (F01-F17)" if context.session == "morning" else "夜盤 (F21-F25)"
        logger.info(f"  🕐 執行時段: {session_name}")
    
    logger.info("=" * 70)
    logger.info("")


def _get_and_validate_modules(logger: logging.Logger, context: ExecutionContext) -> List[str]:
    """取得並驗證模組列表"""
    modules = get_module_list(context.folder, context.only_module, context.session)
    
    if not modules:
        logger.warning(f"⚠️  在 '{context.folder}/' 資料夾中找不到任何模組")
        if context.only_module:
            logger.warning(f"    指定的模組 '{context.only_module}' 不存在")
        return []
    
    logger.info(f"📦 找到 {len(modules)} 個模組")
    logger.info("")
    return modules


def _execute_single_module(logger: logging.Logger, module_name: str,
                           current: int, total: int, context: ExecutionContext, 
                           stats: ExecutionStats):
    """執行單一模組並更新統計"""
    logger.info(f"[{current}/{total}] " + "─" * 50)
    
    module_short = module_name.split(".")[-1].upper()
    logger.info(f"⚙️  執行中: {module_short} ........")
    
    result, status = execute_module(module_name, context.query_date, logger)
    
    # 驗證狀態值
    valid_statuses = {s.value for s in ModuleStatus}
    if status not in valid_statuses:
        logger.warning(f"未知的狀態碼: {status}，設定為 'error'")
        status = ModuleStatus.ERROR.value
    
    stats.increment(status)
    
    try:
        data_file = save_result(result, module_name, context.exec_day, context.dev_mode)
        logger.info(f"💾 檔案: {data_file.name}")
        print_summary(result, status, logger)
    except Exception as error:
        logger.error(f"❌ 儲存失敗: {error}")
        stats.increment("error")
    
    logger.info("")


def _execute_all_modules(logger: logging.Logger, modules: List[str], 
                        context: ExecutionContext) -> ExecutionStats:
    """執行所有模組並收集統計資料"""
    stats = ExecutionStats(total=len(modules))
    
    for idx, module_name in enumerate(modules, 1):
        _execute_single_module(logger, module_name, idx, len(modules), context, stats)
    
    return stats


def _print_execution_summary(logger: logging.Logger, stats: ExecutionStats, 
                            context: ExecutionContext):
    """顯示執行統計報告"""
    logger.info("=" * 70)
    logger.info("  📊 執行統計")
    logger.info("=" * 70)
    logger.info(f"  總數: {stats.total}")
    
    percentages = stats.get_percentages()
    
    logger.info(f"  ✅ 成功: {stats.success} ({percentages['success']:.1f}%)")
    logger.info(f"  ⚠️  失敗: {stats.failed} ({percentages['failed']:.1f}%)")
    logger.info(f"  ❌ 錯誤: {stats.error} ({percentages['error']:.1f}%)")
    logger.info(f"  ⛔ 無效: {stats.invalid} ({percentages['invalid']:.1f}%)")
    logger.info("=" * 70)
    logger.info(f"📝 詳細日誌: {context.log_file}")
    logger.info("=" * 70)
    logger.info("")


def run(query_date: str, dev_mode: bool = False, only_module: Optional[str] = None, 
        session: Optional[str] = None):
    """
    主執行函式

    Args:
        query_date: 查詢日期 (YYYY-MM-DD)
        dev_mode: 是否為驗收模式
        only_module: 僅執行特定模組
        session: 時段篩選 ('morning' 或 'night')
    """
    _setup_environment()
    
    context = _create_execution_context(query_date, dev_mode, only_module, session)
    logger = setup_logger(context.log_file)
    
    _print_execution_header(logger, context)
    
    modules = _get_and_validate_modules(logger, context)
    if not modules:
        return
    
    stats = _execute_all_modules(logger, modules, context)
    
    _print_execution_summary(logger, stats, context)


def _is_valid_trading_data(result: str) -> bool:
    """
    檢查回傳結果是否為有效交易資料

    Args:
        result: 模組回傳的結果字串

    Returns:
        True 表示有有效資料，False 表示無資料（假日或休市）
    """
    if not result:
        return False

    # 包含這些關鍵字代表當日無交易資料
    fail_keywords = [
        "該日無交易資料", "假日", "休市", "錯誤:", "error",
        "未預期的錯誤", "無法取得", "查無資料"
    ]

    for keyword in fail_keywords:
        if keyword in result:
            return False

    return True


def _test_trading_day(date_str: str, session: Optional[str]) -> bool:
    """
    測試指定日期是否為交易日

    Args:
        date_str: 日期字串 (YYYY-MM-DD)
        session: 時段 ('morning' 或 'night')

    Returns:
        True 表示是交易日，False 表示非交易日
    """
    # 根據時段選擇測試模組
    if session == "night":
        test_module = "modules.f21_fetcher"  # 夜盤用 F21 測試
    else:
        test_module = f"modules.{TRADING_DAY_CHECK_MODULE}"  # 早盤用 F01 測試

    try:
        if test_module not in MODULE_CACHE:
            MODULE_CACHE[test_module] = importlib.import_module(test_module)

        loaded_module = MODULE_CACHE[test_module]

        if not hasattr(loaded_module, 'fetch'):
            return False

        # 暫時禁用 logging 輸出
        logging.disable(logging.CRITICAL)
        try:
            result = loaded_module.fetch(date_str)
        finally:
            logging.disable(logging.NOTSET)

        return _is_valid_trading_data(str(result))

    except Exception:
        return False


def find_latest_trading_day(target_date: str, session: Optional[str] = None) -> str:
    """
    從目標日期開始往回找，直到找到有交易資料的那天

    Args:
        target_date: 目標日期 (YYYY-MM-DD)
        session: 時段篩選 ('morning' 或 'night')

    Returns:
        最近的交易日 (YYYY-MM-DD)
    """
    current_date = datetime.strptime(target_date, "%Y-%m-%d")

    print(f"📡 正在尋找最新交易日 (起點: {target_date})...")

    for day_offset in range(MAX_TRADING_DAY_SEARCH + 1):
        date_str = current_date.strftime("%Y-%m-%d")

        if _test_trading_day(date_str, session):
            if day_offset == 0:
                print(f"✅ 確認交易日: {date_str}")
            else:
                print(f"✅ 找到交易日: {date_str} (往回 {day_offset} 天)")
            return date_str

        if day_offset < MAX_TRADING_DAY_SEARCH:
            print(f"  ❌ {date_str} 無資料 (可能是假日或資料未更新)")

        current_date -= timedelta(days=1)

    print(f"⚠️  往回找 {MAX_TRADING_DAY_SEARCH} 天仍無資料，使用原始日期: {target_date}")
    return target_date


def validate_date(date_str: str) -> bool:
    """驗證日期格式"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def print_usage():
    """顯示使用說明"""
    print(__doc__)


def parse_arguments() -> Tuple[str, bool, Optional[str], Optional[str], bool]:
    """
    解析命令列參數

    Returns:
        (查詢日期, 驗收模式, 指定模組, 時段, 自動找交易日)
    """
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print_usage()
        sys.exit(0)

    query_date = args[0] if args and not args[0].startswith("-") else datetime.now().strftime("%Y-%m-%d")

    dev_mode = "dev" in args

    # 是否啟用自動找交易日（預設啟用，加 --no-auto-date 停用）
    auto_find_trading_day = "--no-auto-date" not in args

    only_module = None
    if "--module" in args:
        idx = args.index("--module")
        if idx + 1 < len(args):
            only_module = args[idx + 1]
        else:
            print("❌ 錯誤: --module 參數後需要指定模組名稱\n")
            print_usage()
            sys.exit(1)

    session = None
    if "--session" in args:
        idx = args.index("--session")
        if idx + 1 < len(args):
            session = args[idx + 1]
            if session not in ["morning", "night"]:
                print(f"❌ 錯誤: --session 參數只接受 'morning' 或 'night'，但收到 '{session}'\n")
                print_usage()
                sys.exit(1)
        else:
            print("❌ 錯誤: --session 參數後需要指定時段 (morning 或 night)\n")
            print_usage()
            sys.exit(1)

    if not validate_date(query_date):
        print(f"❌ 錯誤: 日期格式不正確 '{query_date}'")
        print("   請使用 YYYY-MM-DD 格式，例如: 2025-12-01\n")
        print_usage()
        sys.exit(1)

    return query_date, dev_mode, only_module, session, auto_find_trading_day


def main():
    """主程式進入點"""
    if sys.stdout.encoding != 'utf-8' and not hasattr(sys.stdout, '_wrapped_for_utf8'):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stdout._wrapped_for_utf8 = True

    query_date, dev_mode, only_module, session, auto_find_trading_day = parse_arguments()

    # 設定執行環境（需要在找交易日前先設定，以便載入模組）
    _setup_environment()

    # 自動找交易日
    if auto_find_trading_day:
        query_date = find_latest_trading_day(query_date, session)
        print("")  # 空行分隔

    try:
        run(query_date, dev_mode, only_module, session)
    except KeyboardInterrupt:
        print("\n\n⚠️  執行被使用者中斷 (Ctrl+C)")
        sys.exit(130)
    except Exception as error:
        print(f"\n❌ 程式執行失敗: {error}")
        print("\n完整錯誤訊息:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
