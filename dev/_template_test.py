"""
FXX 模組自動化測試腳本範本
========================

📋 使用說明
----------

### 1️⃣ 複製與命名
將此範本複製並命名為 `test_fXX_auto.py`（例如 `test_f02_auto.py`）

### 2️⃣ 必須修改的部分（搜尋 FXX 找到所有需要修改的位置）

**A. 模組路徑設定 (第 48 行)**
```python
MODULE_PATH = PROJECT_ROOT / 'modules' / 'fXX_fetcher.py'  # ← 改為實際模組檔名
```

**B. 測試案例配置 (第 54-82 行)**
```python
TEST_CASES = {
    'normal_dates': {
        'name': '正常交易日測試',
        'dates': [
            '2025-12-04',  # ← 修改為適合的測試日期
            '2025-12-03',
            '2025-11-28',
        ],
        'expect': 'success',
    },
    # ... 依據模組特性調整測試案例
}
```

**C. 格式驗證邏輯 (第 207-231 行)**
```python
def validate_output_format(output: str) -> Dict:
    # ← 修改為 FXX 模組的實際輸出格式規範
    checks = {
        'has_module_id': output.startswith('FXX:') or output.startswith('['),  # 改為 FXX
        'has_source': '[來源名稱]' in output or 'source: 來源名稱' in output,  # 改為實際來源
    }

    # 成功格式檢查（根據實際規範修改）
    if output.startswith('FXX:'):
        checks['format_valid'] = (
            # ← 這裡改為 FXX 模組的格式驗證條件
        )
```

**D. 主程式標題 (第 333 行)**
```python
print("  🚀 FXX 模組自動化測試")  # ← 改為 FXX
```

### 3️⃣ 選擇性修改的部分

- **測試逾時時間** (第 105 行): 預設 30 秒，如需調整請修改 `timeout=30`
- **輸出長度限制** (第 263 行): 預設 150 字元，可依需求調整

### 4️⃣ 執行測試
```bash
python dev/fXX_package/test_fXX_auto.py
```

### 5️⃣ 測試結果說明

**測試結果 (Test Result)**: PASS / FAIL
- 比對「實際狀態」是否符合「預期狀態」
- PASS: 符合預期（預期成功且實際成功，或預期錯誤且實際錯誤）
- FAIL: 不符合預期

**實際狀態 (Actual Status)**: success / error / failed / timeout
- success 🟢: 模組成功執行並回傳資料
- error 🔴: 模組回傳錯誤訊息（格式正確的錯誤）
- failed 🟡: 模組執行失敗（非預期錯誤）
- timeout ⏱️: 執行逾時

### 6️⃣ 範本版本資訊
- 範本來源: test_f01_auto.py v2.0
- 範本版本: 1.0
- 建立日期: 2025-12-08

---

功能特色：
- 自動測試 FXX 模組的各種情境
- 產生詳細的測試報告
- 支援批次測試多個日期
- 正確區分「實際結果」與「測試結果」
- 統計測試通過率與實際狀態分佈

---
"""

import sys
import io
import subprocess
from datetime import datetime
from typing import Dict, List
from pathlib import Path

# 設定 UTF-8 輸出（解決 Windows 終端亂碼）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ==================== 測試配置 ====================

# 自動偵測專案根目錄並設定模組路徑
SCRIPT_DIR = Path(__file__).parent.resolve()  # 腳本所在目錄
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # 專案根目錄 (C:\Taifex)
MODULE_PATH = PROJECT_ROOT / 'modules' / 'fXX_fetcher.py'  # ← 【必改】改為實際模組檔名

# 轉換為字串路徑
MODULE_PATH = str(MODULE_PATH)

# ==================== 測試案例配置 ====================
# ← 【必改】根據 FXX 模組的特性調整測試案例

TEST_CASES = {
    'normal_dates': {
        'name': '正常交易日測試',
        'dates': [
            '2025-12-04',  # ← 修改為適合的測試日期
            '2025-12-03',
            '2025-11-28',
        ],
        'expect': 'success',  # 預期狀態
    },
    'weekend_dates': {
        'name': '週末/假日測試',
        'dates': [
            '2025-12-07',  # 週六
            '2025-12-08',  # 週日
        ],
        'expect': 'may_fail',  # 可能失敗（視 API 限制而定）
    },
    'invalid_formats': {
        'name': '錯誤日期格式測試',
        'dates': [
            '20251204',      # 缺少分隔符
            '2025/12/04',    # 錯誤分隔符
            'invalid',       # 完全錯誤
            '2025-13-01',    # 月份錯誤
        ],
        'expect': 'error',  # 預期錯誤
    },
}


# ==================== 測試函式 ====================

def run_test(date: str, expected_status: str = 'success') -> Dict:
    """
    執行單一測試案例

    Args:
        date: 測試日期
        expected_status: 預期狀態 ('success', 'error', 'may_fail')

    Returns:
        測試結果字典
    """
    try:
        # 執行 FXX 模組
        result = subprocess.run(
            ['python', MODULE_PATH, date],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30  # ← 【選改】可調整逾時時間
        )

        output = result.stdout.strip()
        exit_code = result.returncode

        # 提取實際輸出（最後一行）
        output_lines = output.split('\n')
        actual_output = output_lines[-1] if output_lines else ''

        # 判斷實際狀態
        if exit_code == 0 and '錯誤:' not in actual_output:
            actual_status = 'success'
        elif '錯誤:' in actual_output:
            actual_status = 'error'
        else:
            actual_status = 'failed'

        # 判斷測試結果（PASS/FAIL）
        test_result = evaluate_test_result(actual_status, expected_status)

        return {
            'date': date,
            'actual_status': actual_status,  # 實際結果 (success/error/failed)
            'expected_status': expected_status,  # 預期結果
            'test_result': test_result,  # 測試結果 (PASS/FAIL)
            'exit_code': exit_code,
            'output': output,
            'actual_output': actual_output,  # 實際的模組輸出（最後一行）
            'error': None
        }

    except subprocess.TimeoutExpired:
        return {
            'date': date,
            'actual_status': 'timeout',
            'expected_status': expected_status,
            'test_result': 'FAIL',  # 逾時視為測試失敗
            'exit_code': -1,
            'output': '',
            'actual_output': '',
            'error': '執行逾時（超過 30 秒）'
        }
    except FileNotFoundError:
        return {
            'date': date,
            'actual_status': 'error',
            'expected_status': expected_status,
            'test_result': 'FAIL',  # 找不到檔案視為測試失敗
            'exit_code': -1,
            'output': '',
            'actual_output': '',
            'error': f'找不到模組檔案: {MODULE_PATH}'
        }
    except Exception as e:
        return {
            'date': date,
            'actual_status': 'error',
            'expected_status': expected_status,
            'test_result': 'FAIL',  # 未預期錯誤視為測試失敗
            'exit_code': -1,
            'output': '',
            'actual_output': '',
            'error': f'未預期的錯誤: {str(e)}'
        }


def evaluate_test_result(actual_status: str, expected_status: str) -> str:
    """
    評估測試結果是否符合預期

    Args:
        actual_status: 實際狀態 ('success', 'error', 'failed', 'timeout')
        expected_status: 預期狀態 ('success', 'error', 'may_fail')

    Returns:
        'PASS' 或 'FAIL'
    """
    if expected_status == 'success':
        # 預期成功：實際必須是 success
        return 'PASS' if actual_status == 'success' else 'FAIL'
    elif expected_status == 'error':
        # 預期錯誤：實際必須是 error
        return 'PASS' if actual_status == 'error' else 'FAIL'
    elif expected_status == 'may_fail':
        # 可能失敗：success 或 error 都算通過
        return 'PASS' if actual_status in ['success', 'error'] else 'FAIL'
    else:
        # 未知預期狀態，視為失敗
        return 'FAIL'


def validate_output_format(output: str) -> Dict:
    """
    驗證輸出格式是否符合統一文字格式 v5.0 規範

    ← 【必改】根據 FXX 模組的實際輸出格式修改此函式

    Args:
        output: 模組輸出

    Returns:
        驗證結果字典
    """
    checks = {
        'is_string': isinstance(output, str),
        'has_module_id': output.startswith('FXX:') or output.startswith('['),  # ← 改為 FXX
        'has_source': '[來源名稱]' in output or 'source: 來源名稱' in output,  # ← 改為實際來源
        'format_valid': False,
    }

    # v5.0 成功格式檢查 ← 【必改】根據 FXX 模組規範修改
    if output.startswith('FXX:'):
        checks['format_valid'] = (
            # 在此加入 FXX 模組的格式驗證條件
            # 例如: '[標籤1]' in output and '[標籤2]' in output
            True  # ← 暫時通過，請實作實際驗證邏輯
        )
    # 錯誤格式檢查
    elif output.startswith('['):
        checks['format_valid'] = (
            'FXX 錯誤:' in output and  # ← 改為 FXX
            'source: 來源名稱' in output  # ← 改為實際來源
        )

    checks['all_passed'] = all(checks.values())

    return checks


def print_test_header(category_name: str):
    """印出測試類別標題"""
    print(f"\n{'='*70}")
    print(f"  📋 {category_name}")
    print('='*70)


def print_test_result(result: Dict, index: int, total: int):
    """印出單一測試結果"""
    # 測試結果圖示 (PASS/FAIL)
    test_result_icon = '✅' if result['test_result'] == 'PASS' else '❌'

    # 實際狀態圖示 (success/error/failed/timeout)
    status_icons = {
        'success': '🟢',
        'error': '🔴',
        'failed': '🟡',
        'timeout': '⏱️'
    }
    status_icon = status_icons.get(result['actual_status'], '❓')

    print(f"\n[{index}/{total}] {test_result_icon} 測試日期: {result['date']}")
    print(f"      測試結果: {result['test_result']} (預期: {result['expected_status']}, 實際: {result['actual_status']} {status_icon})")
    print(f"      Exit Code: {result['exit_code']}")

    if result['error']:
        print(f"      錯誤: {result['error']}")
    elif result['output']:
        # 限制輸出長度 ← 【選改】可調整顯示長度
        output_preview = result['output'][:150]
        if len(result['output']) > 150:
            output_preview += '...'
        print(f"      輸出: {output_preview}")


def print_summary(all_results: List[Dict], start_time: datetime):
    """印出測試總結"""
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # 統計測試結果 (PASS/FAIL)
    total = len(all_results)
    pass_count = sum(1 for r in all_results if r['test_result'] == 'PASS')
    fail_count = sum(1 for r in all_results if r['test_result'] == 'FAIL')

    # 統計實際狀態 (success/error/failed/timeout)
    success_count = sum(1 for r in all_results if r['actual_status'] == 'success')
    error_count = sum(1 for r in all_results if r['actual_status'] == 'error')
    failed_count = sum(1 for r in all_results if r['actual_status'] == 'failed')
    timeout_count = sum(1 for r in all_results if r['actual_status'] == 'timeout')

    print(f"\n\n{'='*70}")
    print("  📊 測試總結")
    print('='*70)
    print(f"  開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  結束時間: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  執行時長: {duration:.2f} 秒")

    print(f"\n  【測試結果統計】")
    print(f"  總測試數: {total}")
    print(f"  ✅ PASS: {pass_count} ({pass_count/total*100:.1f}%)")
    print(f"  ❌ FAIL: {fail_count} ({fail_count/total*100:.1f}%)")

    print(f"\n  【實際狀態分佈】")
    print(f"  🟢 成功 (success): {success_count} ({success_count/total*100:.1f}%)")
    print(f"  🔴 錯誤 (error): {error_count} ({error_count/total*100:.1f}%)")
    print(f"  🟡 失敗 (failed): {failed_count} ({failed_count/total*100:.1f}%)")
    print(f"  ⏱️  逾時 (timeout): {timeout_count} ({timeout_count/total*100:.1f}%)")

    # 通過率（基於測試結果 PASS/FAIL）
    pass_rate = pass_count / total * 100 if total > 0 else 0
    if pass_rate == 100:
        print(f"\n  🎉 測試通過率: {pass_rate:.1f}% - 完美！")
    elif pass_rate >= 80:
        print(f"\n  👍 測試通過率: {pass_rate:.1f}% - 良好")
    elif pass_rate >= 60:
        print(f"\n  ⚠️  測試通過率: {pass_rate:.1f}% - 需要改進")
    else:
        print(f"\n  ❌ 測試通過率: {pass_rate:.1f}% - 存在嚴重問題")

    # 列出失敗項目（測試結果為 FAIL 的項目）
    failed_items = [r for r in all_results if r['test_result'] == 'FAIL']
    if failed_items:
        print(f"\n  ❌ 測試失敗項目詳細:")
        for item in failed_items:
            print(f"     - {item['date']}: 預期 {item['expected_status']}, 實際 {item['actual_status']}")
            if item['error']:
                print(f"       原因: {item['error']}")

    print('='*70)


# ==================== 主程式 ====================

def main():
    """主程式入口"""
    print("="*70)
    print("  🚀 FXX 模組自動化測試")  # ← 【必改】改為 FXX
    print("="*70)
    print(f"  模組路徑: {MODULE_PATH}")
    print(f"  測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    start_time = datetime.now()
    all_results = []

    # 執行所有測試類別
    for category_key, category_config in TEST_CASES.items():
        print_test_header(category_config['name'])

        dates = category_config['dates']
        expected_status = category_config['expect']  # 取得預期狀態
        total = len(dates)

        for index, date in enumerate(dates, 1):
            result = run_test(date, expected_status)  # 傳遞預期狀態
            all_results.append(result)
            print_test_result(result, index, total)

            # 如果是成功的測試，驗證輸出格式
            if result['actual_status'] == 'success' and result.get('actual_output'):
                format_checks = validate_output_format(result['actual_output'])
                if format_checks['all_passed']:
                    print(f"      ✅ 輸出格式驗證通過")
                else:
                    print(f"      ⚠️  輸出格式驗證失敗:")
                    for check_name, check_result in format_checks.items():
                        if not check_result and check_name != 'all_passed':
                            print(f"         - {check_name}: {check_result}")

    # 印出總結
    print_summary(all_results, start_time)

    # 根據結果決定 exit code（基於測試結果 PASS/FAIL）
    has_failures = any(r['test_result'] == 'FAIL' for r in all_results)
    sys.exit(1 if has_failures else 0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  測試被使用者中斷")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ 測試腳本發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
