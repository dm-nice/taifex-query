"""
===========================================================
 run.py  —  模組統一執行程式 (集中輸出到 data/)
===========================================================

【用途】
- 執行指定查詢日期的模組，並將結果寫入 C:\Taifex\data\
- 不管成功或失敗，皆會寫入一筆 JSON 檔案到 data/
- log 檔案也寫在 data/，與 JSON 同目錄
- 終端機即時顯示執行進度 (print)

【用法】
  python run.py [查詢日期] [模式] [--module 模組名稱]

【範例】
  python run.py 2025-12-01 dev
  python run.py 2025-12-01
  python run.py 2025-12-01 dev --module f01_fetcher_dev_example
===========================================================
"""

import os
import sys
import json
import importlib
from datetime import datetime
from utils.debug_pipeline import format_traceback

BASE_DIR = r"C:\Taifex\data"   # ✅ 集中輸出目錄

def get_module_list(folder: str, only_module: str = None):
    files = [f for f in os.listdir(folder) if f.endswith(".py") and not f.startswith("_")]
    modules = [f"{folder}.{f[:-3]}" for f in files]
    if only_module:
        modules = [m for m in modules if m.endswith(only_module)]
    return modules

def run(query_date: str, dev_mode: bool, only_module: str = None):
    os.makedirs(BASE_DIR, exist_ok=True)

    folder = "dev" if dev_mode else "modules"
    mode = "驗收模式" if dev_mode else "正式模式"
    exec_day = datetime.now().strftime("%Y-%m-%d")

    # ✅ log 檔案集中在 data 目錄
    log_file = os.path.join(BASE_DIR, f"{exec_day}_run{'_dev' if dev_mode else ''}.log")
    exec_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    success_count = fail_count = error_count = invalid_count = 0

    print(f"=== 查詢日期: {query_date} ｜ 執行日期: {exec_time} ｜ 模式: {mode} ===")

    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"\n=== 查詢日期: {query_date} ｜ 執行日期: {exec_time} ｜ 模式: {mode} ===\n")

        for module_name in get_module_list(folder, only_module):
            try:
                print(f"[執行] {module_name}")
                mod = importlib.import_module(module_name)
                result = mod.fetch(query_date)

                if not isinstance(result, dict) or "status" not in result:
                    record = {
                        "date": query_date,
                        "module": module_name.split(".")[-1],
                        "status": "invalid",
                        "data": {},
                        "source": "-"
                    }
                    invalid_count += 1
                else:
                    record = result
                    if result["status"] == "success":
                        success_count += 1
                    else:
                        fail_count += 1

                suffix = "_dev" if dev_mode else ""
                data_file = os.path.join(BASE_DIR, f"{exec_day}_{record['module']}{suffix}.json")
                with open(data_file, "w", encoding="utf-8") as f:
                    json.dump(record, f, ensure_ascii=False, indent=2)

                log.write(f"[{record['status'].upper()}] {module_name} → {data_file}\n")
                print(f"[{record['status'].upper()}] {module_name} → {data_file}")

            except Exception as e:
                record = {
                    "date": query_date,
                    "module": module_name.split(".")[-1],
                    "status": "error",
                    "error": str(e),
                    "data": {},
                    "source": "-"
                }
                suffix = "_dev" if dev_mode else ""
                data_file = os.path.join(BASE_DIR, f"{exec_day}_{record['module']}{suffix}.json")
                with open(data_file, "w", encoding="utf-8") as f:
                    json.dump(record, f, ensure_ascii=False, indent=2)

                log.write(f"[ERROR] {module_name} → {data_file}\n")
                log.write(f"錯誤訊息 (Traceback)：{format_traceback(e)}\n")
                print(f"[ERROR] {module_name} → 詳見 {log_file}")
                error_count += 1

        log.write("\n=== 驗收統計 ===\n")
        log.write(f"成功模組數：{success_count}\n")
        log.write(f"失敗模組數：{fail_count}\n")
        log.write(f"錯誤模組數：{error_count}\n")
        log.write(f"無效模組數：{invalid_count}\n")

    print("=== 驗收統計 ===")
    print(f"成功模組數：{success_count}")
    print(f"失敗模組數：{fail_count}")
    print(f"錯誤模組數：{error_count}")
    print(f"無效模組數：{invalid_count}")
    print(f"詳細紀錄請查看：{log_file}")

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
