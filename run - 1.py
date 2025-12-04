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

import os
import sys
import json
import logging
import importlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import traceback
from functools import lru_cache

# ===== 設定 =====
# 自動取得專案根目錄
PROJECT_ROOT = Path(__file__).parent.absolute()
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


def setup_logger(log_file: Path) -> logging.Logger:
    """設定日誌記錄器"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    # 檔案 handler - 詳細記錄（UTF-8 編碼）
    file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # 終端機 handler - 簡潔輸出（使用 UTF-8 編碼以支援中文和表情符號）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    
    # 設定終端機編碼為 UTF-8（Windows 相容）
    if sys.stdout.encoding != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
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
        
        files = [
            f for f in os.listdir(folder_path) 
            if f.endswith(".py") and not f.startswith("_")
        ]
        
        modules = [f"{folder}.{f[:-3]}" for f in files]
        
        if only_module:
            modules = [m for m in modules if m.endswith(only_module)]
        
        return sorted(modules)
        
    except Exception as e:
        print(f"⚠️  讀取模組列表失敗: {e}")
        return []


def validate_result_format(result: Dict, module_name: str, query_date: str) -> Tuple[Dict, str]:
    """
    驗證並正規化模組返回結果
    
    Args:
        result: 模組返回的結果
        module_name: 模組名稱
        query_date: 查詢日期
        
    Returns:
        (正規化後的結果, 狀態碼)
    """
    module_short = module_name.split(".")[-1]
    
    # 檢查是否為字典
    if not isinstance(result, dict):
        return {
            "module": module_short,
            "date": query_date,
            "status": "invalid",
            "error": "返回格式錯誤：應為 dict 類型"
        }, "invalid"
    
    # 檢查必要欄位
    if "status" not in result:
        return {
            "module": module_short,
            "date": query_date,
            "status": "invalid",
            "error": "返回結果缺少 'status' 欄位"
        }, "invalid"
    
    # 取得狀態
    status = result.get("status", "unknown")
    
    # 補充缺少的欄位
    if "module" not in result:
        result["module"] = module_short
    if "date" not in result:
        result["date"] = query_date
    
    return result, status


def save_result(result: Dict, module_name: str, exec_day: str, dev_mode: bool) -> Path:
    """
    儲存執行結果到 JSON 檔案
    
    Args:
        result: 執行結果
        module_name: 模組名稱
        exec_day: 執行日期
        dev_mode: 是否為驗收模式
        
    Returns:
        JSON 檔案路徑
    """
    suffix = "_dev" if dev_mode else ""
    module_short = module_name.split(".")[-1]
    data_file = BASE_DIR / f"{exec_day}_{module_short}{suffix}.json"
    
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return data_file


def execute_module(module_name: str, query_date: str, logger: logging.Logger) -> Tuple[Dict, str]:
    """
    執行單一模組
    
    Args:
        module_name: 模組完整名稱
        query_date: 查詢日期
        logger: 日誌記錄器
        
    Returns:
        (執行結果, 狀態碼)
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
            error_result = {
                "module": module_short,
                "date": query_date,
                "status": "error",
                "error": "模組缺少 fetch() 函式"
            }
            return error_result, "error"
        
        # 執行 fetch 函式
        result = mod.fetch(query_date)
        
        # 驗證並正規化結果
        validated_result, status = validate_result_format(result, module_name, query_date)
        
        return validated_result, status
        
    except ImportError as e:
        logger.error(f"模組載入失敗: {e}")
        error_result = {
            "module": module_short,
            "date": query_date,
            "status": "error",
            "error": f"無法載入模組: {str(e)}"
        }
        return error_result, "error"
    
    except Exception as e:
        logger.error(f"執行異常: {str(e)}")
        logger.debug(traceback.format_exc())
        
        error_result = {
            "module": module_short,
            "date": query_date,
            "status": "error",
            "error": f"執行失敗: {str(e)}"
        }
        return error_result, "error"


def print_summary(result: Dict, status: str, logger: logging.Logger):
    """
    顯示執行摘要（中文）
    
    Args:
        result: 執行結果
        status: 狀態碼
        logger: 日誌記錄器
    """
    icon = STATUS_ICONS.get(status, "❓")
    
    # 狀態中文對應
    status_zh = {
        "success": "成功",
        "failed": "失敗",
        "error": "錯誤",
        "invalid": "無效"
    }
    
    logger.info(f"  {icon} 狀態: {status_zh.get(status, status)}")
    
    # 顯示摘要或錯誤訊息
    if "summary" in result and result["summary"]:
        logger.info(f"  📊 {result['summary']}")
    elif "error" in result:
        logger.info(f"  💬 {result['error']}")
    
    # 顯示資料內容
    if status == "success" and "data" in result:
        data = result["data"]
        if isinstance(data, dict):
            for key, value in data.items():
                # 將英文 key 轉換為中文顯示
                key_zh = {
                    "long_position": "多方口數",
                    "short_position": "空方口數",
                    "net_position": "淨額"
                }.get(key, key)
                
                if isinstance(value, (int, float)):
                    logger.info(f"     • {key_zh}: {value:,}")
                else:
                    logger.info(f"     • {key_zh}: {value}")


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
    
    # 設定日誌
    log_file = BASE_DIR / f"{exec_day}_run{'_dev' if dev_mode else ''}.log"
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


def main():
    """主程式進入點"""
    # 設定 UTF-8 編碼以支援中文和表情符號
    if sys.stdout.encoding != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    args = sys.argv[1:]
    
    # 顯示說明
    if "--help" in args or "-h" in args:
        print_usage()
        sys.exit(0)
    
    # 解析參數
    query_date = args[0] if len(args) > 0 else datetime.now().strftime("%Y-%m-%d")
    dev_mode = len(args) > 1 and args[1].lower() == "dev"
    only_module = None
    
    if "--module" in args:
        idx = args.index("--module")
        if idx + 1 < len(args):
            only_module = args[idx + 1]
        else:
            print("❌ 錯誤: --module 參數後需要指定模組名稱")
            print()
            print_usage()
            sys.exit(1)
    
    # 驗證日期
    if not validate_date(query_date):
        print(f"❌ 錯誤: 日期格式不正確 '{query_date}'")
        print("   請使用 YYYY-MM-DD 格式，例如: 2025-12-01")
        print()
        print_usage()
        sys.exit(1)
    
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