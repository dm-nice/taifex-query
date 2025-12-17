# Technical Design: F12 台股每日成交金額模組

## Context

台指期貨20因子預測系統需要抓取台股每日成交金額數據，作為市場交易活絡度指標。此模組從 TWSE（台灣證券交易所）官網抓取歷史成交金額資料。

**數據來源**: https://www.twse.com.tw/zh/trading/historical/fmtqik.html

**專案規範**:
- 輸出格式：v5.0 統一文字格式
- 測試標準：21 個單元測試，90%+ 覆蓋率
- 開發流程：OpenSpec 4-Phase 標準

## Goals / Non-Goals

### Goals
✅ 從 TWSE 官網抓取指定日期的台股成交金額
✅ 輸出統一 v5.0 文字格式
✅ 完整異常處理（5+ 異常類型）
✅ 支援歷史日期查詢
✅ 符合專案測試標準（21 個測試）

### Non-Goals
❌ 不實現 API 服務器（此次僅實現 fetcher 模組）
❌ 不抓取實時資料（僅歷史日資料）
❌ 不實現資料儲存（僅文字輸出）
❌ 不實現圖表或視覺化

## Decisions

### 1. HTTP 請求方式

**決策**: 使用 `requests` + `pandas.read_html()` 組合

**理由**:
- TWSE 網頁使用標準 HTML 表格格式
- `pandas.read_html()` 能自動解析表格，減少手動解析
- 與 F04, F13-F17 等模組一致的技術棧
- 不需要 Selenium（頁面非動態載入）

**替代方案**:
- ❌ BeautifulSoup 手動解析：較複雜，容易出錯
- ❌ Selenium：過度設計，效能較差

### 2. 日期參數格式

**決策**: 查詢參數使用 `date=YYYYMMDD` 格式

**理由**:
- TWSE 官網 API 使用 `date` 參數接受 YYYYMMDD 格式
- 範例：`?date=20251217&response=html`
- 需從輸入的 `YYYY-MM-DD` 轉換為 `YYYYMMDD`

**實現**:
```python
query_date_formatted = date.replace("-", "")  # "2025-12-17" → "20251217"
url = f"https://www.twse.com.tw/zh/trading/historical/fmtqik.html?date={query_date_formatted}&response=html"
```

### 3. 資料欄位識別

**決策**: 使用多個可能欄位名稱（模糊匹配）

**理由**:
- TWSE 網頁欄位名稱可能包含不規則空白
- 可能的欄位名稱：`成交金額`, `成交金額(億)`, `成 交金額`, `金額`
- 使用優先級清單，依序嘗試

**實現**:
```python
COLUMN_VARIANTS = [
    '成交金額',
    '成交金額(億)',
    '成 交金額',  # 可能有空白
    '金額',
    'Turnover'
]
```

### 4. 數值處理

**決策**: 移除逗號 → 轉換 float → 重新格式化

**理由**:
- TWSE 回傳數值可能包含逗號（如 `12,345.67`）
- 需轉換為 float 進行計算
- 最終輸出使用千分位逗號 + 億元單位

**實現**:
```python
# 移除逗號並轉換
value_str = row['成交金額'].replace(',', '')
value = float(value_str)

# 轉換單位（假設原始為億元）
value_formatted = f"{value:,.2f}"
```

### 5. 輸出格式

**決策**: v5.0 統一文字格式

**成功格式**:
```
2025.12.17  F12: 台股每日成交金額 : 4,567.89 [TWSE]
```

**失敗格式**:
```
F12 錯誤: 該日無交易資料 [TWSE]
```

**規範**:
- 日期：`YYYY.MM.DD`（輸入 `YYYY-MM-DD` 轉換）
- 模組代號：`F12:`
- 數值：千分位逗號 + 小數點兩位
- 來源：`[TWSE]`

### 6. 異常處理策略

**決策**: 捕捉所有異常並轉為文字格式

**異常類型** (5+ 種):
1. `requests.Timeout` → `F12 錯誤: 連線逾時 [TWSE]`
2. `requests.HTTPError` → `F12 錯誤: HTTP {status_code} [TWSE]`
3. `requests.ConnectionError` → `F12 錯誤: 網路連線失敗 [TWSE]`
4. `ValueError` / `KeyError` → `F12 錯誤: 資料解析失敗 [TWSE]`
5. `IndexError` → `F12 錯誤: 欄位缺失 [TWSE]`
6. 空表格（假日）→ `F12 錯誤: 該日無交易資料 [TWSE]`

**規範**: 所有異常不拋出，必須轉為統一文字格式。

## Architecture Patterns

### 模組結構

```python
# ===== 配置區塊 =====
TWSE_URL = "https://www.twse.com.tw/zh/trading/historical/fmtqik.html"
HTTP_TIMEOUT = 10
COLUMN_VARIANTS = [...]

# ===== 日誌配置 =====
logger = logging.getLogger(__name__)
# [F12] prefix

# ===== 主函式 =====
def fetch(date: str) -> str:
    """
    抓取指定日期的台股成交金額

    Args:
        date: 查詢日期，格式 YYYY-MM-DD

    Returns:
        統一格式文字字串
    """
    try:
        # 1. 日期格式轉換
        # 2. HTTP 請求
        # 3. 資料解析
        # 4. 數值提取與格式化
        # 5. 回傳成功格式
    except requests.Timeout:
        return "F12 錯誤: 連線逾時 [TWSE]"
    # ... 其他異常
    except Exception as e:
        return f"F12 錯誤: {str(e)} [TWSE]"

# ===== 輔助函式 =====
def format_output(date: str, value: float) -> str:
    """格式化輸出"""

def format_error(error_msg: str) -> str:
    """格式化錯誤"""

# ===== 獨立測試 =====
def main():
    """命令列測試用"""

if __name__ == '__main__':
    main()
```

### 測試架構（21 個測試）

```
test_f12_openspec.py
├── TestFormatValidation (5 tests)
│   ├── test_success_format
│   ├── test_error_format
│   ├── test_date_format_conversion
│   ├── test_thousand_separator
│   └── test_unit_validation
├── TestDataExtraction (4 tests)
│   ├── test_normal_extraction
│   ├── test_value_format_handling
│   ├── test_column_name_variants
│   └── test_column_priority
├── TestExceptionHandling (5 tests)
│   ├── test_timeout_exception
│   ├── test_http_error
│   ├── test_parsing_failure
│   ├── test_missing_column
│   └── test_format_exception
├── TestEdgeCases (3 tests)
│   ├── test_empty_table_holiday
│   ├── test_zero_value
│   └── test_large_value
├── TestLogging (2 tests)
│   ├── test_success_logging
│   └── test_failure_logging
└── TestIntegration (2 tests)
    ├── test_module_import
    └── test_function_signature
```

## Risks / Trade-offs

### 風險 1: TWSE 網頁結構變更

**風險**: TWSE 官網可能改變表格結構或欄位名稱
**緩解**:
- 使用 `COLUMN_VARIANTS` 支援多個欄位名稱
- 編寫詳細測試確保容易發現問題
- 文檔記錄網頁結構供未來參考

### 風險 2: 日期格式不一致

**風險**: 不同日期的資料格式可能有差異
**緩解**:
- 在測試中涵蓋多個歷史日期
- 使用 pandas 自動處理日期解析
- 記錄已知的邊界情況

### 風險 3: 網路不穩定

**風險**: TWSE 伺服器可能無回應或連線逾時
**緩解**:
- 設置 10 秒 timeout
- 完整的異常處理
- 日誌記錄所有錯誤

## Migration Plan

**無需遷移**（新模組）

**部署步驟**:
1. 開發完成後複製到 `modules/f12_fetcher.py`
2. `run.py` 自動偵測新模組
3. 執行測試驗證：`python run.py 2025-12-17 --module f12_fetcher`

## Open Questions

1. ✅ **成交金額單位**：確認 TWSE 回傳單位為「億元」還是「元」？
   - 待研究：需實際測試網頁回應

2. ✅ **假日處理**：假日是回傳空表格還是錯誤訊息？
   - 待測試：2025-12-14（週六）

3. ✅ **資料延遲**：當日成交金額何時可用？
   - 預期：隔日才公布（與其他 TWSE 模組一致）

---

**版本**: v1.0
**建立日期**: 2025-12-17
**狀態**: 待批准
