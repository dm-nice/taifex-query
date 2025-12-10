"""
test_f06.py
"""
import sys
import os
# Removed sys.stdout wrapper to prevent I/O closed error

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dev.f06_package.f06_fetcher import fetch

def main():
    print("🚀 F06 測試 (TVIX)")
    # 測試今天 (可能無資料 NaN)
    # 測試今天 (可能無資料 NaN)
    print(f"Test Today: {fetch('2025-12-10')}")
    
    # 驗證輸出名稱是否正確
    output = fetch('2025-12-10')
    if "臺指選擇權波動率指數" in output:
        print("✅ Name Check Passed")
    else:
        print(f"❌ Name Check Failed: Got {output}")
    # 測試無效日期
    print(f"Test Invalid: {fetch('invalid')}")

if __name__ == "__main__":
    main()
