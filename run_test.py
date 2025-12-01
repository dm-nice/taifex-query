"""
run_test.py
專門用來驗收 outsource/ 子目錄下的外包模組
支援命令列輸入日期，未輸入則預設為今日
"""

import importlib
import os
import sys
import json
from datetime import datetime
from utils.debug_pipeline import report_error

# 驗收模式：只測試 outsource/ 裡的模組
MODULES = [
    "outsource.f01_fetcher_dev",
    # "outsource.f02_fetcher_dev",
    # ...
]

def run(date: str):
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("issues", exist_ok=True)

    log_file = f"logs/{date}_run_test.log"
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"\n=== 驗收測試日期: {date} ===\n")

        for module_name in MODULES:
            try:
                mod = importlib.import_module(module_name)
                result = mod.fetch(date)

                if result["status"] == "success":
                    data_file = f"data/{date}_{result['module']}_test.json"
                    with open(data_file, "w", encoding="utf-8") as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    log.write(f"[SUCCESS] {module_name} → {data_file}\n")

                else:
                    error_file = report_error(result["module"], date, result["error"])
                    log.write(f"[FAIL] {module_name} → {error_file}\n")

            except Exception as e:
                error_file = report_error(module_name, date, str(e))
                log.write(f"[ERROR] {module_name} → {error_file}\n")


if __name__ == "__main__":
    # ✅ 支援命令列輸入日期，未輸入則預設今日
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = datetime.now().strftime("%Y-%m-%d")

    run(date)
    print(f"驗收測試完成，請查看 logs/{date}_run_test.log")
