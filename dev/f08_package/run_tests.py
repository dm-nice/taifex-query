"""
簡化的測試執行腳本
避免 pytest 的 UTF-8 包裝衝突
"""

import sys
import os

# 添加模組路徑
sys.path.insert(0, os.path.dirname(__file__))

# 暫時移除 UTF-8 包裝以避免測試衝突
if hasattr(sys.stdout, '_wrapped_for_utf8'):
    delattr(sys.stdout, '_wrapped_for_utf8')
if hasattr(sys.stderr, '_wrapped_for_utf8'):
    delattr(sys.stderr, '_wrapped_for_utf8')

# 執行 pytest
import pytest

if __name__ == '__main__':
    exit_code = pytest.main([
        'test_f08_openspec.py',
        '-v',
        '--tb=short',
        '-p', 'no:cacheprovider'
    ])
    sys.exit(exit_code)
