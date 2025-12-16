# Design Document: F11 加權股價收盤指數

## Technical Specification

### Architecture Decision

使用 **requests + BeautifulSoup** 方案（相對 Selenium）：

```
優點:
- ✅ 輕量級，無需浏覽器驅動
- ✅ 快速執行 (< 500ms)
- ✅ 資源消耗少
- ✅ 易於部署

缺點:
- ⚠️ 需要分析 HTML 結構
- ⚠️ 頁面改變時可能失敗
```

**如果 requests 失敗，改用 Selenium**（參考 F06 v1.1 模式）

### Data Source

**URL**: `https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html`

**抓取流程**:

1. 向 TWSE 伺服器發送 GET 請求
2. 解析返回的 HTML 頁面
3. 尋找包含指數數據的表格 `<table>`
4. 提取最新行的收盤指數值
5. 格式化為統一輸出字串

### Function Signature

```python
def fetch_taiex_index() -> str:
    """
    從 TWSE 官網抓取加權股價收盤指數。
    
    Returns:
        str: 格式化後的結果字串，例如:
             "2025.12.17  F11: 加權股價收盤指數 : 18254.50 [TWSE]"
        
    Raises:
        Exception: 包含在返回字串中，例如:
                  "F11 錯誤: [錯誤描述] [TWSE]"
    """
```

### Error Handling Strategy

| 異常類型 | 觸發條件 | 處理方式 | 返回值 |
|---------|--------|--------|--------|
| HTTP 錯誤 | requests.exceptions.RequestException | 日誌記錄 + 返回錯誤字串 | `F11 錯誤: 網路連線失敗 [TWSE]` |
| 解析失敗 | BeautifulSoup 無法找到表格 | 日誌記錄 + 異常捕捉 | `F11 錯誤: 無法解析頁面結構 [TWSE]` |
| 無交易數據 | 表格為空或未找到指數 | 檢查日期是否為假日 | `F11 錯誤: 該日無交易資料 [TWSE]` |
| ValueError | 無法轉換為 float | 日誌記錄 + 返回錯誤 | `F11 錯誤: 數據格式異常 [TWSE]` |
| Timeout | 請求超時 (>10秒) | 重試 1 次後放棄 | `F11 錯誤: 伺服器無回應 [TWSE]` |

### Logging Requirements

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 日誌範例
logger.info("[F11] 開始抓取加權股價收盤指數...")
logger.debug("[F11] HTML 頁面大小: 125KB")
logger.info("[F11] 成功提取指數值: 18254.50")
logger.error("[F11] 網路連線失敗: 連線超時")
```

### Performance Targets

- **執行時間**: < 5 秒
- **記憶體使用**: < 50MB
- **成功率**: > 95%（排除假日）

### Dependencies

```
requests >= 2.28.0        # HTTP 請求
beautifulsoup4 >= 4.11.0  # HTML 解析
pytest >= 7.0.0           # 單元測試
```

### Testing Strategy

#### Unit Tests (10+ 個測試)

- ✅ 成功案例: 實際獲取到指數
- ✅ HTML 解析: 測試 BeautifulSoup 邏輯
- ✅ 格式驗證: 檢查輸出格式
- ✅ 日期驗證: 確保日期格式正確
- ✅ 異常處理: 測試各類失敗情況

#### Integration Tests (5+ 個測試)

- ✅ 實際網路請求 (mocked)
- ✅ 完整流程驗證
- ✅ 假日檢測

### Deployment Strategy

1. 開發完成後移動 `f11_openspec_dev.py` → `modules/f11_fetcher.py`
2. 驗證測試套件全部通過
3. 在 `run.py` 中新增 F11 調用
4. 驗證生產環境執行成功

### Backwards Compatibility

- ✅ 新增模組，不影響既有代碼
- ✅ 輸出格式與 F06、其他模組保持一致

### Success Criteria

- [ ] fetch_taiex_index() 能正確返回指數值
- [ ] 格式完全符合需求 (YYYY.MM.DD 格式)
- [ ] 15+ 個單元測試全部通過
- [ ] 異常情況正確處理
- [ ] 日誌輸出完整
- [ ] 部署到 modules/f11_fetcher.py
