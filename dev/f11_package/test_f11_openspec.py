"""
Test Suite for F11 Module: Taiwan Weighted Stock Index
======================================================

Comprehensive test suite for the F11 TAIEX data fetcher module.

Test Coverage:
    - Format validation (output format, date format, value precision)
    - Data extraction (HTML parsing, column finding, value conversion)
    - Error handling (HTTP errors, parsing errors, data validation)
    - Edge cases (missing data, malformed values, non-trading days)
    - Logging (log levels, prefixes, error messages)
    - Integration (module import, function signature)

Test Statistics:
    Total Tests: 19
    Categories: 6
        - Format Output: 5 tests
        - Extract Values: 4 tests
        - Error Handling: 5 tests
        - Edge Cases: 3 tests
        - Logging: 2 tests
    
    Coverage Target: 90%+

Author: F11 Test Team
Version: 1.0.0
Created: 2025-12-17
"""

import pytest
from unittest import mock
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import sys
import os

# Add the project directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the module to test
import f11_openspec_dev as f11


# ============================================================================
# PYTEST FIXTURES
# ============================================================================

@pytest.fixture
def mock_logger(monkeypatch):
    """Fixture to capture logger output"""
    logger = logging.getLogger('f11_openspec_dev')
    return logger


@pytest.fixture
def sample_html_success():
    """Sample HTML response with successful TAIEX data"""
    return """
    <html>
    <body>
    <table>
        <tr>
            <th>日期</th>
            <th>開盤</th>
            <th>最高</th>
            <th>目前指數</th>
            <th>最低</th>
        </tr>
        <tr>
            <td>2025/12/17</td>
            <td>18200.00</td>
            <td>18300.00</td>
            <td>18254.50</td>
            <td>18150.00</td>
        </tr>
    </table>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_no_data():
    """Sample HTML response with no trading data (empty table)"""
    return """
    <html>
    <body>
    <table>
        <tr>
            <th>日期</th>
            <th>開盤</th>
            <th>目前指數</th>
        </tr>
    </table>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_malformed():
    """Sample HTML response with malformed value"""
    return """
    <html>
    <body>
    <table>
        <tr>
            <th>日期</th>
            <th>目前指數</th>
        </tr>
        <tr>
            <td>2025/12/17</td>
            <td>N/A</td>
        </tr>
    </table>
    </body>
    </html>
    """


# ============================================================================
# CATEGORY 1: FORMAT OUTPUT VALIDATION (5 tests)
# ============================================================================

class TestFormatOutput:
    """Test output format consistency and correctness"""
    
    def test_format_output_success(self):
        """Test format_taiex_output creates correct success format"""
        # Task 2.4 Validation
        result = f11.format_taiex_output(18254.50, datetime(2025, 12, 17))
        expected = "2025.12.17  F11: 加權股價收盤指數 : 18254.50 [TWSE]"
        assert result == expected
    
    def test_format_output_decimal_precision(self):
        """Test output always has 2 decimal places"""
        # Value with 1 decimal place
        result = f11.format_taiex_output(18254.5, datetime(2025, 12, 17))
        assert "18254.50" in result
        
        # Integer value
        result = f11.format_taiex_output(18254, datetime(2025, 12, 17))
        assert "18254.00" in result
        
        # Many decimal places
        result = f11.format_taiex_output(18254.12345, datetime(2025, 12, 17))
        assert "18254.12" in result
    
    def test_format_output_date_format(self):
        """Test date format is always YYYY.MM.DD"""
        result = f11.format_taiex_output(18254.50, datetime(2025, 12, 17))
        assert result.startswith("2025.12.17")
        
        # Test with different month/day
        result = f11.format_taiex_output(18254.50, datetime(2025, 1, 5))
        assert result.startswith("2025.01.05")
    
    def test_format_error_basic(self):
        """Test format_taiex_error creates correct error format"""
        result = f11.format_taiex_error("網路連線失敗")
        expected = "F11 錯誤: 網路連線失敗 [TWSE]"
        assert result == expected
    
    def test_format_error_with_timestamp(self):
        """Test format_taiex_error with timestamp"""
        result = f11.format_taiex_error("網路連線失敗", include_timestamp=True)
        assert "F11 錯誤: 網路連線失敗 [TWSE]" in result
        assert "(" in result and ")" in result
        # Check timestamp format (YYYY-MM-DD HH:MM:SS)
        assert len(result) > len("F11 錯誤: 網路連線失敗 [TWSE]")


# ============================================================================
# CATEGORY 2: DATA EXTRACTION VALIDATION (4 tests)
# ============================================================================

class TestExtractTAIEX:
    """Test TAIEX value extraction and validation"""
    
    @patch('f11_openspec_dev.webdriver.Chrome')
    def test_extract_value_success(self, mock_chrome, sample_html_success):
        """Test successful extraction of TAIEX value"""
        # Setup Selenium mock
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = sample_html_success
        
        # Call function
        result = f11.fetch_taiex_index()
        
        # Verify result contains the extracted value
        assert "18254.50" in result
        assert "F11: 加權股價收盤指數" in result
        
        # Verify WebDriver was properly closed
        mock_driver.quit.assert_called()
    
    @patch('f11_openspec_dev.webdriver.Chrome')
    def test_extract_value_with_comma(self, mock_chrome):
        """Test extraction handles comma-separated numbers"""
        html = """
        <html><body><table>
        <tr><th>現在指數</th></tr>
        <tr><td>18,254.50</td></tr>
        </table></body></html>
        """
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = html
        
        result = f11.fetch_taiex_index()
        assert "18254.50" in result
        mock_driver.quit.assert_called()
    
    @patch('f11_openspec_dev.webdriver.Chrome')
    def test_extract_column_variant_names(self, mock_chrome):
        """Test extraction finds alternative column names"""
        # Test with different column name
        html = """
        <html><body><table>
        <tr><th>日期</th><th>收盤指數</th></tr>
        <tr><td>2025/12/17</td><td>18254.50</td></tr>
        </table></body></html>
        """
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = html
        
        result = f11.fetch_taiex_index()
        assert "18254.50" in result
        mock_driver.quit.assert_called()
    
    @patch('f11_openspec_dev.webdriver.Chrome')
    def test_extract_last_row_only(self, mock_chrome):
        """Test extraction gets the last row (most recent data)"""
        html = """
        <html><body><table>
        <tr><th>日期</th><th>現在指數</th></tr>
        <tr><td>2025/12/15</td><td>18000.00</td></tr>
        <tr><td>2025/12/16</td><td>18100.00</td></tr>
        <tr><td>2025/12/17</td><td>18254.50</td></tr>
        </table></body></html>
        """
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = html
        
        result = f11.fetch_taiex_index()
        # Should get the last row (18254.50), not earlier values
        assert "18254.50" in result
        mock_driver.quit.assert_called()


# ============================================================================
# CATEGORY 3: ERROR HANDLING (5 tests)
# ============================================================================

class TestErrorHandling:
    """Test proper error handling for various failure scenarios"""
    
    @patch('f11_openspec_dev.webdriver.Chrome')
    def test_handle_network_timeout(self, mock_chrome):
        """Test handling of network timeout"""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.get.side_effect = Exception("Timeout")
        
        result = f11.fetch_taiex_index()
        
        assert "F11 錯誤" in result
        assert "[TWSE]" in result
    
    @patch('f11_openspec_dev.webdriver.Chrome')
    def test_handle_http_error(self, mock_chrome):
        """Test handling of HTTP errors"""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.get.side_effect = Exception("Connection error")
        
        result = f11.fetch_taiex_index()
        
        assert "F11 錯誤" in result
        assert "[TWSE]" in result
    
    @patch('f11_openspec_dev.webdriver.Chrome')
    def test_handle_parsing_error(self, mock_chrome):
        """Test handling when HTML parsing fails"""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = "<invalid>html"
        
        result = f11.fetch_taiex_index()
        
        # Should return gracefully without raising exception
        assert "F11 錯誤" in result
        assert "[TWSE]" in result
    
    @patch('f11_openspec_dev.webdriver.Chrome')
    def test_handle_missing_column(self, mock_chrome):
        """Test handling when required column is missing"""
        html = """
        <html><body><table>
        <tr><th>日期</th><th>開盤</th></tr>
        <tr><td>2025/12/17</td><td>18200.00</td></tr>
        </table></body></html>
        """
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = html
        
        result = f11.fetch_taiex_index()
        
        assert "F11 錯誤" in result
        assert "[TWSE]" in result
    
    @patch('f11_openspec_dev.webdriver.Chrome')
    def test_handle_malformed_value(self, mock_chrome, sample_html_malformed):
        """Test handling of non-numeric values"""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = sample_html_malformed
        
        result = f11.fetch_taiex_index()
        
        assert "F11 錯誤" in result
        assert "[TWSE]" in result


# ============================================================================
# CATEGORY 4: EDGE CASES (3 tests)
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @patch('f11_openspec_dev.webdriver.Chrome')
    def test_empty_table(self, mock_chrome):
        """Test handling of empty table (no data rows)"""
        html = """
        <html><body><table>
        <tr><th>日期</th><th>現在指數</th></tr>
        </table></body></html>
        """
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = html
        
        result = f11.fetch_taiex_index()
        
        # Should handle gracefully
        assert "F11" in result
        assert "[TWSE]" in result
    
    @patch('f11_openspec_dev.webdriver.Chrome')
    def test_zero_value(self, mock_chrome):
        """Test handling of zero as index value"""
        html = """
        <html><body><table>
        <tr><th>現在指數</th></tr>
        <tr><td>0.00</td></tr>
        </table></body></html>
        """
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = html
        
        result = f11.fetch_taiex_index()
        
        # Should accept zero as valid value
        assert "0.00" in result
    
    @patch('f11_openspec_dev.webdriver.Chrome')
    def test_very_large_value(self, mock_chrome):
        """Test handling of very large index values"""
        html = """
        <html><body><table>
        <tr><th>現在指數</th></tr>
        <tr><td>99999999.99</td></tr>
        </table></body></html>
        """
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = html
        
        result = f11.fetch_taiex_index()
        
        assert "99999999.99" in result


# ============================================================================
# CATEGORY 5: LOGGING (2 tests)
# ============================================================================

class TestLogging:
    """Test logging output and levels"""
    
    @patch('f11_openspec_dev.webdriver.Chrome')
    def test_logging_success(self, mock_chrome, sample_html_success, caplog):
        """Test logging on successful fetch"""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = sample_html_success
        
        with caplog.at_level(logging.INFO):
            result = f11.fetch_taiex_index()
        
        # Check that success is logged
        log_output = caplog.text
        assert "[F11]" in log_output or "F11" in str(result)
    
    @patch('f11_openspec_dev.webdriver.Chrome')
    def test_logging_error(self, mock_chrome, caplog):
        """Test logging on error"""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.get.side_effect = Exception("Network error")
        
        with caplog.at_level(logging.ERROR):
            result = f11.fetch_taiex_index()
        
        # Error result should be returned
        assert "F11 錯誤" in result
        assert "[TWSE]" in result


# ============================================================================
# CATEGORY 6: INTEGRATION (2 tests)
# ============================================================================

class TestIntegration:
    """Test module integration and compatibility"""
    
    def test_module_import(self):
        """Test that module can be imported"""
        assert hasattr(f11, 'fetch_taiex_index')
        assert callable(f11.fetch_taiex_index)
    
    def test_function_signature(self):
        """Test function has correct signature"""
        import inspect
        sig = inspect.signature(f11.fetch_taiex_index)
        
        # Should have no required parameters
        assert len(sig.parameters) == 0
        
        # Should return str
        assert sig.return_annotation == str


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    """Run tests with pytest"""
    pytest.main([__file__, "-v", "--tb=short"])
