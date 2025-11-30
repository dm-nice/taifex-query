"""
run_debug.py
模組測試工具：快速驗證 fetchers/ 裡的模組是否能正確匯入與執行

使用方式：
1. 修改 target_name 與 target_module 為你要測試的模組
2. 執行 python run_debug.py
"""

import os, sys
import importlib
import json

# 加入專案根目錄到 sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ✅ 修改這兩行來測試不同模組
target_name = "f01"
target_module = "fetchers.f01_fetcher"

# 測試日期
test_date = "2025-11-28"

# 額外偵錯輸出
print("📂 目前目錄:", ROOT_DIR)
print("📁 是否存在 fetchers 資料夾:", os.path.isdir(os.path.join(ROOT_DIR, "fetchers")))
print("📄 是否存在 f01_fetcher.py:", os.path.isfile(os.path.join(ROOT_DIR, "fetchers", "f01_fetcher.py")))
print("🔍 sys.path:", sys.path)

# 匯入模組並執行 fetch()
try:
    mod = importlib.import_module(target_module)
    result = mod.fetch(test_date)
    print(f"\n✅ 成功執行 {target_name} 模組：")
    print(json.dumps(result, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"\n❌ 匯入或執行 {target_name} 模組失敗：{e}")
