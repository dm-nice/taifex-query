"""
===========================================================
 run.py  —  模組統一執行程式 (集中輸出版本)
===========================================================
"""

import sys
import json
import importlib
import logging
from datetime import datetime
from pathlib import Path
from typing import List

from config import settings
from utils.debug_pipeline import format_traceback

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

FIELDS = ["日期", "外資多方口數", "外資空方口數", "外資多空淨額", "source", "status", "module"]

def to_int_safe(val):
    try:
        if val is None:
            return "-"
        s = str(val).replace(",", "").strip()
        return int(s)
    except:
        return "-"

def build_flat_record(date, result, module_name, status_override=None):
    d = result.get("data", {}) if isinstance(result, dict) else {}

    def safe_get(key):
        val = d.get(key)
        if val is None or str(val).strip() == "":
            return "-"
        return to_int_safe(val)

    long_val = safe_get("外資多方口數")
    short_val = safe_get("外資空方口數")
    net_val = safe_get("外資多空淨額")

    if long_val == "-" and short_val == "-":
        net_val = "-"

    return {
        "日期": date,
        "外資多方口數": long_val,
        "外資空方口數": short_val,
        "外資多空淨額": net_val,
        "source": result.get("source", "-") if isinstance(result, dict) else "-",
        "status": status_override or (result.get("status", "invalid") if isinstance(result, dict) else "invalid"),
        "module": result.get("module", module_name.split(".")[-1]) if isinstance(result, dict) else module_name.split(".")[-1]
    }

def format_row(record):
    widths = [12, 12, 12, 12, 10, 10, 8]
    row = []
    for field, width in zip(FIELDS, widths):
        val = str(record.get(field, "-"))
        row.append(val.ljust(width))
    return " ".join(row)

def get_module_list(folder_name: str, only_module: str = None) -> List[str]:
    folder_path = settings.BASE_DIR / folder_name
    if not folder_path.exists():
        return []
        
    files = [f.name for f in folder_path.iterdir() if f.suffix == ".py" and not f.name.startswith("_") and f.name != "base.py"]
    modules = [f"{folder_name}.{f[:-3]}" for f in files]
    if only_module:
        modules = [m for m in modules if m.endswith(only_module)]
    return modules

def run(query_date: str, dev_mode: bool, only_module: str = None):
    folder = "dev" if dev_mode else "modules"
    mode = "驗收模式" if dev_mode else "正式模式"
    exec_day = datetime.now().strftime("%Y-%m-%d")
    
    log_filename = f"{exec_day}_run{'_dev' if dev_mode else ''}.log"
    log_file = settings.LOG_DIR / log_filename
    
    # Add file handler dynamically
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(file_handler)

    success_count = fail_count = error_count = invalid_count = 0

    logger.info(f"=== 查詢日期: {query_date} ｜ 模式: {mode} ===")
    file_handler.stream.write(format_row({f: f for f in FIELDS}) + "\n")

    for module_name in get_module_list(folder, only_module):
        try:
            logger.info(f"[執行] {module_name}")
            mod = importlib.import_module(module_name)
            
            # Duck typing check or BaseFetcher check could go here
            if not hasattr(mod, 'fetch'):
                 logger.warning(f"Module {module_name} has no fetch function")
                 continue

            result = mod.fetch(query_date)

            if not isinstance(result, dict) or "status" not in result:
                record = build_flat_record(query_date, result, module_name, status_override="invalid")
                invalid_count += 1
            else:
                record = build_flat_record(query_date, result, module_name)
                if result["status"] == "success":
                    success_count += 1
                else:
                    fail_count += 1

            suffix = "_dev" if dev_mode else ""
            data_filename = f"{exec_day}_{record['module']}{suffix}.json"
            data_file = settings.DATA_DIR / data_filename
            
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=2)

            file_handler.stream.write(format_row(record) + "\n")
            logger.info(f"[{record['status'].upper()}] {module_name} → {data_file}")

        except Exception as e:
            record = build_flat_record(query_date, {}, module_name, status_override="error")
            suffix = "_dev" if dev_mode else ""
            data_filename = f"{exec_day}_{record['module']}{suffix}.json"
            data_file = settings.DATA_DIR / data_filename
            
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=2)

            file_handler.stream.write(format_row(record) + "\n")
            logger.error(f"[ERROR] {module_name} : {e}")
            logger.debug(format_traceback(e))
            error_count += 1

    logger.info("=== 驗收統計 ===")
    logger.info(f"成功: {success_count}, 失敗: {fail_count}, 錯誤: {error_count}, 無效: {invalid_count}")
    logger.info(f"詳細紀錄: {log_file}")
    
    logger.removeHandler(file_handler)

if __name__ == "__main__":
    args = sys.argv[1:]
    query_date = args[0] if len(args) > 0 else datetime.now().strftime("%Y-%m-%d")
    dev_mode = len(args) > 1 and args[1].lower() == "dev"
    only_module = None
    if "--module" in args:
        idx = args.index("--module")
        if idx + 1 < len(args):
            only_module = args[idx + 1]

    run(query_date, dev_mode, only_module)

