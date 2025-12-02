"""
===========================================================
 run.py  —  模組統一執行程式
===========================================================

【用途】
- 執行指定查詢日期的模組，並將結果寫入 data/ 與 logs/
- 不管成功或失敗，皆會寫入一筆平坦 JSON 檔案到 data/
- log 檔案會完整記錄 [START] / [SUCCESS] / [FAIL] / [ERROR] / [INVALID] 與一行平坦資料

【用法】
  python run.py [查詢日期] [模式] [--module 模組名稱]

【參數說明】
  查詢日期 : 必填，格式 YYYY-MM-DD，例如 2025-12-01
  模式     : 選填，"dev" 表示執行 dev/ 下的模組；不填表示執行 modules/ 下的模組
  --module : 選填，只執行指定模組（不含副檔名 .py）

【範例】
  執行所有 dev 模組：
    python run.py 2025-12-01 dev

  執行所有正式模組：
    python run.py 2025-12-01

  只執行單一模組：
    python run.py 2025-12-01 dev --module f01_fetcher_dev_claude

【輸出檔案】
  data/{執行日}_{模組}.json        ← 正式模式
  data/{執行日}_{模組}_dev.json    ← 驗收模式
  logs/{執行日}_run.log            ← 正式模式 log
  logs/{執行日}_run_dev.log        ← 驗收模式 log

【注意事項】
- 每個模組執行後，必定會在 log 檔案留下完整一行平坦資料
- JSON 檔案只會有一筆資料（單一查詢日、單一模組）
- status 欄位可能為 success / fail / error / invalid
- 若模組失敗或錯誤，JSON 仍會寫入，但數值欄位為 "-"
===========================================================
"""

import os
import sys
import json
import importlib
from datetime import datetime
from utils.debug_pipeline import format_traceback

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
    return {
        "日期": date,
        "外資多方口數": to_int_safe(d.get("外資多方口數")),
        "外資空方口數": to_int_safe(d.get("外資空方口數")),
        "外資多空淨額": to_int_safe(d.get("外資多空淨額")),
        "source": result.get("source", "-") if isinstance(result, dict) else "-",
        "status": status_override or (result.get("status", "invalid") if isinstance(result, dict) else "invalid"),
        "module": result.get("module", module_name.split(".")[-1]) if isinstance(result, dict) else module_name.split(".")[-1]
    }

def format_row(record):
    return "\t".join(str(record.get(field, "-")) for field in FIELDS)

def get_module_list(folder: str, only_module: str = None):
    files = [f for f in os.listdir(folder) if f.endswith(".py") and not f.startswith("_")]
    modules = [f"{folder}.{f[:-3]}" for f in files]
    if only_module:
        modules = [m for m in modules if m.endswith(only_module)]
    return modules

def run(query_date: str, dev_mode: bool, only_module: str = None):
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    folder = "dev" if dev_mode else "modules"
    mode = "驗收模式" if dev_mode else "正式模式"
    exec_day = datetime.now().strftime("%Y-%m-%d")

    log_file = f"logs/{exec_day}_run{'_dev' if dev_mode else ''}.log"
    exec_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    success_count = fail_count = error_count = invalid_count = 0

    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"\n=== 查詢日期: {query_date} ｜ 執行日期: {exec_time} ｜ 模式: {mode} ===\n")
        log.write("\t".join(FIELDS) + "\n")

        for module_name in get_module_list(folder, only_module):
            log.write(f"[START] {module_name}\n")

            try:
                mod = importlib.import_module(module_name)
                result = mod.fetch(query_date)

                if not isinstance(result, dict) or "status" not in result:
                    log.write(f"[INVALID] {module_name} → 無效回傳格式\n")
                    record = build_flat_record(query_date, result, module_name, status_override="invalid")
                    invalid_count += 1
                else:
                    record = build_flat_record(query_date, result, module_name)
                    if result["status"] == "success":
                        log.write(f"[SUCCESS] {module_name}\n")
                        success_count += 1
                    else:
                        log.write(f"[FAIL] {module_name}\n")
                        log.write(f"錯誤訊息：{result.get('error','未知錯誤')}\n")
                        fail_count += 1

                # ✅ 寫入 JSON（使用執行日命名）
                suffix = "_dev" if dev_mode else ""
                data_file = f"data/{exec_day}_{record['module']}{suffix}.json"
                with open(data_file, "w", encoding="utf-8") as f:
                    json.dump(record, f, ensure_ascii=False, indent=2)
                log.write(f"[WRITE] 已寫入資料檔案：{data_file}\n")
                log.write(format_row(record) + "\n")

            except Exception as e:
                log.write(f"[ERROR] {module_name}\n")
                log.write(f"錯誤訊息 (Traceback)：{format_traceback(e)}\n")
                record = build_flat_record(query_date, {}, module_name, status_override="error")
                suffix = "_dev" if dev_mode else ""
                data_file = f"data/{exec_day}_{record['module']}{suffix}.json"
                with open(data_file, "w", encoding="utf-8") as f:
                    json.dump(record, f, ensure_ascii=False, indent=2)
                log.write(f"[WRITE] 已寫入資料檔案：{data_file}\n")
                log.write(format_row(record) + "\n")
                error_count += 1

        log.write("\n=== 驗收統計 ===\n")
        log.write(f"成功模組數：{success_count}\n")
        log.write(f"失敗模組數：{fail_count}\n")
        log.write(f"錯誤模組數：{error_count}\n")
        log.write(f"無效模組數：{invalid_count}\n")

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
    print(f"執行完成，請查看 logs/{datetime.now().strftime('%Y-%m-%d')}_run{'_dev' if dev_mode else ''}.log")
