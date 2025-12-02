"""
run.py
主程式：執行所有模組並分流結果
支援命令列輸入日期，預設為今日
"""

import os
import sys
import json
from datetime import datetime

# 加入專案根目錄到 sys.path，確保 fetchers/ 可匯入
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ✅ 匯入模組（目前只執行 f01）
from fetchers.f01_fetcher import fetch as f01

# ✅ 工具模組（錯誤回報）
from utils.debug_pipeline import report_error

# 建立目錄
for folder in ["data", "logs", "issues"]:
    os.makedirs(folder, exist_ok=True)

def save_to_data(module, date, data):
    """成功結果存到 data/"""
    filename = f"data/{date}_{module}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_to_logs(module, date, message):
    """一般紀錄存到 logs/"""
    filename = f"logs/{date}_{module}.log"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")

def main(date: str):
    modules = [("f01", f01)]  # ✅ 可擴充模組清單

    results = []

    for name, module in modules:
        try:
            result = module(date)
            results.append(result)

            if result["status"] == "success":
                save_to_data(result["module"], result["date"], result["data"])
                save_to_logs(result["module"], result["date"], "成功寫入 data/")
            else:
                report_error(
                    module=result["module"],
                    date=result["date"],
                    error=result.get("error", "未知錯誤"),
                )
                save_to_logs(result["module"], result["date"], "失敗，已回報 issues/")
        except Exception as e:
            report_error(module=name, date=date, error=str(e))
            save_to_logs(name, date, f"例外錯誤: {e}")

    return results

if __name__ == "__main__":
    # ✅ 支援命令列輸入日期，預設為今日
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = datetime.today().strftime("%Y-%m-%d")

    data = main(date)
    print(json.dumps(data, ensure_ascii=False, indent=2))

