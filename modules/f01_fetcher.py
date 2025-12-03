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
===========================================================
"""

import os
import sys
import json
import logging
import importlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# ===== 設定 =====
BASE_DIR = Path(r"C:\Taifex\data")
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ===== 日誌設定 =====
def setup_logger(log_file: Path, dev_mode: bool) -> logging.Logger:
    """設定日誌記錄器"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # 清除現有 handlers
    logger.handlers.clear()
    
    # 檔案 handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # 終端機 handler
    console_handler = logging.StreamHandler(sys.stdout)
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
        only_module: 僅執行特定模組名稱
        
    Returns:
        模組名稱列表
    """
    try:
        folder_path = Path(folder)
        if not folder_path.exists():
            return []
        
        files = [f for f in os.listdir(folder) 
                if f.endswith(".py") and not f.startswith("_")]
        modules = [f"{folder}.{f[:-3]}" for f in files]
        
        if only_module:
            modules = [m for m in modules if m.endswith(only_module)]
        
        return sorted(modules)
    except Exception as e:
        print(f"⚠️  取得模組列表失敗: {e}")
        return []


def save_result(result: Dict, module_name: str, exec_day: str, dev_mode: bool) -> Path:
    """
    儲存執行結果到 JSON 檔案
    
    Args:
        result: 模組執行結果
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


def execute_module(module_name: str, query_date: str, logger: logging.Logger) -> Dict:
    """
    執行單一模組
    
    Args:
        module_name: 模組完整名稱
        query_date: 查詢日期
        logger: 日誌記錄器
        
    Returns:
        執行結果字典
    """
    module_short = module_name.split(".")[-1]
    
    try:
        logger.info(f"[執行] {module_name}")
        
        # 動態載入模組
        mod = importlib.import_module(module_name)
        
        # 檢查是否有 fetch 函式
        if not hasattr(mod, 'fetch'):
            return {
                "date": query_date,
                "module": module_short,
                "status": "error",
                "error": "模組缺少 fetch() 函式",
                "data": {},
                "source": "-"
            }
        
        # 執行 fetch
        result = mod.fetch(query_date)
        
        # 驗證返回格式
        if not isinstance(result, dict):
            return {
                "date": query_date,
                "module": module_short,
                "status": "invalid",
                "error": "fetch() 返回格式不正確 (應為 dict)",
                "data": {},
                "source": "-"
            }
        
        # 驗證必要欄位
        if "狀態" not in result:
            return {
                "date": query_date,
                "module": module_short,
                "status": "invalid",
                "error": "返回結果缺少 '狀態' 欄位",
                "data": {},
                "source": "-"
            }
        
        # 正規化狀態名稱
        status_map = {
            "成功": "success",
            "失敗": "failed",
            "錯誤": "error"
        }
        result["status"] = status_map.get(result.get("狀態", ""), "unknown")
        
        return result
        
    except ImportError as e:
        logger.error(f"[錯誤] 無法載入模組 {module_name}: {e}")
        return {
            "date": query_date,
            "module": module_short,
            "status": "error",
            "error": f"模組載入失敗: {str(e)}",
            "data": {},
            "source": "-"
        }
    
    except Exception as e:
        logger.exception(f"[例外] 執行 {module_name} 時發生錯誤")
        return {
            "date": query_date,
            "module": module_short,
            "status": "error",
            "error": str(e),
            "data": {},
            "source": "-"
        }


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
    
    # 設定參數
    folder = "dev" if dev_mode else "modules"
    mode = "驗收模式" if dev_mode else "正式模式"
    exec_day = datetime.now().strftime("%Y-%m-%d")
    exec_time = datetime.now().strftime(DATE_FORMAT)
    
    # 設定日誌
    log_file = BASE_DIR / f"{exec_day}_run{'_dev' if dev_mode else ''}.log"
    logger = setup_logger(log_file, dev_mode)
    
    # 統計計數器
    stats = {
        "success": 0,
        "failed": 0,
        "error": 0,
        "invalid": 0
    }
    
    # 開始執行
    logger.info("=" * 60)
    logger.info(f"查詢日期: {query_date} | 執行時間: {exec_time} | 模式: {mode}")
    logger.info("=" * 60)
    
    # 取得模組列表
    modules = get_module_list(folder, only_module)
    
    if not modules:
        logger.warning(f"⚠️  在 {folder}/ 資料夾中找不到任何模組")
        return
    
    logger.info(f"找到 {len(modules)} 個模組待執行\n")
    
    # 執行各模組
    for module_name in modules:
        # 執行模組
        result = execute_module(module_name, query_date, logger)
        
        # 更新統計
        status = result.get("status", "unknown")
        stats[status] = stats.get(status, 0) + 1
        
        # 儲存結果
        try:
            data_file = save_result(result, module_name, exec_day, dev_mode)
            logger.info(f"[{status.upper()}] {module_name} → {data_file.name}")
            
            # 顯示摘要（如果有）
            if "摘要" in result and result["摘要"]:
                logger.info(f"  📊 {result['摘要']}")
            elif "錯誤" in result:
                logger.info(f"  ❌ {result['錯誤']}")
            
        except Exception as e:
            logger.error(f"[儲存失敗] {module_name}: {e}")
        
        logger.info("")  # 空行分隔
    
    # 輸出統計
    logger.info("=" * 60)
    logger.info("執行統計")
    logger.info("=" * 60)
    logger.info(f"✅ 成功模組數: {stats['success']}")
    logger.info(f"⚠️  失敗模組數: {stats['failed']}")
    logger.info(f"❌ 錯誤模組數: {stats['error']}")
    logger.info(f"⛔ 無效模組數: {stats['invalid']}")
    logger.info(f"📝 詳細紀錄: {log_file}")
    logger.info("=" * 60)


def validate_date(date_str: str) -> bool:
    """驗證日期格式"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def main():
    """主程式進入點"""
    args = sys.argv[1:]
    
    # 解析參數
    query_date = args[0] if len(args) > 0 else datetime.now().strftime("%Y-%m-%d")
    dev_mode = len(args) > 1 and args[1].lower() == "dev"
    only_module = None
    
    if "--module" in args:
        idx = args.index("--module")
        if idx + 1 < len(args):
            only_module = args[idx + 1]
    
    # 驗證日期
    if not validate_date(query_date):
        print(f"❌ 日期格式錯誤: {query_date}")
        print("請使用 YYYY-MM-DD 格式，例如: 2025-12-01")
        sys.exit(1)
    
    # 執行
    try:
        run(query_date, dev_mode, only_module)
    except KeyboardInterrupt:
        print("\n⚠️  執行被使用者中斷")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()