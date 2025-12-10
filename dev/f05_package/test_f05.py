"""
test_f05.py
F05 模組 (台指期貨選擇權總成交量) 自動化測試腳本
"""

import sys
import os
import io

# 將專案根目錄加入 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dev.f05_package.f05_fetcher import fetch

# Removed sys.stdout wrapper to prevent I/O closed error

def run_test(date):
    """執行單一測試案例"""
    try:
        output = fetch(date)
        return output
    except Exception as e:
        return f"CRASH: {str(e)}"

def main():
    print("🚀 F05 測試開始")
    print("=" * 60)
    
    test_cases = [
        ("2025-12-10", "success", "正常交易日"),
        ("2025-12-07", "failed", "假日 (無資料)"),
        ("invalid", "error", "格式錯誤")
    ]
    
    passed = 0
    total = len(test_cases)
    
    for date, expected_status, desc in test_cases:
        print(f"測試日期: {date} ({desc})")
        output = run_test(date)
        print(f"輸出: {output}")
        
        is_pass = False
        if expected_status == "success":
            expected_date = date.replace("-", ".")
            if "F05:" in output and expected_date in output and "錯誤" not in output:
                is_pass = True
        elif expected_status == "failed":
            if "F05" in output and ("錯誤" in output or "無交易資料" in output):
                # 視回傳訊息而定，有時無資料會被歸類在 F05 錯誤
                is_pass = True
        elif expected_status == "error":
            if "錯誤" in output:
                is_pass = True
                
        if is_pass:
            print("✅ PASS")
            passed += 1
        else:
            print("❌ FAIL")
            
        print("-" * 30)
        
    print(f"📊 測試結果: {passed}/{total} 通過")
    if passed == total:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
