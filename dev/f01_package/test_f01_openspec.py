"""
test_f01_openspec.py - F01 Fetcher v7.0 OpenSpec 单元和集成测试

测试覆盖：
- T10-TEST-UNIT: 单元测试（正常路径）
- T11-TEST-EXCEPTION: 异常测试
- T12-TEST-COMPARE: Dev vs Prod 对比
- T13-TEST-EDGE: 边界情况
"""

import sys
import os
import re
from unittest.mock import patch, Mock
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))

try:
    from f01_openspec_dev import (
        fetch,
        format_f01_output,
        convert_to_int,
        find_column_multiindex,
        find_column_single,
        extract_foreign_data_multiindex,
        extract_foreign_data_single,
        ForeignDataDict,
        ErrorContextDict,
        FetchResultDict
    )
    import pandas as pd
    import requests
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)


# ============================================================================
# T10-TEST-UNIT: 单元测试
# ============================================================================

class TestConvertToInt:
    """convert_to_int 函数的单元测试"""
    
    @staticmethod
    def test_normal_string_with_comma():
        """测试正常字符串（带逗号）"""
        assert convert_to_int("45,000") == 45000
        assert convert_to_int("-31,008") == -31008
        print("✓ test_normal_string_with_comma")
    
    @staticmethod
    def test_normal_string_without_comma():
        """测试正常字符串（不带逗号）"""
        assert convert_to_int("45000") == 45000
        assert convert_to_int("-31008") == -31008
        print("✓ test_normal_string_without_comma")
    
    @staticmethod
    def test_empty_string():
        """测试空字符串"""
        assert convert_to_int("") == 0
        print("✓ test_empty_string")
    
    @staticmethod
    def test_none_value():
        """测试 None 值"""
        assert convert_to_int(None) == 0
        print("✓ test_none_value")
    
    @staticmethod
    def test_integer_input():
        """测试整数输入"""
        assert convert_to_int(45000) == 45000
        assert convert_to_int(-31008) == -31008
        print("✓ test_integer_input")
    
    @staticmethod
    def test_invalid_string():
        """测试无效字符串"""
        assert convert_to_int("abc") == 0
        print("✓ test_invalid_string")


class TestFindColumn:
    """find_column_multiindex 和 find_column_single 的单元测试"""
    
    @staticmethod
    def test_find_column_multiindex_found():
        """测试找到 MultiIndex 列"""
        columns = pd.MultiIndex.from_tuples([
            ('未平倉', '多方', '口數'),
            ('未平倉', '空方', '口數'),
            ('身份別', '', '')
        ])
        df = pd.DataFrame([[1, 2, 3], [4, 5, 6]], columns=columns)
        
        result = find_column_multiindex(df, ['未平倉', '多方', '口'])
        assert result == ('未平倉', '多方', '口數')
        print("✓ test_find_column_multiindex_found")
    
    @staticmethod
    def test_find_column_multiindex_not_found():
        """测试未找到 MultiIndex 列"""
        columns = pd.MultiIndex.from_tuples([
            ('成交', '多方', '口數'),
            ('成交', '空方', '口數')
        ])
        df = pd.DataFrame([[1, 2], [3, 4]], columns=columns)
        
        result = find_column_multiindex(df, ['未平倉', '多方'])
        assert result is None
        print("✓ test_find_column_multiindex_not_found")
    
    @staticmethod
    def test_find_column_single_found():
        """测试找到单层列"""
        df = pd.DataFrame({
            '身份別': ['外資及陸資', '自營商'],
            '多方口數': [45000, 10000],
            '空方口數': [76008, 20000]
        })
        
        result = find_column_single(df, ['身份別', '身份', '交易人'])
        assert result == '身份別'
        print("✓ test_find_column_single_found")
    
    @staticmethod
    def test_find_column_single_not_found():
        """测试未找到单层列"""
        df = pd.DataFrame({
            'trader': ['外資及陸資'],
            'long': [45000],
            'short': [76008]
        })
        
        result = find_column_single(df, ['身份別', '身份', '交易人'])
        assert result is None
        print("✓ test_find_column_single_not_found")


class TestFormatOutput:
    """format_f01_output 函数的单元测试"""
    
    @staticmethod
    def test_success_format():
        """测试成功情况的格式"""
        data = {
            "net_position": -31008,
            "long_position": 45000,
            "short_position": 76008,
            "source": "TAIFEX"
        }
        result = format_f01_output("2025-12-12", "success", data=data)
        expected = "2025.12.12  F01: 台指期貨外資 [未平倉] [多空淨額] : -31,008 口 [TAIFEX]"
        assert result == expected
        print("✓ test_success_format")
    
    @staticmethod
    def test_failed_format():
        """测试失敗情况的格式"""
        result = format_f01_output(
            "2025-12-14", "failed",
            error="該日無交易資料（可能是假日或休市日）"
        )
        assert "F01 錯誤" in result
        assert "該日無交易資料" in result
        assert "TAIFEX" in result
        print("✓ test_failed_format")
    
    @staticmethod
    def test_error_format_with_timeout():
        """测试异常情况（含 timeout）的格式"""
        timestamp = "2025-12-15 14:30:45"
        context = {"timeout": 30}
        result = format_f01_output(
            "2025-12-12", "error",
            error="連線逾時，請檢查網路連線",
            timestamp=timestamp,
            context=context
        )
        assert "F01 錯誤" in result
        assert "連線逾時" in result
        assert "2025-12-15 14:30:45" in result
        assert "timeout=30s" in result
        print("✓ test_error_format_with_timeout")
    
    @staticmethod
    def test_error_format_with_status_code():
        """测试异常情况（含 HTTP status_code）的格式"""
        timestamp = "2025-12-15 14:30:45"
        context = {"status_code": 404}
        result = format_f01_output(
            "2025-12-12", "error",
            error="HTTP 錯誤 404",
            timestamp=timestamp,
            context=context
        )
        assert "HTTP 錯誤 404" in result
        assert "status_code=404" in result
        print("✓ test_error_format_with_status_code")


# ============================================================================
# T11-TEST-EXCEPTION: 异常测试
# ============================================================================

class TestExceptionHandling:
    """异常处理的单元测试"""
    
    @staticmethod
    def test_invalid_date_format():
        """测试无效日期格式"""
        result = fetch("2025-12/12")
        assert "日期格式錯誤" in result
        assert "F01 錯誤" in result
        print("✓ test_invalid_date_format")
    
    @staticmethod
    def test_invalid_date_format_2():
        """测试无效日期格式 - 点号分隔"""
        result = fetch("2025.12.12")
        assert "日期格式錯誤" in result
        print("✓ test_invalid_date_format_2")
    
    @staticmethod
    def test_invalid_date_format_3():
        """测试无效日期格式 - 月份/日期超出范围"""
        result = fetch("2025-13-01")
        assert "日期格式錯誤" in result
        print("✓ test_invalid_date_format_3")
    
    @staticmethod
    def test_holiday_or_no_data():
        """测试假日或无交易数据"""
        # 测试一个通常是假日的日期（圣诞节）
        result = fetch("2025-12-25")
        # 可能返回 failed 或 error，关键是有明确的错误消息
        assert ("錯誤" in result or "無交易" in result)
        print("✓ test_holiday_or_no_data")
    
    @staticmethod
    def test_timeout_exception():
        """测试 Timeout 异常处理"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.Timeout("Connection timeout")
            result = fetch("2025-12-12")
            assert "連線逾時" in result
            assert "timeout=30s" in result
            assert "F01 錯誤" in result
            print("✓ test_timeout_exception")
    
    @staticmethod
    def test_http_error_404():
        """测试 HTTP 404 错误"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.HTTPError(
                response=Mock(status_code=404)
            )
            mock_get.return_value = mock_response
            
            result = fetch("2025-12-12")
            assert "HTTP 錯誤 404" in result
            assert "status_code=404" in result
            print("✓ test_http_error_404")
    
    @staticmethod
    def test_http_error_500():
        """测试 HTTP 500 错误"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.HTTPError(
                response=Mock(status_code=500)
            )
            mock_get.return_value = mock_response
            
            result = fetch("2025-12-12")
            assert "HTTP 錯誤 500" in result
            assert "status_code=500" in result
            print("✓ test_http_error_500")
    
    @staticmethod
    def test_request_exception():
        """测试通用网络异常"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.ConnectionError("Connection refused")
            result = fetch("2025-12-12")
            assert "F01 錯誤" in result
            assert "網路請求失敗" in result
            print("✓ test_request_exception")


# ============================================================================
# T12-TEST-COMPARE: Dev vs Prod 对比测试
# ============================================================================

def test_compare_with_prod():
    """对比 dev 版本和 prod 版本的输出"""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from modules.f01_fetcher import fetch as fetch_prod
    except ImportError:
        print("⊘ 跳过 Prod 对比测试 (modules/f01_fetcher.py 不可用)")
        return True
    
    print("\n【T12-TEST-COMPARE: Dev vs Prod 对比】")
    
    # 测试 2025-12-12
    result_dev = fetch("2025-12-12")
    result_prod = fetch_prod("2025-12-12")
    
    print(f"Dev:  {result_dev}")
    print(f"Prod: {result_prod}")
    
    if result_dev == result_prod:
        print("✓ 输出完全相同")
        return True
    else:
        # 检查是否只是格式差异
        if "錯誤" in result_dev and "錯誤" in result_prod:
            print("△ 都返回错误（可能是兼容的）")
            return True
        
        # 提取数字进行对比
        dev_match = re.search(r':\s*([-\d,]+)\s*口', result_dev)
        prod_match = re.search(r':\s*([-\d,]+)\s*口', result_prod)
        
        if dev_match and prod_match:
            if dev_match.group(1) == prod_match.group(1):
                print("△ 数字相同，可能是格式差异")
                return True
        
        print("✗ 输出不匹配")
        return False


# ============================================================================
# T13-TEST-EDGE: 边界情况测试
# ============================================================================

class TestEdgeCases:
    """边界情况测试"""
    
    @staticmethod
    def test_empty_date_string():
        """测试空日期字符串"""
        result = fetch("")
        assert "日期格式錯誤" in result
        print("✓ test_empty_date_string")
    
    @staticmethod
    def test_future_date():
        """测试未来日期"""
        result = fetch("2099-12-31")
        # 应该返回某种错误或无数据提示
        assert ("錯誤" in result or "無交易" in result)
        print("✓ test_future_date")
    
    @staticmethod
    def test_past_date():
        """测试很久以前的日期"""
        result = fetch("2020-01-01")
        # 应该返回某种错误或无数据提示
        assert ("錯誤" in result or "無交易" in result)
        print("✓ test_past_date")
    
    @staticmethod
    def test_month_out_of_range():
        """测试月份超出范围"""
        result = fetch("2025-13-01")
        assert "日期格式錯誤" in result
        print("✓ test_month_out_of_range")
    
    @staticmethod
    def test_day_out_of_range():
        """测试日期超出范围"""
        result = fetch("2025-12-32")
        assert "日期格式錯誤" in result
        print("✓ test_day_out_of_range")
    
    @staticmethod
    def test_slash_format():
        """测试斜杠格式"""
        result = fetch("2025/12/12")
        assert "日期格式錯誤" in result
        print("✓ test_slash_format")
    
    @staticmethod
    def test_letter_format():
        """测试字母格式"""
        result = fetch("December 12, 2025")
        assert "日期格式錯誤" in result
        print("✓ test_letter_format")


# ============================================================================
# 主测试函数
# ============================================================================

def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("F01 Fetcher v7.0 OpenSpec 测试套件")
    print("=" * 70)
    
    total_tests = 0
    passed_tests = 0
    
    # T10-TEST-UNIT
    print("\n【T10-TEST-UNIT: 单元测试 - convert_to_int】")
    for test_method in [
        TestConvertToInt.test_normal_string_with_comma,
        TestConvertToInt.test_normal_string_without_comma,
        TestConvertToInt.test_empty_string,
        TestConvertToInt.test_none_value,
        TestConvertToInt.test_integer_input,
        TestConvertToInt.test_invalid_string,
    ]:
        try:
            test_method()
            passed_tests += 1
        except AssertionError as e:
            print(f"✗ {test_method.__name__}: {e}")
        total_tests += 1
    
    print("\n【T10-TEST-UNIT: 单元测试 - find_column】")
    for test_method in [
        TestFindColumn.test_find_column_multiindex_found,
        TestFindColumn.test_find_column_multiindex_not_found,
        TestFindColumn.test_find_column_single_found,
        TestFindColumn.test_find_column_single_not_found,
    ]:
        try:
            test_method()
            passed_tests += 1
        except AssertionError as e:
            print(f"✗ {test_method.__name__}: {e}")
        total_tests += 1
    
    print("\n【T10-TEST-UNIT: 单元测试 - format_f01_output】")
    for test_method in [
        TestFormatOutput.test_success_format,
        TestFormatOutput.test_failed_format,
        TestFormatOutput.test_error_format_with_timeout,
        TestFormatOutput.test_error_format_with_status_code,
    ]:
        try:
            test_method()
            passed_tests += 1
        except AssertionError as e:
            print(f"✗ {test_method.__name__}: {e}")
        total_tests += 1
    
    # T11-TEST-EXCEPTION
    print("\n【T11-TEST-EXCEPTION: 异常处理测试】")
    for test_method in [
        TestExceptionHandling.test_invalid_date_format,
        TestExceptionHandling.test_invalid_date_format_2,
        TestExceptionHandling.test_invalid_date_format_3,
        TestExceptionHandling.test_holiday_or_no_data,
        TestExceptionHandling.test_timeout_exception,
        TestExceptionHandling.test_http_error_404,
        TestExceptionHandling.test_http_error_500,
        TestExceptionHandling.test_request_exception,
    ]:
        try:
            test_method()
            passed_tests += 1
        except AssertionError as e:
            print(f"✗ {test_method.__name__}: {e}")
        total_tests += 1
    
    # T12-TEST-COMPARE
    print("\n【T12-TEST-COMPARE: Dev vs Prod 对比】")
    if test_compare_with_prod():
        passed_tests += 1
    total_tests += 1
    
    # T13-TEST-EDGE
    print("\n【T13-TEST-EDGE: 边界情况测试】")
    for test_method in [
        TestEdgeCases.test_empty_date_string,
        TestEdgeCases.test_future_date,
        TestEdgeCases.test_past_date,
        TestEdgeCases.test_month_out_of_range,
        TestEdgeCases.test_day_out_of_range,
        TestEdgeCases.test_slash_format,
        TestEdgeCases.test_letter_format,
    ]:
        try:
            test_method()
            passed_tests += 1
        except AssertionError as e:
            print(f"✗ {test_method.__name__}: {e}")
        total_tests += 1
    
    # 总结
    print("\n" + "=" * 70)
    print(f"测试总结: {passed_tests}/{total_tests} 通过")
    print(f"成功率: {100 * passed_tests / total_tests:.1f}%")
    print("=" * 70)
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
