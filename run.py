"""
===========================================================
 run.py  —  模組統一執行程式 (集中輸出到 data/)
===========================================================

【用途】
- 執行指定查詢日期的模組，並將結果寫入 C:\Taifex\data\
- 不管成功或失敗，皆會寫入一筆 JSON 檔案到 data/
- log 檔案也寫在 data/，與 JSON 同目錄
- 終端機即時顯示執行進度

【用法】
  python run.py [查詢日期] [模式] [--module 模組名稱]

【範例】
  python run.py 2025-12-01 dev
  python run.py 2025-12-01
  python run.py 2025-12-01 dev --module f01_fetcher_dev
  python run.py --help
===========================================================
"""

import os
import sys
import json
import logging
import importlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import traceback

# ===== 設定 =====
BASE_DIR = Path(r"C:\Taifex\data")
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 狀態映射表
STATUS_MAP = {
    "成功": "success",
    "失敗": "failed",
    "錯誤": "error"
}


def setup_logger(log_file: Path) -> logging.Logger:
    """設定日誌記錄器"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    # 檔案 handler - 記錄詳細資訊
    file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # 終端機 handler - 簡潔輸出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_module_list(folder: str, only_module: Optional[str] = None) -> List[str]:
    """取得模組列表"""
    try:
        folder_path = Path(folder)
        if not folder_path.exists():
            return []
        
        files = [
            f for f in os.listdir(folder) 
            if f.endswith(".py") and not f.startswith("_")
        ]
        
        modules = [f"{folder}.{f[:-3]}" for f in files]
        
        if only_module:
            modules = [m for m in modules if m.endswith(only_module)]
        
        return sorted(modules)
        
    except Exception as e:
        print(f"⚠️  取得模組列表失敗: {e}")
        return []


def validate_result_format(result: Dict, module_name: str, query_date: str) -> Tuple[Dict, str]:
    """驗證並正規化模組返回結果"""
    module_short = module_name.split(".")[-1]
    
    if not isinstance(result, dict):
        return {
            "模組": module_short,
            "日期": query_date,
            "狀態": "invalid",
            "錯誤": "返回格式錯誤：應為 dict",
            "資料": {},
            "來源": "-"
        }, "invalid"
    
    if "狀態" not in result:
        return {
            "模組": module_short,
            "日期": query_date,
            "狀態": "invalid",
            "錯誤": "返回結果缺少 '狀態' 欄位",
            "資料": {},
            "來源": "-"
        }, "invalid"
    
    status_zh = result.get("狀態", "")
    status_en = STATUS_MAP.get(status_zh, "unknown")
    
    if "模組" not in result:
        result["模組"] = module_short
    if "日期" not in result:
        result["日期"] = query_date
    
    return result, status_en


def save_result(result: Dict, module_name: str, exec_day: str, dev_mode: bool) -> Path:
    """儲存執行結果到 JSON 檔案"""
    suffix = "_dev" if dev_mode else ""
    module_short = module_name.split(".")[-1]
    data_file = BASE_DIR / f"{exec_day}_{module_short}{suffix}.json"
    
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return data_file


def execute_module(module_name: str, query_date: str, logger: logging.Logger) -> Tuple[Dict, str]:
    """執行單一模組"""
    module_short = module_name.split(".")[-1]
    
    try:
        logger.info(f"[執行] {module_name}")
        
        mod = importlib.import_module(module_name)
        
        if not hasattr(mod, 'fetch'):
            error_result = {
                "模組": module_short,
                "日期": query_date,
                "狀態": "錯誤",
                "錯誤": "模組缺少 fetch() 函式",
                "資料": {},
                "來源": "-"
            }
            return error_result, "error"
        
        result = mod.fetch(query_date)
        validated_result, status = validate_result_format(result, module_name, query_date)
        
        return validated_result, status
        
    except ImportError as e:
        logger.error(f"無法載入模組: {e}")
        error_result = {
            "模組": module_short,
            "日期": query_date,
            "狀態": "錯誤",
            "錯誤": f"模組載入失敗: {str(e)}",
            "資料": {},
            "來源": "-"
        }
        return error_result, "error"
    
    except Exception as e:
        logger.error(f"執行模組時發生例外: {str(e)}")
        logger.debug(traceback.format_exc())
        
        error_result = {
            "模組": module_short,
            "日期": query_date,
            "狀態": "錯誤",
            "錯誤": f"執行失敗: {str(e)}",
            "資料": {},
            "來源": "-"
        }
        return error_result, "error"


def print_summary(result: Dict, status: str, logger: logging.Logger):
    """印出執行摘要"""
    status_icons = {
        "success": "✅",
        "failed": "⚠️ ",
        "error": "❌",
        "invalid": "⛔"
    }
    
    icon = status_icons.get(status, "❓")
    
    if "摘要" in result and result["摘要"]:
        logger.info(f"  {icon} {result['摘要']}")
    elif "錯誤" in result:
        logger.info(f"  {icon} {result['錯誤']}")
    elif status == "success":
        logger.info(f"  {icon} 執行成功")


def run(query_date: str, dev_mode: bool = False, only_module: Optional[str] = None):
    """主執行函式"""
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    folder = "dev" if dev_mode else "modules"
    mode = "驗收模式" if dev_mode else "正式模式"
    exec_day = datetime.now().strftime("%Y-%m-%d")
    exec_time = datetime.now().strftime(DATE_FORMAT)
    
    log_file = BASE_DIR / f"{exec_day}_run{'_dev' if dev_mode else ''}.log"
    logger = setup_logger(log_file)
    
    stats = {
        "success": 0,
        "failed": 0,
        "error": 0,
        "invalid": 0,
        "total": 0
    }
    
    logger.info("")
    logger.info("=" * 70)
    logger.info(f"  查詢日期: {query_date}")
    logger.info(f"  執行時間: {exec_time}")
    logger.info(f"  執行模式: {mode}")
    if only_module:
        logger.info(f"  指定模組: {only_module}")
    logger.info("=" * 70)
    logger.info("")
    
    modules = get_module_list(folder, only_module)
    
    if not modules:
        logger.warning(f"⚠️  在 '{folder}/' 資料夾中找不到任何模組")
        if only_module:
            logger.warning(f"    指定模組 '{only_module}' 不存在")
        return
    
    stats["total"] = len(modules)
    logger.info(f"📦 找到 {len(modules)} 個模組待執行")
    logger.info("")
    
    for idx, module_name in enumerate(modules, 1):
        logger.info(f"[{idx}/{len(modules)}] " + "─" * 50)
        
        result, status = execute_module(module_name, query_date, logger)
        stats[status] = stats.get(status, 0) + 1
        
        try:
            data_file = save_result(result, module_name, exec_day, dev_mode)
            logger.info(f"[儲存] {data_file.name}")
            print_summary(result, status, logger)
            
        except Exception as e:
            logger.error(f"❌ 儲存結果失敗: {e}")
            stats["error"] += 1
        
        logger.info("")
    
    logger.info("=" * 70)
    logger.info("  📊 執行統計報告")
    logger.info("=" * 70)
    logger.info(f"  總執行數: {stats['total']}")
    logger.info(f"  ✅ 成功: {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
    logger.info(f"  ⚠️  失敗: {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
    logger.info(f"  ❌ 錯誤: {stats['error']} ({stats['error']/stats['total']*100:.1f}%)")
    logger.info(f"  ⛔ 無效: {stats['invalid']} ({stats['invalid']/stats['total']*100:.1f}%)")
    logger.info("=" * 70)
    logger.info(f"📝 詳細紀錄: {log_file}")
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
    """印出使用說明"""
    print(__doc__)
    print("\n使用範例:")
    print("  python run.py                           # 執行今天日期")
    print("  python run.py 2025-12-01                # 執行指定日期")
    print("  python run.py 2025-12-01 dev            # 驗收模式")
    print("  python run.py 2025-12-01 dev --module f01_fetcher_dev")
    print()


def main():
    """主程式進入點"""
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        print_usage()
        sys.exit(0)
    
    query_date = args[0] if len(args) > 0 else datetime.now().strftime("%Y-%m-%d")
    dev_mode = len(args) > 1 and args[1].lower() == "dev"
    only_module = None
    
    if "--module" in args:
        idx = args.index("--module")
        if idx + 1 < len(args):
            only_module = args[idx + 1]
        else:
            print("❌ --module 參數後需要指定模組名稱")
            sys.exit(1)
    
    if not validate_date(query_date):
        print(f"❌ 日期格式錯誤: {query_date}")
        print("   請使用 YYYY-MM-DD 格式，例如: 2025-12-01")
        print()
        print_usage()
        sys.exit(1)
    
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