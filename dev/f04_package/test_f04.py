"""
F04 模組自動化測試腳本
========================
"""

import sys
import io
import subprocess
from pathlib import Path
from datetime import datetime

# 設定 UTF-8 輸出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

SCRIPT_DIR = Path(__file__).parent.resolve()
MODULE_PATH = SCRIPT_DIR / 'f04_fetcher.py'

TEST_CASES = {
    'normal': [
        '2025-12-04', # 正常交易日
    ],
    'holiday': [
        '2025-12-07', # 週日
    ],
    'error': [
        'invalid_date',
    ]
}

def run_test(date):
    try:
        result = subprocess.run(
            ['python', str(MODULE_PATH), date],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), -1

def main():
    print("🚀 F04 測試開始")
    print("="*60)
    
    passed = 0
    total = 0
    
    # 1. 正常案例
    for date in TEST_CASES['normal']:
        total += 1
        print(f"測試日期: {date} (預期成功)")
        output, code = run_test(date)
        print(f"輸出: {output}")
        if "F04:" in output and "27,799" in output:
            print("✅ PASS")
            passed += 1
        else:
            print("❌ FAIL")
        print("-" * 30)
            
    # 2. 假日案例
    for date in TEST_CASES['holiday']:
        total += 1
        print(f"測試日期: {date} (預期無資料)")
        output, code = run_test(date)
        print(f"輸出: {output}")
        if "錯誤" in output or "無資料" in output or "查無" in output:
            print("✅ PASS")
            passed += 1
        else:
            print("❌ FAIL (Should fail but got success?)")
        print("-" * 30)

    # 3. 異常案例
    for date in TEST_CASES['error']:
        total += 1
        print(f"測試日期: {date} (預期格式錯誤)")
        output, code = run_test(date)
        print(f"輸出: {output}")
        if "錯誤" in output:
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

if __name__ == '__main__':
    main()
