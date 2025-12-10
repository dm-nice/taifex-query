"""
F02 模組自動化測試腳本
========================
"""

import sys
import io
import subprocess
from datetime import datetime
from typing import Dict, List
from pathlib import Path

# 設定 UTF-8 輸出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ==================== 測試配置 ====================

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # C:\Taifex
MODULE_PATH = SCRIPT_DIR / 'f02_fetcher.py'  # 指向同目錄下的 f02_fetcher.py

# ==================== 測試案例配置 ====================

TEST_CASES = {
    'normal_dates': {
        'name': '正常交易日測試',
        'dates': [
            '2025-12-04',
            '2025-11-28',
        ],
        'expect': 'success',
    },
    'weekend_dates': {
        'name': '週末/假日測試',
        'dates': [
            '2025-12-07',  # 週六
            '2025-12-08',  # 週日
        ],
        'expect': 'may_fail',
    },
    'invalid_formats': {
        'name': '錯誤日期格式測試',
        'dates': [
            '20251204',
            'invalid',
        ],
        'expect': 'error',
    },
}

# ==================== 測試函式 (Modified from template) ====================

def run_test(date: str, expected_status: str = 'success') -> Dict:
    try:
        result = subprocess.run(
            ['python', str(MODULE_PATH), date],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )

        output = result.stdout.strip()
        exit_code = result.returncode

        output_lines = output.split('\n')
        actual_output = output_lines[-1] if output_lines else ''

        if exit_code == 0 and '錯誤:' not in actual_output:
            actual_status = 'success'
        elif '錯誤:' in actual_output:
            actual_status = 'error'
        else:
            actual_status = 'failed'

        test_result = evaluate_test_result(actual_status, expected_status)

        return {
            'date': date,
            'actual_status': actual_status,
            'expected_status': expected_status,
            'test_result': test_result,
            'exit_code': exit_code,
            'output': output,
            'actual_output': actual_output,
            'error': None
        }

    except Exception as e:
        return {
            'date': date,
            'actual_status': 'error',
            'expected_status': expected_status,
            'test_result': 'FAIL',
            'exit_code': -1,
            'output': '',
            'actual_output': '',
            'error': f'錯誤: {str(e)}'
        }

def evaluate_test_result(actual_status: str, expected_status: str) -> str:
    if expected_status == 'success':
        return 'PASS' if actual_status == 'success' else 'FAIL'
    elif expected_status == 'error':
        return 'PASS' if actual_status == 'error' else 'FAIL'
    elif expected_status == 'may_fail':
        return 'PASS' if actual_status in ['success', 'error'] else 'FAIL'
    return 'FAIL'

def validate_output_format(output: str) -> Dict:
    checks = {
        'is_string': isinstance(output, str),
        'has_module_id': output.startswith('F02:'),
        'has_source': '[TAIFEX]' in output,
        'format_valid': False,
    }

    if output.startswith('F02:'):
        checks['format_valid'] = (
            '[未平倉]' in output and 
            '[多方]' in output and
            '口' in output
        )
    elif '錯誤:' in output:
         checks['format_valid'] = 'F02 錯誤:' in output

    checks['all_passed'] = all(checks.values())
    return checks

def main():
    print("="*70)
    print("  🚀 F02 模組自動化測試")
    print("="*70)
    
    all_results = []
    
    for category_key, category_config in TEST_CASES.items():
        print(f"\n  📋 {category_config['name']}")
        
        for date in category_config['dates']:
            result = run_test(date, category_config['expect'])
            all_results.append(result)
            
            icon = '✅' if result['test_result'] == 'PASS' else '❌'
            print(f"  {icon} {date}: {result['actual_status']} (Expected: {result['expected_status']})")
            if result['actual_status'] == 'success':
                print(f"     Output: {result['actual_output']}")
                format_check = validate_output_format(result['actual_output'])
                if not format_check['all_passed']:
                    print(f"     ⚠️ Format Error: {format_check}")

    # Summary
    pass_count = sum(1 for r in all_results if r['test_result'] == 'PASS')
    total = len(all_results)
    print(f"\n  📊 Result: {pass_count}/{total} Passed")
    
    sys.exit(1 if pass_count < total else 0)

if __name__ == '__main__':
    main()
