"""
===========================================================
 run.py  —  模組統一執行程式
===========================================================

【功能】
- 自動執行指定日期的所有模組
- 將結果統一輸出到 C:\Taifex\data\
- 支援正式模式和驗收模式
- 提供詳細的執行日誌

【使用方式】
  python run.py [日期] [模式] [--module 模組名稱]

【範例】
  python run.py                              # 執行今天
  python run.py 2025-12-01                   # 執行指定日期
  python run.py 2025-12-01 dev               # 驗收模式
  python run.py 2025-12-01 dev --module f01_fetcher_dev
  python run.py --help                       # 顯示說明
===========================================================
"""

import sys
import logging
import importlib
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

# ===== 設定 =====
# 自動取得專案根目錄
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

# 模組快取（減少重複載入）
MODULE_CACHE = {}

# 狀態對應的圖示
STATUS_ICONS = {
    "success": "✅",
    "failed": "⚠️ ",
    "error": "❌",
    "invalid": "⛔"
}


class SafeConsoleHandler(logging.Handler):
    """安全的 Console Handler - 避免因 stdout 被關閉而出錯"""

    def emit(self, record):
        try:
            msg = self.format(record)

            # 跳過包含時間戳記的訊息（格式：YYYY-MM-DD HH:MM:SS [INFO]）
            if '[INFO]' in msg or '[ERROR]' in msg or '[WARNING]' in msg or '[DEBUG]' in msg:
                return

            # 只在螢幕顯示重要的摘要資訊
            # 允許顯示的模式：開頭標題區塊 + 最後統計區塊
            show_patterns = [
                '═════',              # 標題分隔線
                '📅 查詢日期:',       # 查詢日期
                '⏰ 執行時間:',       # 執行時間
                '🔧 執行模式:',       # 執行模式
                '🎯 指定模組:',       # 指定模組
                # '📦 找到',          # 找到模組數量（移除，不顯示）
                '📊 執行統計',        # 執行統計標題
                '總數:',              # 統計資訊
                '✅ 成功:',           # 成功數量
                '⚠️  失敗:',         # 失敗數量（注意兩個空格）
                '❌ 錯誤:',           # 錯誤數量
                '⛔ 無效:',           # 無效數量
                '📝 詳細日誌:',       # 日誌位置
                '⚠️  在'              # 警告訊息（找不到模組）
            ]

            # 檢查是否需要顯示
            if any(pattern in msg for pattern in show_patterns):
                print(msg)
            # 只在標題區塊顯示空行
            elif msg.strip() == '' and '═' in getattr(self, '_last_msg', ''):
                print(msg)

            # 記錄最後一條訊息（用於判斷空行）
            self._last_msg = msg

        except Exception:
            # 靜默處理錯誤，避免中斷執行
            pass


def setup_logger(log_file: Path) -> logging.Logger:
    """設定日誌記錄器"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # 禁用向上傳播，避免日誌被 root logger 的 handler 重複輸出
    logger.propagate = False

    # 檔案 handler - 詳細記錄（UTF-8 編碼）
    file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(file_formatter)

    # 終端機 handler - 使用安全的 Console Handler
    console_handler = SafeConsoleHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_module_list(folder: str, only_module: Optional[str] = None) -> List[str]:
    """
    取得模組列表

    Args:
        folder: 模組資料夾 ('dev' 或 'modules')
        only_module: 僅執行特定模組

    Returns:
        排序後的模組名稱列表
    """
    try:
        folder_path = PROJECT_ROOT / folder
        if not folder_path.exists():
            return []

        # 取得所有 Python 模組（排除 __init__.py 等）
        files = [
            f.stem for f in folder_path.glob("*.py")
            if not f.name.startswith("_")
        ]

        modules = [f"{folder}.{f}" for f in files]

        if only_module:
            modules = [m for m in modules if m.endswith(only_module)]

        return sorted(modules)

    except Exception as e:
        print(f"⚠️  讀取模組列表失敗: {e}")
        return []


def extract_module_id(module_name: str) -> str:
    """
    從模組名稱提取模組代號

    Args:
        module_name: 例如 "f01_fetcher", "f02_fetcher_dev"

    Returns:
        例如 "F01", "F02"
    """
    # 提取模組代號（字母+數字組合）
    for i, char in enumerate(module_name):
        if char.isdigit():
            # 找到數字後繼續找到非數字為止
            j = i + 1
            while j < len(module_name) and module_name[j].isdigit():
                j += 1
            return module_name[:j].upper()
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
            data_str = ", ".join(f"{k}: {v}" for k, v in data.items())
            text = f"[ {date_formatted}  {module_id} {data_str}   source: {source} ]"
    else:
        error_msg = result_dict.get("error", "未知錯誤")
        text = f"[ {date_formatted}  {module_id} 錯誤: {error_msg}   source: {source} ]"

    return text


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

    # 1. 字串格式（新模組）
    if isinstance(result, str):
        # 接受兩種格式：
        # 舊格式：[ YYYY.MM.DD  FXX...   source: XXX ]
        # 新格式：FXX: ... [source]
        if result.startswith("[") and result.endswith("]"):
            # 舊格式驗證
            if date_formatted in result and module_id in result:
                status = "failed" if "錯誤:" in result else "success"
                return result, status
        elif result.startswith(module_id + ":") or (
            date_formatted in result and (f"{module_id}:" in result or f"{module_id} 錯誤:" in result)
        ):
            # 新格式驗證（包含帶日期的格式）
            status = "failed" if "錯誤:" in result else "success"
            return result, status

        # 格式不正確 - 需要傳入 logger 或移除 logger 調用
        # 暫時移除 logger 調用以避免錯誤
        text = f"[ {date_formatted}  {module_id} 錯誤: 模組回傳格式錯誤   source: UNKNOWN ]"
        return text, "invalid"

    # 2. dict 格式（舊模組，向後兼容）
    elif isinstance(result, dict):
        # 移除 logger 調用以避免錯誤
        return convert_dict_to_text(result, module_short, query_date), \
               result.get("status", "error")

    # 3. 無效類型
    else:
        # 移除 logger 調用以避免錯誤
        text = f"[ {date_formatted}  {module_id} 錯誤: 返回格式錯誤   source: UNKNOWN ]"
        return text, "invalid"


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

    # 檔案名稱格式: YYYY-MM-DD_HHMM_模組名稱.txt
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

        # 從快取或動態載入模組
        if module_name not in MODULE_CACHE:
            MODULE_CACHE[module_name] = importlib.import_module(module_name)

        mod = MODULE_CACHE[module_name]

        # 檢查是否有 fetch 函式
        if not hasattr(mod, 'fetch'):
            module_id = extract_module_id(module_short)
            date_formatted = query_date.replace("-", ".")
            error_text = f"[ {date_formatted}  {module_id} 錯誤: 模組缺少 fetch() 函式   source: UNKNOWN ]"
            return error_text, "error"

        # 暫時禁用 root logger 的 console 輸出，避免模組內部 log 顯示在螢幕上
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]

        # 移除所有 console handlers
        for handler in original_handlers:
            if isinstance(handler, (logging.StreamHandler, SafeConsoleHandler)):
                root_logger.removeHandler(handler)

        try:
            # 執行 fetch 函式
            result = mod.fetch(query_date)
        finally:
            # 恢復 root logger 的 handlers
            for handler in original_handlers:
                if handler not in root_logger.handlers:
                    root_logger.addHandler(handler)

        # 驗證並正規化
        validated_text, status = validate_text_format(result, module_name, query_date)

        return validated_text, status

    except ImportError as e:
        logger.error(f"模組載入失敗: {e}")
        module_id = extract_module_id(module_short)
        date_formatted = query_date.replace("-", ".")
        error_text = f"[ {date_formatted}  {module_id} 錯誤: 無法載入模組   source: UNKNOWN ]"
        return error_text, "error"

    except Exception as e:
        logger.error(f"執行異常: {str(e)}")
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
    icon = STATUS_ICONS.get(status, "❓")

    status_zh = {
        "success": "成功",
        "failed": "失敗",
        "error": "錯誤",
        "invalid": "無效"
    }

    logger.info(f"  {icon} 狀態: {status_zh.get(status, status)}")
    logger.info(f"  📄 輸出: {result}")


def run(query_date: str, dev_mode: bool = False, only_module: Optional[str] = None):
    """
    主執行函式
    
    Args:
        query_date: 查詢日期 (YYYY-MM-DD)
        dev_mode: 是否為驗收模式
        only_module: 僅執行特定模組
    """
    # 建立輸出目錄
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 將專案根目錄加入 sys.path（以便可以載入模組）
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    
    # 設定參數
    folder = "dev" if dev_mode else "modules"
    mode = "驗收模式" if dev_mode else "正式模式"
    exec_day = datetime.now().strftime("%Y-%m-%d")
    exec_time = datetime.now().strftime(DATE_FORMAT)
    exec_time_short = datetime.now().strftime("%H%M")  # 用於檔案名稱
    
    # 設定日誌 - 檔案名稱包含時間戳記
    log_file = BASE_DIR / f"{exec_day}_{exec_time_short}_run{'_dev' if dev_mode else ''}.log"
    logger = setup_logger(log_file)
    
    # 統計計數器
    stats = {
        "success": 0,
        "failed": 0,
        "error": 0,
        "invalid": 0,
        "total": 0
    }
    
    # 顯示標題
    logger.info("")
    logger.info("=" * 70)
    logger.info(f"  📅 查詢日期: {query_date}")
    logger.info(f"  ⏰ 執行時間: {exec_time}")
    logger.info(f"  🔧 執行模式: {mode}")
    if only_module:
        logger.info(f"  🎯 指定模組: {only_module}")
    logger.info("=" * 70)
    logger.info("")
    
    # 取得模組列表
    modules = get_module_list(folder, only_module)
    
    if not modules:
        logger.warning(f"⚠️  在 '{folder}/' 資料夾中找不到任何模組")
        if only_module:
            logger.warning(f"    指定的模組 '{only_module}' 不存在")
        return
    
    stats["total"] = len(modules)
    logger.info(f"📦 找到 {len(modules)} 個模組")
    logger.info("")
    
    # 執行各模組
    for idx, module_name in enumerate(modules, 1):
        logger.info(f"[{idx}/{len(modules)}] " + "─" * 50)
        
        # 執行模組
        result, status = execute_module(module_name, query_date, logger)
        stats[status] = stats.get(status, 0) + 1
        
        # 儲存結果
        try:
            data_file = save_result(result, module_name, exec_day, dev_mode)
            logger.info(f"💾 檔案: {data_file.name}")
            
            # 顯示摘要
            print_summary(result, status, logger)
            
        except Exception as e:
            logger.error(f"❌ 儲存失敗: {e}")
            stats["error"] += 1
        
        logger.info("")
    
    # 顯示統計報告
    logger.info("=" * 70)
    logger.info("  📊 執行統計")
    logger.info("=" * 70)
    logger.info(f"  總數: {stats['total']}")
    logger.info(f"  ✅ 成功: {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
    logger.info(f"  ⚠️  失敗: {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
    logger.info(f"  ❌ 錯誤: {stats['error']} ({stats['error']/stats['total']*100:.1f}%)")
    logger.info(f"  ⛔ 無效: {stats['invalid']} ({stats['invalid']/stats['total']*100:.1f}%)")
    logger.info("=" * 70)
    logger.info(f"📝 詳細日誌: {log_file}")
    logger.info("=" * 70)
    logger.info("")


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


def parse_arguments() -> Tuple[str, bool, Optional[str]]:
    """
    解析命令列參數

    Returns:
        (查詢日期, 驗收模式, 指定模組)
    """
    args = sys.argv[1:]

    # 顯示說明
    if "--help" in args or "-h" in args:
        print_usage()
        sys.exit(0)

    # 解析日期
    query_date = args[0] if args and not args[0].startswith("-") else datetime.now().strftime("%Y-%m-%d")

    # 解析模式
    dev_mode = "dev" in args

    # 解析指定模組
    only_module = None
    if "--module" in args:
        idx = args.index("--module")
        if idx + 1 < len(args):
            only_module = args[idx + 1]
        else:
            print("❌ 錯誤: --module 參數後需要指定模組名稱\n")
            print_usage()
            sys.exit(1)

    # 驗證日期格式
    if not validate_date(query_date):
        print(f"❌ 錯誤: 日期格式不正確 '{query_date}'")
        print("   請使用 YYYY-MM-DD 格式，例如: 2025-12-01\n")
        print_usage()
        sys.exit(1)

    return query_date, dev_mode, only_module


def main():
    """主程式進入點"""
    # 設定 UTF-8 編碼以支援中文和表情符號
    if sys.stdout.encoding != 'utf-8' and not hasattr(sys.stdout, '_wrapped_for_utf8'):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stdout._wrapped_for_utf8 = True

    # 解析參數
    query_date, dev_mode, only_module = parse_arguments()

    # 執行
    try:
        run(query_date, dev_mode, only_module)
    except KeyboardInterrupt:
        print("\n\n⚠️  執行被使用者中斷 (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 程式執行失敗: {e}")
        print("\n完整錯誤訊息:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()