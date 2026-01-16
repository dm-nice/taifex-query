#!/usr/bin/env python
"""
Test script for Wantgoo nighttime scraper (F21-F25)
"""
import sys
sys.path.insert(0, '.')

from scrapers.nighttime import query_wantgoo_nighttime

def test():
    print("Testing Wantgoo Nighttime Scraper (F21-F25)...")
    print("=" * 60)

    results = query_wantgoo_nighttime()

    if results:
        print(f"\nSuccess! Found {len(results)} indicators:")
        print("-" * 60)

        for item in sorted(results, key=lambda x: x['f_code']):
            f_code = item['f_code']
            name = item['name']
            value = item['value']
            field = item.get('field', '')

            print(f"  {f_code:3s} {name:15s} [{field:6s}]: {value:>8s}")

        print("-" * 60)

        # 驗證所有 F21-F25 都存在
        expected = {'F21', 'F22', 'F23', 'F24', 'F25'}
        actual = {item['f_code'] for item in results}
        missing = expected - actual

        if missing:
            print(f"\nWarning: Missing indicators: {missing}")
            return False
        else:
            print("\nAll 5 indicators found!")

            # 驗證值格式
            print("\nFormat Validation:")
            all_valid = True
            for item in results:
                value = item['value']
                # 檢查是否包含 + 或 - 符號
                if not (value.startswith('+') or value.startswith('-')):
                    print(f"  ERROR {item['f_code']}: Missing sign: {value}")
                    all_valid = False
                # 檢查是否包含 % 符號（不應該包含）
                elif '%' in value:
                    print(f"  ERROR {item['f_code']}: Should not contain %: {value}")
                    all_valid = False
                # 檢查是否包含逗號（不應該包含）
                elif ',' in value:
                    print(f"  ERROR {item['f_code']}: Should not contain comma: {value}")
                    all_valid = False
                else:
                    print(f"  OK {item['f_code']}: {value}")

            return all_valid
    else:
        print("Failed to fetch data")
        return False

if __name__ == "__main__":
    success = test()
    sys.exit(0 if success else 1)
