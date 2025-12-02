"""
===========================================================
 run.py  —  模組統一執行程式 (集中輸出版本)
===========================================================

【用途】
- 執行指定查詢日期的模組，並將結果寫入 C:\Taifex\data\
- 不管成功或失敗，皆會寫入一筆平坦 JSON 檔案
- log 檔案也寫在同一目錄
- 終端機即時顯示執行進度 (print)

【用法】
  python run.py [查詢日期] [模式] [--module 模組名稱]
===========================================================
"""

import os
import sys
import json
import importlib
from datetime import datetime
from utils.debug_pipeline import format_traceback

FIELDS = ["日期", "外資多方口數", "外資空方口數", "外資多空淨額", "source", "status", "module"]

BASE_DIR = r"C:\Taifex\data"   # ✅ 集中輸出目錄

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

    log_file = os.path.join(BASE_DIR, f"{exec_day}_run{'_dev' if dev_mode else ''}.log")
    exec_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    success_count = fail_count = error_count = invalid_count = 0

    print(f"=== 查詢日期: {query_date} ｜ 執行日期: {exec_time} ｜ 模式: {mode} ===")

    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"\n=== 查詢日期: {query_date} ｜ 執行日期: {exec_time} ｜ 模式: {mode} ===\n")
        log.write(format_row({f: f for f in FIELDS}) + "\n")

        for module_name in get_module_list(folder, only_module):
            try:
                print(f"[執行] {module_name}")
                mod = importlib.import_module(module_name)
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
                data_file = os.path.join(BASE_DIR, f"{exec_day}_{record['module']}{suffix}.json")
                with open(data_file, "w", encoding="utf-8") as f:
                    json.dump(record, f, ensure_ascii=False, indent=2)

                log.write(format_row(record) + "\n")
                log.write(f"[START] {module_name}\n")
                log.write(f"[{record['status'].upper()}] {module_name}\n")
                log.write(f"[WRITE] 已寫入資料檔案：{data_file}\n")

                print(f"[{record['status'].upper()}] {module_name} → {data_file}")

            except Exception as e:
                record = build_flat_record(query_date, {}, module_name, status_override="error")
                suffix = "_dev" if dev_mode else ""
                data_file = os.path.join(BASE_DIR, f"{exec_day}_{record['module']}{suffix}.json")
                with open(data_file, "w", encoding="utf-8") as f:
                    json.dump(record, f, ensure_ascii=False, indent=2)

                log.write(format_row(record) + "\n")
                log.write(f"[START] {module_name}\n")
                log.write(f"[ERROR] {module_name}\n")
                log.write(f"錯誤訊息 (Traceback)：{format_traceback(e)}\n")
                log.write(f"[WRITE] 已寫入資料檔案：{data_file}\n")

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
