"""
run.py
主程式整合範例
統一呼叫 F1–F20 模組，並依結果自動分流到 data/、logs/、issues/

自動分流：成功 → data/，失敗 → issues/，一般紀錄 → logs/
模組統一呼叫：所有 F1–F20 都照 fetch(date) 規範執行
錯誤自動回報：失敗或例外會呼叫 debug_pipeline.py，產生 Markdown 錯誤紀錄
可擴充：未來增加 F21–F30，只要加到 fetchers/ 並匯入即可
"""

import os
import sys
import json
from datetime import datetime

# 加入專案根目錄到 sys.path，確保 fetchers/ 可匯入
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 匯入 F01–F20 模組
from fetchers.f01_fetcher import fetch as f01
from fetchers.f02_fetcher import fetch as f02
from fetchers.f03_fetcher import fetch as f03
from fetchers.f04_fetcher import fetch as f04
from fetchers.f05_fetcher import fetch as f05
from fetchers.f06_fetcher import fetch as f06
from fetchers.f07_fetcher import fetch as f07
from fetchers.f08_fetcher import fetch as f08
from fetchers.f09_fetcher import fetch as f09
from fetchers.f10_fetcher import fetch as f10
from fetchers.f11_fetcher import fetch as f11
from fetchers.f12_fetcher import fetch as f12
from fetchers.f13_fetcher import fetch as f13
from fetchers.f14_fetcher import fetch as f14
from fetchers.f15_fetcher import fetch as f15
from fetchers.f16_fetcher import fetch as f16
from fetchers.f17_fetcher import fetch as f17
from fetchers.f18_fetcher import fetch as f18
from fetchers.f19_fetcher import fetch as f19
from fetchers.f20_fetcher import fetch as f20

# 工具模組 (錯誤回報)
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
    modules = [
        ("f01", f01), ("f02", f02), ("f03", f03), ("f04", f04), ("f05", f05),
        ("f06", f06), ("f07", f07), ("f08", f08), ("f09", f09), ("f10", f10),
        ("f11", f11), ("f12", f12), ("f13", f13), ("f14", f14), ("f15", f15),
        ("f16", f16), ("f17", f17), ("f18", f18), ("f19", f19), ("f20", f20),
    ]

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
    # 範例：執行 2025-11-28 的資料抓取
    data = main("2025-11-28")
    print(json.dumps(data, ensure_ascii=False, indent=2))
