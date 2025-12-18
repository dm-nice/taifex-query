"""
test_f08_openspec.py
F08 台指期貨夜盤收盤價模組測試套件

測試覆蓋:
- 6 個測試類別
- 21 個單元測試
- 目標覆蓋率: 90%+
"""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import io
import sys
import os

# 添加模組路徑
sys.path.insert(0, os.path.dirname(__file__))

import f08_openspec_dev as f08


# ============================================================================
# 1️⃣ 格式驗證測試 (5 個)
# ============================================================================

class TestOutputFormat:
    """測試輸出格式是否符合 v5.0 規範"""

    @patch('f08_openspec_dev.requests.get')
    def test_date_format_dots(self, mock_get):
        """測試日期格式為 YYYY.MM.DD (點號分隔)"""
        # Mock HTML 回應
        html = """
        <table>
            <tr><th>契約</th><th>最後成交價</th></tr>
            <tr><td>TX</td><td>27591.0</td></tr>
        </table>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = f08.fetch("2025-12-18")
        assert "2025.12.18" in result  # 日期應為點號格式
        assert "2025-12-18" not in result  # 不應包含破折號

    @patch('f08_openspec_dev.requests.get')
    def test_number_with_comma(self, mock_get):
        """測試數值包含千分位逗號"""
        html = """
        <table>
            <tr><th>契約</th><th>最後成交價</th></tr>
            <tr><td>TX</td><td>27591.0</td></tr>
        </table>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_get.return_value = mock_response

        result = f08.fetch("2025-12-18")
        assert "27,591" in result  # 應包含千分位

    @patch('f08_openspec_dev.requests.get')
    def test_url_in_output(self, mock_get):
        """測試輸出包含來源 URL"""
        html = """
        <table>
            <tr><th>契約</th><th>最後成交價</th></tr>
            <tr><td>TX</td><td>27591.0</td></tr>
        </table>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_get.return_value = mock_response

        result = f08.fetch("2025-12-18")
        assert "https://www.taifex.com.tw/cht/3/futDailyMarketReport" in result

    @patch('f08_openspec_dev.requests.get')
    def test_error_format(self, mock_get):
        """測試錯誤格式"""
        mock_get.side_effect = Exception("測試錯誤")

        result = f08.fetch("2025-12-18")
        assert "F08 錯誤:" in result
        assert "2025.12.18" in result

    def test_module_id(self):
        """測試模組 ID 正確"""
        assert f08.MODULE_ID == "f08"
        assert f08.MODULE_NAME == "f08_fetcher"


# ============================================================================
# 2️⃣ 資料提取測試 (4 個)
# ============================================================================

class TestDataExtraction:
    """測試資料提取邏輯"""

    @patch('f08_openspec_dev.requests.get')
    def test_extract_normal_value(self, mock_get):
        """測試正常數值提取"""
        html = """
        <table>
            <tr><th>契約</th><th>最後成交價</th></tr>
            <tr><td>TX</td><td>27591.0</td></tr>
        </table>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_get.return_value = mock_response

        result = f08.fetch("2025-12-18")
        assert "F08: 台指期貨夜盤收盤價 : 27,591" in result

    @patch('f08_openspec_dev.requests.get')
    def test_comma_in_source_value(self, mock_get):
        """測試來源數值本身包含逗號"""
        html = """
        <table>
            <tr><th>契約</th><th>最後成交價</th></tr>
            <tr><td>TX</td><td>27,591.0</td></tr>
        </table>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_get.return_value = mock_response

        result = f08.fetch("2025-12-18")
        assert "27,591" in result  # 應正確處理

    @patch('f08_openspec_dev.requests.get')
    def test_column_name_with_space(self, mock_get):
        """測試欄位名稱含不規則空白"""
        html = """
        <table>
            <tr><th>契約</th><th>最後 成交價</th></tr>
            <tr><td>TX</td><td>27591.0</td></tr>
        </table>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_get.return_value = mock_response

        result = f08.fetch("2025-12-18")
        assert "27,591" in result  # 應能識別「最後 成交價」

    @patch('f08_openspec_dev.requests.get')
    def test_settlement_price_fallback(self, mock_get):
        """測試優先級：無成交價時使用結算價"""
        html = """
        <table>
            <tr><th>契約</th><th>結算價</th></tr>
            <tr><td>TX</td><td>27550.0</td></tr>
        </table>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_get.return_value = mock_response

        result = f08.fetch("2025-12-18")
        assert "27,550" in result  # 應使用結算價


# ============================================================================
# 3️⃣ 異常處理測試 (5 個)
# ============================================================================

class TestExceptionHandling:
    """測試異常處理完整性"""

    @patch('f08_openspec_dev.requests.get')
    def test_timeout_exception(self, mock_get):
        """測試連線逾時異常"""
        import requests
        mock_get.side_effect = requests.Timeout()

        result = f08.fetch("2025-12-18")
        assert "F08 錯誤: 連線逾時" in result

    @patch('f08_openspec_dev.requests.get')
    def test_http_error(self, mock_get):
        """測試 HTTP 錯誤"""
        import requests
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        result = f08.fetch("2025-12-18")
        assert "F08 錯誤: HTTP 404" in result

    @patch('f08_openspec_dev.requests.get')
    def test_empty_table(self, mock_get):
        """測試空表格"""
        html = """
        <table>
            <tr><th>契約</th><th>最後成交價</th></tr>
        </table>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_get.return_value = mock_response

        result = f08.fetch("2025-12-18")
        assert "F08 錯誤: 查無資料 (可能是假日)" in result

    @patch('f08_openspec_dev.requests.get')
    def test_no_tx_contract(self, mock_get):
        """測試找不到 TX 合約"""
        html = """
        <table>
            <tr><th>契約</th><th>最後成交價</th></tr>
            <tr><td>MTX</td><td>10000.0</td></tr>
        </table>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_get.return_value = mock_response

        result = f08.fetch("2025-12-18")
        assert "F08 錯誤: 找不到台指期(TX)資料" in result

    @patch('f08_openspec_dev.requests.get')
    def test_no_price_columns(self, mock_get):
        """測試無收盤價或結算價欄位"""
        html = """
        <table>
            <tr><th>契約</th><th>開盤價</th></tr>
            <tr><td>TX</td><td>27500.0</td></tr>
        </table>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_get.return_value = mock_response

        result = f08.fetch("2025-12-18")
        assert "F08 錯誤: 無法取得收盤價或結算價" in result


# ============================================================================
# 4️⃣ 邊界情況測試 (3 個)
# ============================================================================

class TestEdgeCases:
    """測試邊界情況"""

    @patch('f08_openspec_dev.requests.get')
    def test_zero_value(self, mock_get):
        """測試零值處理"""
        html = """
        <table>
            <tr><th>契約</th><th>最後成交價</th></tr>
            <tr><td>TX</td><td>0</td></tr>
        </table>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_get.return_value = mock_response

        result = f08.fetch("2025-12-18")
        assert ": 0" in result  # 零值應正常顯示

    @patch('f08_openspec_dev.requests.get')
    def test_large_value(self, mock_get):
        """測試超大數值"""
        html = """
        <table>
            <tr><th>契約</th><th>最後成交價</th></tr>
            <tr><td>TX</td><td>99999.0</td></tr>
        </table>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_get.return_value = mock_response

        result = f08.fetch("2025-12-18")
        assert "99,999" in result

    def test_invalid_date_format(self):
        """測試錯誤日期格式"""
        result = f08.fetch("20251218")  # 錯誤格式
        assert "F08 錯誤: 日期格式錯誤" in result


# ============================================================================
# 5️⃣ 日誌測試 (2 個)
# ============================================================================

class TestLogging:
    """測試日誌記錄"""

    @patch('f08_openspec_dev.requests.get')
    @patch('f08_openspec_dev.logger')
    def test_success_logging(self, mock_logger, mock_get):
        """測試成功抓取時的日誌"""
        html = """
        <table>
            <tr><th>契約</th><th>最後成交價</th></tr>
            <tr><td>TX</td><td>27591.0</td></tr>
        </table>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_get.return_value = mock_response

        f08.fetch("2025-12-18")

        # 驗證日誌呼叫
        assert mock_logger.info.called
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("[F08]" in str(call) for call in log_calls)

    @patch('f08_openspec_dev.requests.get')
    @patch('f08_openspec_dev.logger')
    def test_error_logging(self, mock_logger, mock_get):
        """測試失敗時的日誌"""
        import requests
        mock_get.side_effect = requests.Timeout()

        f08.fetch("2025-12-18")

        # 驗證錯誤日誌呼叫
        assert mock_logger.error.called


# ============================================================================
# 6️⃣ 集成測試 (2 個)
# ============================================================================

class TestIntegration:
    """測試模組集成"""

    def test_module_import(self):
        """測試模組可正確匯入"""
        assert hasattr(f08, 'fetch')
        assert hasattr(f08, 'MODULE_ID')
        assert hasattr(f08, 'SOURCE')

    def test_function_signature(self):
        """測試函式簽名"""
        import inspect
        sig = inspect.signature(f08.fetch)

        # 應有一個參數 date
        assert 'date' in sig.parameters

        # 測試返回值為 str
        result = f08.fetch("invalid-date")
        assert isinstance(result, str)


# ============================================================================
# 執行測試
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
