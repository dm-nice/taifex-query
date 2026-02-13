"""
TAIFEX 爬蟲系統 - 主選單
"""

import os
import sys

def clear_screen():
    """清除螢幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """顯示主選單"""
    print("=" * 50)
    print("  TAIFEX 爬蟲系統")
    print("=" * 50)
    print()
    print("  1. 日盤 (F01-F20)")
    print("  2. 夜盤 - API 版 (F21-F25) [推薦，速度快]")
    print("  3. 夜盤 - Playwright 版 (F21-F25)")
    print()
    print("  0. 離開")
    print()
    print("-" * 50)

def run_daytime():
    """執行日盤爬蟲"""
    print("\n執行日盤爬蟲...\n")
    from daytime_query import main as daytime_main
    daytime_main()

def run_nighttime_api():
    """執行夜盤爬蟲 (API 版)"""
    print("\n執行夜盤爬蟲 (API 版)...\n")
    # 動態 import 中文檔名
    import importlib.util
    spec = importlib.util.spec_from_file_location("nighttime_api", "夜盤API抓取資料.py")
    if spec is None or spec.loader is None:
        print("錯誤: 無法載入 夜盤API抓取資料.py")
        return
    nighttime_api = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nighttime_api)
    nighttime_api.main()

def run_nighttime_playwright():
    """執行夜盤爬蟲 (Playwright 版)"""
    print("\n執行夜盤爬蟲 (Playwright 版)...\n")
    from nighttime_query import main as nighttime_main
    nighttime_main()

def main():
    while True:
        clear_screen()
        show_menu()

        choice = input("請選擇 (0-3): ").strip()

        if choice == '1':
            run_daytime()
            input("\n按 Enter 返回選單...")

        elif choice == '2':
            run_nighttime_api()
            input("\n按 Enter 返回選單...")

        elif choice == '3':
            run_nighttime_playwright()
            input("\n按 Enter 返回選單...")

        elif choice == '0':
            print("\n再見！")
            sys.exit(0)

        else:
            print("\n無效選項，請重新選擇")
            input("按 Enter 繼續...")

if __name__ == "__main__":
    main()
