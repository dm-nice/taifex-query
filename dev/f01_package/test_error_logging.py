"""
F01 錯誤日誌功能測試
==================

功能：
- 測試 format_f01_output() 增強後的新參數功能
- 驗證時間戳和上下文信息的正確格式化

使用方式：
    python test_error_logging.py

版本：1.0
建立日期：2025-12-15
"""

import sys
import io
from pathlib import Path

# 設定 UTF-8 輸出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 自動偵測專案根目錄
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
MODULE_PATH = PROJECT_ROOT / 'modules' / 'f01_fetcher.py'

# 將 modules 目錄加入 Python 路徑
sys.path.insert(0, str(PROJECT_ROOT / 'modules'))

# 導入 f01_fetcher
import importlib.util
spec = importlib.util.spec_from_file_location("f01_fetcher", MODULE_PATH)
f01_fetcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f01_fetcher)

format_f01_output = f01_fetcher.format_f01_output


def test_basic_backward_compatibility():
    """測試向後兼容性"""
    test_data = {"net_position": -26823, "source": "TAIFEX"}
    result = format_f01_output("2025-12-15", "success", data=test_data)
    assert "F01:" in result and "[TAIFEX]" in result
    print("✅ 向後兼容性")


def test_output_with_timestamp():
    """測試時間戳參數"""
    timestamp = "2025-12-15 14:30:45"
    result = format_f01_output(
        "2025-12-15",
        "error",
        error="連線逾時",
        timestamp=timestamp
    )
    assert "F01 錯誤:" in result and timestamp in result
    print("✅ 時間戳參數")


def test_output_with_context():
    """測試上下文參數"""
    context = {"timeout": 30}
    result = format_f01_output(
        "2025-12-15",
        "error",
        error="連線逾時",
        context=context
    )
    assert "F01 錯誤:" in result and "timeout" in result
    print("✅ 上下文參數")


def test_timestamp_and_context():
    """測試時間戳+上下文"""
    result = format_f01_output(
        "2025-12-15",
        "error",
        error="HTTP 錯誤",
        timestamp="2025-12-15 14:30:45",
        context={"status_code": 500}
    )
    assert all(x in result for x in ["F01 錯誤:", "2025-12-15 14:30:45", "500"])
    print("✅ 時間戳+上下文")


def run_all_tests():
    """執行所有測試"""
    print("\n" + "="*70)
    print("  🚀 F01 錯誤日誌功能測試")
    print("="*70 + "\n")

    tests = [
        test_basic_backward_compatibility,
        test_output_with_timestamp,
        test_output_with_context,
        test_timestamp_and_context,
    ]

    passed = failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__doc__}: {e}")
            failed += 1

    print("\n" + "="*70)
    print(f"  📊 測試結果：✅ {passed} 通過，❌ {failed} 失敗")
    print("="*70)

    return failed == 0


if __name__ == '__main__':
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 測試執行失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
