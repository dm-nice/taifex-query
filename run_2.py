"""
run.py
主程式：統一呼叫 F01–F20 模組
依照 interface_spec.md 與 architecture.md 規範設計
"""

import os
import importlib
from datetime import datetime
from utils.debug_pipeline import report_error

# 要執行的模組清單 (可依需求調整)
MODULES = [
    "f01_fetcher",
    # "f02_fetcher",
    # "f10_fetcher",
    # ...
]

def run(date: str):
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("issues", exist_ok=True)

    log_file = f"logs/{date}_run.log"
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"\n=== 執行日期: {date} ===\n")

        for module_name in MODULES:
            try:
                # 動態載入模組
                mod = importlib.import_module(f"fetchers.{module_name}")
                result = mod.fetch(date)

                if result["status"] == "success":
                    # 成功 → 存到 data/
                    data_file = f"data/{date}_{result['module']}.json"
                    import json
                    with open(data_file, "w", encoding="utf-8") as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)

                    log.write(f"[SUCCESS] {module_name} → {data_file}\n")

                else:
                    # 失敗 → 呼叫 debug_pipeline
                    error_file = report_error(result["module"], date, result["error"])
                    log.write(f"[FAIL] {module_name} → {error_file}\n")

            except Exception as e:
                # 捕捉主程式層級錯誤
                error_file = report_error(module_name, date, str(e))
                log.write(f"[ERROR] {module_name} → {error_file}\n")


if __name__ == "__main__":
    # 預設執行今天日期
    today = datetime.now().strftime("%Y-%m-%d")
    run(today)
    print(f"執行完成，請查看 logs/{today}_run.log")
