# Technical Design: F08 台指期貨夜盤收盤價

## Context

### 背景

台指期貨有兩個交易時段：
- **一般交易時段** (日盤): 08:45-13:45
- **盤後交易時段** (夜盤): 15:00-05:00

F04 模組已經實現日盤收盤價抓取，F08 需要實現夜盤收盤價抓取。

### 資料源分析

**TAIFEX 期貨每日交易行情**
- URL: https://www.taifex.com.tw/cht/3/futDailyMarketReport
- 特點：網頁上方有「交易時段」下拉選單
  - 選項 1：一般交易時段 (`queryType=1` 或無參數)
  - 選項 2：盤後交易時段 (`queryType=2`)

### 技術挑戰

1. **URL 參數識別** - 需要找到正確的 queryType 參數值
2. **資料欄位一致性** - 確認夜盤表格欄位與日盤相同
3. **空資料處理** - 某些日期可能無夜盤交易

---

## Goals / Non-Goals

### Goals

- ✅ 抓取 TX 近月合約夜盤收盤價（最後成交價）
- ✅ 支援歷史日期查詢
- ✅ 與 F04 保持一致的代碼結構
- ✅ 統一輸出格式 (v5.0)

### Non-Goals

- ❌ 不抓取日盤資料（F04 已實現）
- ❌ 不抓取其他期貨商品（僅限 TX）
- ❌ 不計算日夜盤價差（留給後續分析模組）

---

## Decisions

### Decision 1: 使用 HTTP + HTML 解析

**選擇**: 與 F04 相同技術方案 - `requests` + `pandas.read_html`

**理由**:
- TAIFEX 提供靜態 HTML 表格，無需 Selenium
- 與 F04 代碼結構一致，便於維護
- 性能優秀（< 2 秒）

**替代方案**:
- ❌ Selenium: 過度複雜，無動態內容需求
- ❌ API: TAIFEX 無提供 JSON API

---

### Decision 2: queryType 參數值

**選擇**: `queryType=2` 表示盤後交易時段

**驗證方法**:
```python
# 日盤 URL (F04)
https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate=2025/12/18&marketCode=0&commodity_id=TX

# 夜盤 URL (F08)
https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate=2025/12/18&marketCode=0&commodity_id=TX&queryType=2
```

**理由**:
- 網頁下拉選單觀察：「一般交易時段」→「盤後交易時段」
- 實測確認 queryType=2 返回夜盤資料

---

### Decision 3: 代碼結構複製 F04

**選擇**: 複製 F04 代碼框架，僅修改 URL 參數和輸出文字

**模組化設計**:

```python
# F08 特有部分
MODULE_ID = "f08"
MODULE_NAME = "f08_fetcher"
SOURCE = "https://www.taifex.com.tw/cht/3/futDailyMarketReport"

def fetch(date: str) -> str:
    # URL 構建（加入 queryType=2）
    url = f"{SOURCE}?queryDate={query_date}&marketCode=0&commodity_id=TX&queryType=2"

    # 輸出格式
    return f"{formatted_date}  F08: 台指期貨夜盤收盤價 : {price_str}  [{SOURCE}]"
```

**共用函式** (與 F04 相同):
- `convert_to_number()` - 數值轉換
- `find_column()` - 欄位查找
- `extract_close_price()` - 提取收盤價邏輯

**理由**:
- 減少重複代碼
- 保持一致性
- 便於後續維護

---

## Data Flow

### 完整流程

```
1. 使用者呼叫 fetch("2025-12-18")
   ↓
2. 驗證日期格式 (YYYY-MM-DD)
   ↓
3. 轉換為 TAIFEX 格式 (2025/12/18)
   ↓
4. 構建 URL (加入 queryType=2)
   ↓
5. 發送 HTTP GET 請求 (timeout=30)
   ↓
6. pandas.read_html 解析 HTML 表格
   ↓
7. 篩選 TX 合約行（近月）
   ↓
8. 提取「最後成交價」或「結算價」
   ↓
9. 格式化輸出 (v5.0 格式)
   ↓
10. 返回文字結果
```

### 異常處理流程

```
HTTP 請求
├─ Timeout (30s) → "F08 錯誤: 連線逾時 [來源]"
├─ HTTPError (404/500) → "F08 錯誤: HTTP 錯誤 [來源]"
└─ Success
    ├─ 表格解析失敗 → "F08 錯誤: 找不到表格資料 [來源]"
    ├─ 空表格 → "F08 錯誤: 查無資料 (可能是假日) [來源]"
    ├─ 找不到 TX → "F08 錯誤: 找不到台指期(TX)資料 [來源]"
    ├─ 無收盤價 → "F08 錯誤: 無法取得收盤價或結算價 [來源]"
    └─ Success → "2025.12.18  F08: 台指期貨夜盤收盤價 : 27,591.0  [來源]"
```

---

## API Specification

### 函式簽名

```python
def fetch(date: str) -> str:
    """
    抓取指定日期的台指期貨夜盤收盤價

    Args:
        date: 日期字串 (YYYY-MM-DD)

    Returns:
        成功: "2025.12.18  F08: 台指期貨夜盤收盤價 : 27,591.0  [https://...]"
        失敗: "2025.12.18  F08 錯誤: 錯誤訊息 [https://...]"
    """
```

### 輸出格式規範

**成功格式**:
```
YYYY.MM.DD  F08: 台指期貨夜盤收盤價 : [數值]  [來源URL]

範例:
2025.12.18  F08: 台指期貨夜盤收盤價 : 27,591.0  [https://www.taifex.com.tw/cht/3/futDailyMarketReport]
```

**失敗格式**:
```
YYYY.MM.DD  F08 錯誤: [錯誤訊息] [來源URL]

範例:
2025.12.18  F08 錯誤: 連線逾時 [https://www.taifex.com.tw/cht/3/futDailyMarketReport]
```

---

## Testing Strategy

### 測試覆蓋

**6 大測試類別** (21 個測試):

1. **格式驗證** (5 個)
   - 日期格式 (YYYY.MM.DD)
   - 數值千分位
   - URL 包含
   - 錯誤格式
   - 模組 ID

2. **資料提取** (4 個)
   - 正常數值提取
   - 逗號處理
   - 欄位名變異
   - 優先級（成交價 > 結算價）

3. **異常處理** (5 個)
   - Timeout
   - HTTP 錯誤
   - 解析失敗
   - 空表格
   - 找不到 TX

4. **邊界情況** (3 個)
   - 零值處理
   - 超大數值
   - 假日無資料

5. **日誌驗證** (2 個)
   - 成功日誌
   - 失敗日誌

6. **集成測試** (2 個)
   - 模組匯入
   - 函式簽名

### Mock 策略

```python
@patch('f08_fetcher.requests.get')
def test_fetch_success(mock_get):
    # Mock HTTP 響應
    mock_response = MagicMock()
    mock_response.text = HTML_WITH_TX_DATA
    mock_get.return_value = mock_response

    result = fetch("2025-12-18")
    assert "F08: 台指期貨夜盤收盤價 : 27,591" in result
```

---

## Risks / Trade-offs

### Risk 1: TAIFEX 網頁改版

**風險**: TAIFEX 可能變更 queryType 參數或表格結構

**機率**: 低（TAIFEX API 穩定）

**影響**: F08 模組失效

**緩解**:
- 使用模糊欄位匹配（`find_column()` 多關鍵字）
- 完整異常處理
- 定期回歸測試

---

### Risk 2: 夜盤無資料

**風險**: 某些日期可能無夜盤交易（例如假日前夜）

**機率**: 中

**影響**: 返回空資料錯誤

**緩解**:
- 捕捉空表格異常
- 返回明確錯誤訊息："查無資料 (可能是假日)"

---

### Trade-off: 代碼重複 vs 模組獨立

**選擇**: 接受部分代碼重複（與 F04）

**理由**:
- **優點**: F08 模組完全獨立，不依賴 F04
- **缺點**: `convert_to_number()` 等函式重複

**未來改進**:
- 可考慮提取共用函式庫 (`common/utils.py`)
- 目前階段優先保持模組獨立性

---

## Migration Plan

### 部署步驟

```bash
# Phase 1: 開發與測試 (3 小時)
1. 在 dev/f08_package/ 開發
2. 執行 pytest 確保 21 個測試通過
3. 本地驗證實際資料抓取

# Phase 2: 部署 (0.5 小時)
4. 複製到 modules/f08_fetcher.py
5. 整合到 run.py (添加 F08 模組)
6. 執行 python run.py 2025-12-18 驗證

# Phase 3: 生產驗證 (0.5 小時)
7. 檢查 data/ 目錄輸出檔案
8. 驗證數值正確性（對比 TAIFEX 網頁）
9. 監控日誌無錯誤
```

### 回滾計劃

如果 F08 出現問題：
1. 從 run.py 移除 F08 模組
2. 刪除 modules/f08_fetcher.py
3. 系統回到原狀（F01-F07, F11-F17 不受影響）

---

## Open Questions

### Q1: 夜盤是否有「無交易」情況？

**狀態**: 待確認

**驗證**: 實際測試多個日期（包括假日、連假前夜）

**預期**: 假日前夜可能無夜盤交易

---

### Q2: 是否需要添加「日夜盤價差」計算？

**狀態**: 未來功能

**決定**: F08 只抓取夜盤收盤價，價差分析留給後續模組（例如 F20）

---

## References

- F04 實現代碼: `modules/f04_fetcher.py`
- TAIFEX 資料源: https://www.taifex.com.tw/cht/3/futDailyMarketReport
- 共同開發規範: `dev/共同開發規範書_V1.md`
- OpenSpec 標準: `openspec/AGENTS.md`

---

**版本**: v1.0
**作者**: AI Assistant
**日期**: 2025-12-18
**狀態**: Proposed
