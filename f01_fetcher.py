"""
測試 f01_fetcher_範例.py - 台指期貨外資淨口數抓取程式
測試日期：2025-11-28
"""

import sys
sys.path.append('c:\\Taifex\\fetchers')

from f01_fetcher_範例 import fetch
import json

def test_f01_fetcher():
    """測試 F01 fetcher"""
    print("=" * 70)
    print("測試台指期貨外資淨口數抓取程式 (F01)")
    print("=" * 70)
    
    # 測試日期
    test_date = "2025-11-28"
    print(f"\n測試日期：{test_date}")
    print("-" * 70)
    
    # 執行抓取
    print("正在執行 fetch()...")
    result = fetch(test_date)
    
    # 顯示結果
    print("\n結果：")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 檢查狀態
    print("\n" + "-" * 70)
    if result.get("status") == "success":
        print("✓ 抓取成功")
        print(f"  摘要：{result.get('summary')}")
    else:
        print("✗ 抓取失敗")
        print(f"  錯誤：{result.get('error')}")
    
    print("=" * 70)
    
    return result

if __name__ == "__main__":
    result = test_f01_fetcher()
