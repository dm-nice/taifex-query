"""
批次修復所有模組的 UTF-8 包裝問題
避免重複包裝 sys.stdout 導致 I/O 錯誤
"""

import sys
import io
import re
from pathlib import Path

# 設定 UTF-8 輸出
if sys.stdout.encoding != 'utf-8' and not hasattr(sys.stdout, '_wrapped_for_utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stdout._wrapped_for_utf8 = True

# 要修復的目錄
DIRS_TO_FIX = [
    Path("C:/Taifex/dev"),
    Path("C:/Taifex/modules")
]

# 舊的包裝模式（需要替換）
OLD_PATTERNS = [
    # 模式 1: f02 風格
    (
        r'# 設定 UTF-8 輸出\(解決 Windows 終端亂碼\)\n'
        r'if sys\.platform == \'win32\':\n'
        r'    if not getattr\(sys, "frozen", False\):\n'
        r'        sys\.stdout = io\.TextIOWrapper\(sys\.stdout\.buffer, encoding=\'utf-8\'\)\n'
        r'        sys\.stderr = io\.TextIOWrapper\(sys\.stderr\.buffer, encoding=\'utf-8\'\)',

        '# 設定 UTF-8 輸出（解決 Windows 終端亂碼）\n'
        '# 只在尚未包裝時才進行包裝，避免重複包裝導致 I/O 錯誤\n'
        'if sys.platform == \'win32\':\n'
        '    if not getattr(sys, "frozen", False):\n'
        '        if not hasattr(sys.stdout, \'_wrapped_for_utf8\'):\n'
        '            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=\'utf-8\')\n'
        '            sys.stdout._wrapped_for_utf8 = True\n'
        '        if not hasattr(sys.stderr, \'_wrapped_for_utf8\'):\n'
        '            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding=\'utf-8\')\n'
        '            sys.stderr._wrapped_for_utf8 = True'
    ),

    # 模式 2: f01 風格
    (
        r'# 設定 UTF-8 輸出\(解決 Windows 終端亂碼，PyInstaller 已處理打包的情境\)\n'
        r'if sys\.platform == \'win32\' and not getattr\(sys, "frozen", False\):\n'
        r'    sys\.stdout = io\.TextIOWrapper\(sys\.stdout\.buffer, encoding=\'utf-8\'\)\n'
        r'    sys\.stderr = io\.TextIOWrapper\(sys\.stderr\.buffer, encoding=\'utf-8\'\)',

        '# 設定 UTF-8 輸出（解決 Windows 終端亂碼，PyInstaller 已處理打包的情境）\n'
        '# 只在尚未包裝時才進行包裝，避免重複包裝導致 I/O 錯誤\n'
        'if sys.platform == \'win32\' and not getattr(sys, "frozen", False):\n'
        '    if not hasattr(sys.stdout, \'_wrapped_for_utf8\'):\n'
        '        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=\'utf-8\')\n'
        '        sys.stdout._wrapped_for_utf8 = True\n'
        '    if not hasattr(sys.stderr, \'_wrapped_for_utf8\'):\n'
        '        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding=\'utf-8\')\n'
        '        sys.stderr._wrapped_for_utf8 = True'
    ),

    # 模式 3: 簡化版
    (
        r'if sys\.stdout\.encoding != \'utf-8\':\n'
        r'    sys\.stdout = io\.TextIOWrapper\(sys\.stdout\.buffer, encoding=\'utf-8\'\)',

        'if sys.stdout.encoding != \'utf-8\' and not hasattr(sys.stdout, \'_wrapped_for_utf8\'):\n'
        '    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=\'utf-8\')\n'
        '    sys.stdout._wrapped_for_utf8 = True'
    )
]

def fix_file(file_path: Path) -> bool:
    """修復單一檔案"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 嘗試所有模式
        for old_pattern, new_text in OLD_PATTERNS:
            content = re.sub(old_pattern, new_text, content)

        # 如果有修改，寫回檔案
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"❌ 修復失敗 {file_path}: {e}")
        return False

def main():
    """主程式"""
    print("=" * 70)
    print("  批次修復 UTF-8 包裝問題")
    print("=" * 70)
    print()

    total_files = 0
    fixed_files = 0

    for dir_path in DIRS_TO_FIX:
        if not dir_path.exists():
            print(f"⚠️  目錄不存在: {dir_path}")
            continue

        print(f"📁 掃描目錄: {dir_path}")

        # 遍歷所有 .py 檔案
        for py_file in dir_path.rglob("*.py"):
            # 跳過本腳本
            if py_file.name == "fix_utf8_wrapper.py":
                continue

            # 檢查是否包含 sys.stdout = io.TextIOWrapper
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    if 'sys.stdout = io.TextIOWrapper' in f.read():
                        total_files += 1
                        print(f"  🔍 檢查: {py_file.relative_to(dir_path.parent)}")

                        if fix_file(py_file):
                            fixed_files += 1
                            print(f"    ✅ 已修復")
                        else:
                            print(f"    ⏭️  已是正確格式，跳過")
            except Exception as e:
                print(f"  ❌ 讀取失敗 {py_file}: {e}")

    print()
    print("=" * 70)
    print(f"  📊 修復統計")
    print("=" * 70)
    print(f"  檢查檔案: {total_files}")
    print(f"  修復檔案: {fixed_files}")
    print(f"  跳過檔案: {total_files - fixed_files}")
    print("=" * 70)

if __name__ == '__main__':
    main()
