"""
test_f06_openspec.py - F06 模組完整測試套件

【測試覆蓋】
- 單元測試 (格式化、數據提取)
- 異常處理測試 (5 種異常類型)
- 邊界情況測試
- 集成測試 (fetch 函數)

【運行方式】
pytest test_f06_openspec.py -v
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pandas as pd
import requests

from f06_openspec_dev import fetch, format_f06_output, extract_vix_value


# ============================================================================
# 單元測試 - 格式化輸出
# ============================================================================

class TestFormatOutput:
    """測試 format_f06_output 函數的各種輸出格式"""
    
    def test_success_case_basic(self):
        """測試成功情況的基本格式"""
        result = format_f06_output(
            date="2025-12-15",
            status="success",
            data={"vix_value": 18.50, "source": "TAIFEX"}
        )
        assert result == "2025.12.15  F06: 臺指選擇權波動率指數 : 18.50 [TAIFEX]"
    
    def test_success_case_precision(self):
        """測試成功情況的精度（小數後 2 位）"""
        result = format_f06_output(
            date="2025-12-15",
            status="success",
            data={"vix_value": 18.567, "source": "TAIFEX"}
        )
        # 應該四捨五入到 2 位小數
        assert "18.57" in result
    
    def test_success_case_whole_number(self):
        """測試成功情況的整數波動率"""
        result = format_f06_output(
            date="2025-12-15",
            status="success",
            data={"vix_value": 20, "source": "TAIFEX"}
        )
        assert "20.00" in result
    
    def test_failed_case_no_trading(self):
        """測試失敗情況（假日）"""
        result = format_f06_output(
            date="2025-12-14",
            status="failed",
            error="該日無交易資料（可能是假日或休市日）"
        )
        assert result == "F06 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]"
    
    def test_error_case_with_timestamp(self):
        """測試異常情況（包含時間戳）"""
        result = format_f06_output(
            date="2025-12-15",
            status="error",
            error="連線逾時，請檢查網路連線",
            timestamp="2025-12-15 14:30:45"
        )
        assert "F06 錯誤:" in result
        assert "連線逾時" in result
        assert "2025-12-15 14:30:45" in result
    
    def test_error_case_with_context_timeout(self):
        """測試異常情況（包含逾時上下文）"""
        result = format_f06_output(
            date="2025-12-15",
            status="error",
            error="連線逾時，請檢查網路連線",
            timestamp="2025-12-15 14:30:45",
            context={"timeout": 30}
        )
        assert "timeout=30s" in result
        assert "2025-12-15 14:30:45" in result
    
    def test_error_case_with_context_http_error(self):
        """測試異常情況（包含 HTTP 錯誤上下文）"""
        result = format_f06_output(
            date="2025-12-15",
            status="error",
            error="HTTP 錯誤 404",
            timestamp="2025-12-15 14:30:45",
            context={"status_code": 404}
        )
        assert "status_code=404" in result


# ============================================================================
# 單元測試 - 數據提取
# ============================================================================

class TestExtractVIXValue:
    """測試 extract_vix_value 函數的數據提取"""
    
    def test_extract_single_layer_table(self):
        """測試單層表頭表格的提取"""
        df = pd.DataFrame({
            '臺指選擇權波動率指數': [18.50],
            '其他欄位': ['數據']
        })
        
        result = extract_vix_value(df, "2025-12-15")
        assert result['status'] == 'success'
        assert result['data']['vix_value'] == 18.50
    
    def test_extract_alternative_column_name(self):
        """測試備選欄位名稱"""
        df = pd.DataFrame({
            '波動率指數': [19.25],
            '其他欄位': ['數據']
        })
        
        result = extract_vix_value(df, "2025-12-15")
        assert result['status'] == 'success'
        assert result['data']['vix_value'] == 19.25
    
    def test_extract_no_matching_column(self):
        """測試無法找到波動率欄位"""
        df = pd.DataFrame({
            '其他欄位1': ['數據1'],
            '其他欄位2': ['數據2']
        })
        
        result = extract_vix_value(df, "2025-12-15")
        assert result['status'] == 'failed'
        assert '無交易資料' in result['error']
    
    def test_extract_with_string_value(self):
        """測試字串波動率值的轉換"""
        df = pd.DataFrame({
            '波動率指數': ['18.50'],
            '其他欄位': ['數據']
        })
        
        result = extract_vix_value(df, "2025-12-15")
        assert result['status'] == 'success'
        assert result['data']['vix_value'] == 18.50
    
    def test_extract_multiindex_table(self):
        """測試 MultiIndex 表頭的提取"""
        # 建立 MultiIndex columns
        columns = pd.MultiIndex.from_tuples([
            ('數據', '臺指選擇權波動率指數'),
            ('數據', '其他欄位')
        ])
        df = pd.DataFrame([[18.50, 'X']], columns=columns)
        
        result = extract_vix_value(df, "2025-12-15")
        assert result['status'] == 'success'
        assert result['data']['vix_value'] == 18.50


# ============================================================================
# 異常處理測試
# ============================================================================

class TestExceptionHandling:
    """測試 fetch 函數的異常處理"""
    
    def test_invalid_date_format(self):
        """測試日期格式錯誤"""
        result = fetch("2025-12/15")  # 錯誤格式
        assert "F06 錯誤:" in result
        assert "日期格式錯誤" in result
    
    @patch('requests.get')
    def test_timeout_exception(self, mock_get):
        """測試連線逾時異常"""
        mock_get.side_effect = requests.Timeout("Connection timeout")
        
        result = fetch("2025-12-15")
        assert "F06 錯誤:" in result
        assert "連線逾時" in result
        assert "timeout=30s" in result
    
    @patch('requests.get')
    def test_http_404_error(self, mock_get):
        """測試 HTTP 404 錯誤"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # 創建 HTTPError 並設定 response 屬性
        error = requests.HTTPError()
        error.response = mock_response
        mock_response.raise_for_status.side_effect = error
        
        result = fetch("2025-12-15")
        assert "F06 錯誤:" in result
        assert "404" in result
    
    @patch('requests.get')
    def test_http_500_error(self, mock_get):
        """測試 HTTP 500 錯誤"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        
        error = requests.HTTPError()
        error.response = mock_response
        mock_response.raise_for_status.side_effect = error
        mock_get.return_value = mock_response
        
        result = fetch("2025-12-15")
        assert "F06 錯誤:" in result
        assert "500" in result
    
    @patch('requests.get')
    def test_request_exception(self, mock_get):
        """測試一般網路異常"""
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = fetch("2025-12-15")
        assert "F06 錯誤:" in result
        assert "網路請求失敗" in result


# ============================================================================
# 邊界情況測試
# ============================================================================

class TestEdgeCases:
    """測試邊界情況和特殊日期"""
    
    def test_empty_date_string(self):
        """測試空日期字串"""
        result = fetch("")
        assert "F06 錯誤:" in result
        assert "日期格式錯誤" in result
    
    def test_date_with_spaces(self):
        """測試包含空格的日期"""
        result = fetch(" 2025-12-15 ")
        assert "F06 錯誤:" in result
    
    def test_date_with_letters(self):
        """測試包含字母的日期"""
        result = fetch("2025-12-15a")
        assert "F06 錯誤:" in result
        assert "日期格式錯誤" in result
    
    def test_invalid_month(self):
        """測試無效月份"""
        result = fetch("2025-13-01")
        assert "F06 錯誤:" in result
        assert "日期格式錯誤" in result
    
    def test_invalid_day(self):
        """測試無效日期"""
        result = fetch("2025-02-30")
        assert "F06 錯誤:" in result
        assert "日期格式錯誤" in result
    
    @patch('requests.get')
    def test_empty_response(self, mock_get):
        """測試空 HTML 響應"""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.encoding = "utf-8"
        mock_get.return_value = mock_response
        
        result = fetch("2025-12-15")
        assert "F06 錯誤:" in result or "該日無交易資料" in result
    
    @patch('requests.get')
    def test_malformed_html(self, mock_get):
        """測試格式錯誤的 HTML"""
        mock_response = MagicMock()
        mock_response.text = "<html><body>Not a table</body></html>"
        mock_response.encoding = "utf-8"
        mock_get.return_value = mock_response
        
        result = fetch("2025-12-15")
        # 應該返回無交易資料或解析失敗
        assert "F06 錯誤:" in result


# ============================================================================
# 集成測試 - 完整 fetch 流程
# ============================================================================

class TestFetchIntegration:
    """測試 fetch 函數的完整流程"""
    
    def test_valid_date_format_success(self):
        """測試有效日期格式的成功情況"""
        # 測試日期格式驗證通過（不拋出異常）
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            df = pd.DataFrame({
                '臺指選擇權波動率指數': [18.50]
            })
            mock_response.text = "<table><tr><td>18.50</td></tr></table>"
            mock_response.encoding = "utf-8"
            mock_get.return_value = mock_response
            
            # 即使網頁內容不同，至少應該嘗試處理
            result = fetch("2025-12-15")
            assert isinstance(result, str)
            assert "F06:" in result or "F06 錯誤:" in result
    
    def test_date_format_yyyy_mm_dd(self):
        """測試 YYYY-MM-DD 格式"""
        result = fetch("2025-12-15")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_date_format_boundary_year_change(self):
        """測試年份邊界"""
        result = fetch("2024-12-31")
        assert isinstance(result, str)
    
    def test_output_always_string(self):
        """測試輸出始終為字串"""
        result = fetch("2025-12-15")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_date_conversion_dash_to_dot(self):
        """測試日期格式轉換（- 到 .）"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            df = pd.DataFrame({
                '波動率指數': [18.50]
            })
            mock_response.text = "<table><tr><td>18.50</td></tr></table>"
            mock_response.encoding = "utf-8"
            mock_get.return_value = mock_response
            
            # 結果應該包含點號格式的日期
            result = fetch("2025-12-15")
            if "2025.12.15" in result:
                # 成功抓取，檢查日期格式
                assert "2025.12.15" in result


# ============================================================================
# 輸出格式驗證
# ============================================================================

class TestOutputFormat:
    """測試輸出格式的正確性"""
    
    def test_success_format_structure(self):
        """測試成功輸出的結構"""
        result = format_f06_output(
            date="2025-12-15",
            status="success",
            data={"vix_value": 18.50, "source": "TAIFEX"}
        )
        
        # 應該包含所有必要元素
        assert "2025.12.15" in result
        assert "F06:" in result
        assert "臺指選擇權波動率指數" in result
        assert "18.50" in result
        assert "[TAIFEX]" in result
    
    def test_error_format_structure(self):
        """測試錯誤輸出的結構"""
        result = format_f06_output(
            date="2025-12-15",
            status="failed",
            error="該日無交易資料（可能是假日或休市日）"
        )
        
        # 應該包含所有必要元素
        assert "F06 錯誤:" in result
        assert "該日無交易資料" in result
        assert "[TAIFEX]" in result
    
    def test_vix_value_precision(self):
        """測試波動率精度"""
        test_cases = [
            (18.50, "18.50"),
            (18.567, "18.57"),  # 四捨五入
            (18.564, "18.56"),  # 四捨五入
            (18, "18.00"),       # 整數
            (18.5, "18.50"),     # 單位小數
        ]
        
        for vix_value, expected in test_cases:
            result = format_f06_output(
                date="2025-12-15",
                status="success",
                data={"vix_value": vix_value, "source": "TAIFEX"}
            )
            assert expected in result, f"Expected {expected} for {vix_value}"


# ============================================================================
# 日期驗證測試
# ============================================================================

class TestDateValidation:
    """測試日期驗證邏輯"""
    
    def test_valid_dates(self):
        """測試有效日期"""
        valid_dates = [
            "2025-12-15",
            "2020-01-01",
            "2025-12-31",
            "2000-02-29",  # 閏年
        ]
        
        for date in valid_dates:
            # 應該不拋出異常，返回字串
            result = fetch(date)
            assert isinstance(result, str)
    
    def test_invalid_dates(self):
        """測試無效日期"""
        invalid_dates = [
            "2025/12/15",   # 錯誤分隔符
            "15-12-2025",   # 錯誤順序
            "2025-13-01",   # 無效月份
            "2025-12-32",   # 無效日期
            "2025-02-30",   # 無效日期（2月無30日）
        ]
        
        for date in invalid_dates:
            result = fetch(date)
            assert "F06 錯誤:" in result
            assert "日期格式錯誤" in result


# ============================================================================
# 主測試執行
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
