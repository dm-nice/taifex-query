"""
quick_fetch.py - 快速抓取台指期貨關鍵數據 (F01-F04)
穩定版：使用 Subprocess 避免模組間的 I/O 衝突
"""

import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path

# 取得 python 執行路徑 (優先使用虛擬環境)
PYTHON_EXE = str(Path(sys.executable))

def run_module(module_name, date):
    """使用子程序執行模組並獲取輸出"""
    try:
        # 呼叫 python -m modules.fxx_fetcher [date]
        # 注意：你的模組必須支援從命令列執行或被當作模組執行
        # 由於 run.py 使用了 fetch(date)，我們直接執行一個小片段來呼叫它
        cmd = [
            PYTHON_EXE, "-c", 
            f"import sys; from modules import {module_name}; print({module_name}.fetch('{date}'))"
        ]
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"錯誤: {str(e)}"

def main():
    query_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    
    print("\n" + "═" * 70)
    print(f"  📊 台指期貨關鍵數據報告 (日期: {query_date})")
    print("═" * 70 + "\n")

    targets = [
        ("F01 外資未平倉淨額", "f01_fetcher"),
        ("F02 外資未平倉多方", "f02_fetcher"),
        ("F03 外資未平倉空方", "f03_fetcher"),
        ("F04 台指期貨收盤價", "f04_fetcher"),
    ]

    for label, mod_name in targets:
        print(f" 正在獲取 {label}...", end="", flush=True)
        res = run_module(mod_name, query_date)
        
        # 提取結果 (去除模組內部的 log 訊息，只保留最後一行結果)
        clean_res = res.split('\n')[-1] if res else "無回傳資料"
        
        print(f"\r ✅ {label}:")
        print(f"    {clean_res}\n")

    print("═" * 70)
    print("  ⚠️  市場有風險，投資需謹慎。")
    print("═" * 70)
    
    if os.isatty(sys.stdin.fileno()):
        input("\n按 [Enter] 鍵結束...")

if __name__ == "__main__":
    main()
