# Specification: F08 台指期貨夜盤收盤價

## ADDED Requirements

### Requirement: 夜盤收盤價資料抓取

F08 模組 MUST 從 TAIFEX 期貨每日交易行情抓取台指期貨 (TX) 近月合約的**盤後交易時段（夜盤）**收盤價。

#### Scenario: 成功抓取夜盤收盤價

- **WHEN** 使用者呼叫 `fetch("2025-12-18")` 且該日有夜盤交易資料
- **THEN** 模組應返回格式化文字：`"2025.12.18  F08: 台指期貨夜盤收盤價 : 27,591.0  [https://www.taifex.com.tw/cht/3/futDailyMarketReport]"`
- **AND** 數值包含千分位逗號
- **AND** 日期格式為 YYYY.MM.DD
- **AND** URL 為使用者可訪問的網頁 URL

#### Scenario: 假日無夜盤交易資料

- **WHEN** 使用者查詢假日或無夜盤交易的日期
- **THEN** 模組應返回錯誤訊息：`"2025.12.18  F08 錯誤: 查無資料 (可能是假日) [https://www.taifex.com.tw/cht/3/futDailyMarketReport]"`
- **AND** 不應拋出異常

#### Scenario: 日期格式錯誤

- **WHEN** 使用者傳入錯誤日期格式（如 "20251218" 或 "2025/12/18"）
- **THEN** 模組應返回錯誤訊息：`"20251218  F08 錯誤: 日期格式錯誤，請使用 YYYY-MM-DD [https://www.taifex.com.tw/cht/3/futDailyMarketReport]"`

---

### Requirement: URL 參數正確性

F08 模組 MUST 在 HTTP 請求中包含 `queryType=2` 參數以指定「盤後交易時段」。

#### Scenario: URL 參數驗證

- **WHEN** 模組構建請求 URL
- **THEN** URL 應包含以下參數：
  - `queryDate=2025/12/18` (日期格式 YYYY/MM/DD)
  - `marketCode=0` (市場代碼)
  - `commodity_id=TX` (商品代碼：台指期貨)
  - `queryType=2` (交易時段：盤後)
- **AND** 完整 URL 範例：`https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate=2025/12/18&marketCode=0&commodity_id=TX&queryType=2`

---

### Requirement: 近月合約選擇

F08 模組 MUST 自動選取 TX 台指期貨的**近月合約**進行資料提取。

#### Scenario: 多個合約並存時選擇近月

- **WHEN** TAIFEX 表格中存在多個 TX 合約（如 TX 202501, TX 202502）
- **THEN** 模組應選取第一筆 TX 合約（通常為近月）
- **AND** 提取該合約的「最後成交價」或「結算價」

---

### Requirement: 資料欄位提取優先級

F08 模組 MUST 優先提取「最後成交價」欄位，若不存在則嘗試提取「結算價」欄位。

#### Scenario: 最後成交價存在

- **WHEN** 表格中存在「最後成交價」欄位且有數值
- **THEN** 模組應使用該數值作為夜盤收盤價

#### Scenario: 僅結算價存在

- **WHEN** 表格中「最後成交價」為空或不存在，但「結算價」存在
- **THEN** 模組應使用「結算價」作為夜盤收盤價

#### Scenario: 兩者皆不存在

- **WHEN** 表格中既無「最後成交價」也無「結算價」
- **THEN** 模組應返回錯誤訊息：`"F08 錯誤: 無法取得收盤價或結算價 [來源]"`

---

### Requirement: 欄位名稱模糊匹配

F08 模組 MUST 使用模糊匹配機制處理 TAIFEX 表格欄位名稱變異（如空白、大小寫）。

#### Scenario: 欄位名稱含不規則空白

- **WHEN** 表格欄位為 "最後 成交價"（含空白）
- **THEN** 模組應正確識別並提取數值
- **AND** 使用 `find_column(df, ['最後成交價', '最後 成交價', 'Close', 'Last Price'])` 多關鍵字匹配

---

### Requirement: 數值格式化

F08 模組 MUST 將數值格式化為包含千分位逗號的字串。

#### Scenario: 整數數值

- **WHEN** 提取到數值 `27591`
- **THEN** 輸出應為 `"27,591"`

#### Scenario: 小數數值

- **WHEN** 提取到數值 `27591.5`
- **THEN** 輸出應為 `"27,591.5"` (保留原有小數位)

#### Scenario: 零值

- **WHEN** 提取到數值 `0`
- **THEN** 輸出應為 `"0"`

---

### Requirement: 異常處理完整性

F08 模組 MUST 捕捉所有可能的異常並轉為統一文字格式，不得拋出異常。

#### Scenario: 連線逾時

- **WHEN** HTTP 請求超過 30 秒無響應
- **THEN** 模組應返回：`"YYYY.MM.DD  F08 錯誤: 連線逾時 [來源]"`

#### Scenario: HTTP 404 錯誤

- **WHEN** TAIFEX 返回 404 Not Found
- **THEN** 模組應返回：`"YYYY.MM.DD  F08 錯誤: HTTP 404 [來源]"`

#### Scenario: 解析失敗

- **WHEN** pandas.read_html 無法解析 HTML（無表格）
- **THEN** 模組應返回：`"YYYY.MM.DD  F08 錯誤: 找不到表格資料 [來源]"`

#### Scenario: 找不到 TX 合約

- **WHEN** 表格中無任何 TX 合約資料
- **THEN** 模組應返回：`"YYYY.MM.DD  F08 錯誤: 找不到台指期(TX)資料 [來源]"`

---

### Requirement: 日誌記錄

F08 模組 MUST 使用 Python logging 模組記錄所有操作，日誌前綴為 `[F08]`。

#### Scenario: 成功抓取日誌

- **WHEN** 模組成功抓取資料
- **THEN** 日誌應包含：`"[F08] 2025-12-18 開始抓取資料"`
- **AND** 日誌應包含：`"[F08] 正在抓取 2025-12-18 的資料: [URL]"`

#### Scenario: 失敗異常日誌

- **WHEN** 模組遇到異常
- **THEN** 日誌應包含：`"[F08] 執行過程發生錯誤"`
- **AND** 日誌應包含完整 traceback（使用 `logger.exception()`）

---

### Requirement: 函式簽名一致性

F08 模組 MUST 提供統一的 `fetch(date: str) -> str` 函式介面。

#### Scenario: 函式簽名驗證

- **WHEN** 外部模組（如 run.py）呼叫 F08
- **THEN** 應使用 `f08_fetcher.fetch(date)` 介面
- **AND** 參數 `date` 型別為 `str` (格式 YYYY-MM-DD)
- **AND** 返回值型別為 `str` (統一文字格式)

---

### Requirement: UTF-8 輸出支援

F08 模組 MUST 在 Windows 終端正確顯示中文字元，不得出現 UnicodeEncodeError。

#### Scenario: Windows 終端中文顯示

- **WHEN** 模組在 Windows cmd/PowerShell 執行
- **THEN** 所有中文字元應正常顯示
- **AND** 使用 `io.TextIOWrapper` 包裝 `sys.stdout` 為 UTF-8 編碼

---

### Requirement: 獨立測試入口

F08 模組 MUST 提供 `if __name__ == '__main__'` 入口供獨立測試。

#### Scenario: 命令列測試

- **WHEN** 使用者執行 `python f08_fetcher.py 2025-12-18`
- **THEN** 模組應輸出該日期的抓取結果
- **AND** 若無參數，預設測試日期為 2025-12-18

---

### Requirement: 代碼覆蓋率

F08 測試套件 MUST 達到 90% 以上的代碼覆蓋率。

#### Scenario: 執行覆蓋率測試

- **WHEN** 執行 `pytest test_f08_openspec.py --cov=f08_fetcher`
- **THEN** 覆蓋率報告應顯示 ≥ 90%
- **AND** 所有 21 個測試應通過

---

## MODIFIED Requirements

*(無修改的既有需求)*

---

## REMOVED Requirements

*(無移除的需求)*

---

## RENAMED Requirements

*(無重新命名的需求)*

---

**規格版本**: v1.0
**變更 ID**: add-f08-night-session
**狀態**: Proposed
**最後更新**: 2025-12-18
