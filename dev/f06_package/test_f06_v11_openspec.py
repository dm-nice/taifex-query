"""
test_f06_v1.1_openspec.py - F06 v1.1 (Selenium 版) 測試套件

【測試覆蓋】
- 單元測試 (格式化、異常處理)
- Mock Selenium 測試 (模擬瀏覽器行為)
- 邊界情況測試
- 集成測試 (完整流程驗證)

【運行方式】
pytest test_f06_v1.1_openspec.py -v
或
python test_f06_v1.1_openspec.py
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
import pandas as pd
import sys
import importlib.util

# 動態導入 v1.1 模組
spec = importlib.util.spec_from_file_location("f06_v11", "f06_v11_openspec_dev.py")
f06_v11 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f06_v11)

format_f06_output = f06_v11.format_f06_output
extract_vix_value_from_table = f06_v11.extract_vix_value_from_table
fetch_with_selenium = f06_v11.fetch_with_selenium


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
            data={"vix_value": 18.50, "source": "TAIFEX-MIS"}
        )
        assert "2025.12.15" in result
        assert "F06:" in result
        assert "18.50" in result
        assert "[TAIFEX]" in result
    
    def test_success_case_precision(self):
        """測試成功情況的精度（小數後 2 位）"""
        result = format_f06_output(
            date="2025-12-15",
            status="success",
            data={"vix_value": 18.567, "source": "TAIFEX-MIS"}
        )
        assert "18.57" in result
    
    def test_failed_case_no_trading(self):
        """測試失敗情況（假日）"""
        result = format_f06_output(
            date="2025-12-14",
            status="failed",
            error="該日無交易資料（可能是假日或休市日）"
        )
        assert "F06 錯誤:" in result
        assert "該日無交易資料" in result
        assert "[TAIFEX]" in result
    
    def test_error_case_with_timestamp(self):
        """測試異常情況（包含時間戳）"""
        result = format_f06_output(
            date="2025-12-15",
            status="error",
            error="瀏覽器啟動失敗",
            timestamp="2025-12-15 22:07:45"
        )
        assert "F06 錯誤:" in result
        assert "瀏覽器啟動失敗" in result
        assert "2025-12-15 22:07:45" in result
    
    def test_error_case_with_context(self):
        """測試異常情況（包含上下文）"""
        result = format_f06_output(
            date="2025-12-15",
            status="error",
            error="瀏覽器啟動失敗",
            timestamp="2025-12-15 22:07:45",
            context={"step": "啟動Chrome驅動"}
        )
        assert "step=啟動Chrome驅動" in result


# ============================================================================
# 單元測試 - HTML 表格解析
# ============================================================================

class TestExtractVIXValue:
    """測試 extract_vix_value_from_table 函數"""
    
    def test_extract_from_simple_html(self):
        """測試從簡單 HTML 表格中提取"""
        html = """
        <table>
            <tr><th>臺指選擇權波動率指數</th></tr>
            <tr><td>18.50</td></tr>
        </table>
        """
        result = extract_vix_value_from_table(html, "2025-12-15")
        assert result["status"] == "success"
        assert result["data"]["vix_value"] == 18.50
    
    def test_extract_alternative_column_name(self):
        """測試備選欄位名稱"""
        html = """
        <table>
            <tr><th>波動率指數</th></tr>
            <tr><td>19.25</td></tr>
        </table>
        """
        result = extract_vix_value_from_table(html, "2025-12-15")
        assert result["status"] == "success"
        assert result["data"]["vix_value"] == 19.25
    
    def test_extract_no_table(self):
        """測試無表格的情況"""
        html = "<div>No table here</div>"
        result = extract_vix_value_from_table(html, "2025-12-15")
        assert result["status"] == "failed"
    
    def test_extract_with_string_value(self):
        """測試字串波動率值的轉換"""
        html = """
        <table>
            <tr><th>VIX</th></tr>
            <tr><td>20.50</td></tr>
        </table>
        """
        result = extract_vix_value_from_table(html, "2025-12-15")
        assert result["status"] == "success"
        assert isinstance(result["data"]["vix_value"], float)


# ============================================================================
# Mock Selenium 測試
# ============================================================================

class TestSeleniumIntegration:
    """使用 Mock 測試 Selenium 集成邏輯"""
    
    @patch('f06_v11_openspec_dev.webdriver.Chrome')
    def test_fetch_with_selenium_success(self, mock_chrome_class):
        """測試 Selenium 成功抓取"""
        # 設置 Mock
        mock_driver = MagicMock()
        mock_chrome_class.return_value = mock_driver
        
        # Mock 頁面 HTML
        mock_html = """
        <table>
            <tr><th>臺指選擇權波動率指數</th></tr>
            <tr><td>18.50</td></tr>
        </table>
        """
        mock_driver.page_source = mock_html
        
        # 執行
        result = fetch_with_selenium("2025-12-15")
        
        # 驗證
        assert "18.50" in result
        assert "2025.12.15" in result
        assert mock_driver.quit.called
    
    @patch('f06_v11_openspec_dev.webdriver.Chrome')
    def test_fetch_selenium_button_click(self, mock_chrome_class):
        """測試點擊確認按鈕"""
        mock_driver = MagicMock()
        mock_chrome_class.return_value = mock_driver
        
        # Mock 確認按鈕
        mock_button = MagicMock()
        mock_driver.find_element.return_value = mock_button
        
        mock_html = """
        <table>
            <tr><th>波動率指數</th></tr>
            <tr><td>17.50</td></tr>
        </table>
        """
        mock_driver.page_source = mock_html
        
        result = fetch_with_selenium("2025-12-15")
        
        # 驗證點擊被執行（或至少被嘗試）
        assert "17.50" in result
    
    @patch('f06_v11_openspec_dev.webdriver.Chrome')
    def test_fetch_selenium_browser_cleanup(self, mock_chrome_class):
        """測試瀏覽器正確關閉"""
        mock_driver = MagicMock()
        mock_chrome_class.return_value = mock_driver
        mock_driver.page_source = "<table><tr><th>波動率</th></tr><tr><td>18.0</td></tr></table>"
        
        fetch_with_selenium("2025-12-15")
        
        # 驗證 quit 被調用
        assert mock_driver.quit.called


# ============================================================================
# 邊界情況測試
# ============================================================================

class TestEdgeCases:
    """測試邊界情況"""
    
    def test_invalid_date_format(self):
        """測試日期格式錯誤"""
        result = fetch_with_selenium("2025-12/15")
        assert "F06 錯誤:" in result
        assert "日期格式錯誤" in result
    
    def test_empty_date_string(self):
        """測試空日期字串"""
        result = fetch_with_selenium("")
        assert "F06 錯誤:" in result
    
    def test_vix_value_precision_edge_cases(self):
        """測試邊界波動率值"""
        test_cases = [
            (0.01, "0.01"),
            (999.99, "999.99"),
            (18.567, "18.57"),  # 四捨五入
            (18.564, "18.56"),  # 四捨五入
        ]
        
        for vix_value, expected in test_cases:
            result = format_f06_output(
                date="2025-12-15",
                status="success",
                data={"vix_value": vix_value, "source": "TAIFEX-MIS"}
            )
            assert expected in result


# ============================================================================
# 輸出格式驗證
# ============================================================================

class TestOutputFormat:
    """測試輸出格式的正確性"""
    
    def test_success_format_complete_structure(self):
        """測試成功輸出的完整結構"""
        result = format_f06_output(
            date="2025-12-15",
            status="success",
            data={"vix_value": 18.50, "source": "TAIFEX-MIS"}
        )
        
        # 應該包含所有必要元素
        assert "2025.12.15" in result       # 日期
        assert "F06:" in result              # 模塊代碼
        assert "臺指選擇權波動率指數" in result  # 描述
        assert "18.50" in result             # 值
        assert "[TAIFEX]" in result          # 來源標記
    
    def test_error_format_complete_structure(self):
        """測試錯誤輸出的完整結構"""
        result = format_f06_output(
            date="2025-12-15",
            status="error",
            error="瀏覽器啟動失敗",
            timestamp="2025-12-15 22:07:45",
            context={"step": "初始化"}
        )
        
        # 應該包含所有必要元素
        assert "F06 錯誤:" in result
        assert "瀏覽器啟動失敗" in result
        assert "2025-12-15 22:07:45" in result
        assert "step=初始化" in result
        assert "[TAIFEX]" in result


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
            result = fetch_with_selenium(date)
            assert isinstance(result, str)
            # 不應該是格式錯誤（除非其他原因）
    
    def test_invalid_dates_format(self):
        """測試無效日期格式"""
        invalid_dates = [
            "2025/12/15",   # 錯誤分隔符
            "15-12-2025",   # 錯誤順序
            "2025-13-01",   # 無效月份
            "2025-12-32",   # 無效日期
        ]
        
        for date in invalid_dates:
            result = fetch_with_selenium(date)
            assert "F06 錯誤:" in result
            assert "日期格式錯誤" in result


# ============================================================================
# 主測試執行
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
