# Specification: F09 台指期貨夜盤漲跌點數

## ADDED Requirements

### Requirement: 夜盤漲跌點數資料抓取

F09 模組 MUST 從 TAIFEX 期貨每日交易行情（盤後交易時段）抓取台指期貨 (TX) 近月合約的**漲跌點數**。

#### Scenario: 成功抓取正數漲跌

- **WHEN** 使用者呼叫 `fetch("2025-12-18")` 且夜盤上漲
- **THEN** 模組應返回格式化文字：`"2025.12.18  F09: 台指期貨夜盤漲跌點數 : +108 點  [https://www.taifex.com.tw/cht/3/futDailyMarketReport]"`
- **AND** 正數必須包含 `+` 號
- **AND** 數值包含千分位逗號（如有需要）
- **AND** 包含「點」單位

#### Scenario: 成功抓取負數漲跌

- **WHEN** 使用者呼叫 `fetch("2025-12-17")` 且夜盤下跌
- **THEN** 模組應返回：`"2025.12.17  F09: 台指期貨夜盤漲跌點數 : -108 點  [https://www.taifex.com.tw/cht/3/futDailyMarketReport]"`
- **AND** 負數包含 `-` 號

#### Scenario: 夜盤無漲跌（持平）

- **WHEN** 夜盤收盤價與日盤收盤價相同
- **THEN** 模組應返回：`"2025.12.18  F09: 台指期貨夜盤漲跌點數 : 0 點  [https://www.taifex.com.tw/cht/3/futDailyMarketReport]"`
- **AND** 零值不顯示正負號

#### Scenario: 假日無夜盤資料

- **WHEN** 使用者查詢假日或無夜盤交易的日期
- **THEN** 模組應返回錯誤訊息：`"2025.12.18  F09 錯誤: 查無資料 (可能是假日) [https://www.taifex.com.tw/cht/3/futDailyMarketReport]"`
- **AND** 不應拋出異常

---

### Requirement: 欄位名稱模糊匹配

F09 模組 MUST 使用模糊匹配查找「漲跌點數」相關欄位。

#### Scenario: 多種欄位名稱支援

- **WHEN** 表格欄位為「漲跌點數」、「漲跌」或「Change」
- **THEN** 模組應能正確識別並提取數值
- **AND** 使用 `find_column(df, ['漲跌點數', '漲跌', 'Change', '漲跌 (點)'])` 多關鍵字匹配

---

### Requirement: 正負號格式化

F09 模組 MUST 根據漲跌數值自動添加正負號。

#### Scenario: 正數格式化

- **WHEN** 漲跌點數為正數（例如 108）
- **THEN** 輸出應為 `"+108 點"`
- **AND** 必須包含 `+` 號

#### Scenario: 負數格式化

- **WHEN** 漲跌點數為負數（例如 -52）
- **THEN** 輸出應為 `"-52 點"`
- **AND** 保留 `-` 號

#### Scenario: 零值格式化

- **WHEN** 漲跌點數為 0
- **THEN** 輸出應為 `"0 點"`
- **AND** 不包含正負號

---

### Requirement: 千分位格式化

F09 模組 MUST 對大數值使用千分位逗號。

#### Scenario: 大數值漲跌

- **WHEN** 漲跌點數為 1000 以上（例如 +1,234）
- **THEN** 輸出應為 `"+1,234 點"`
- **AND** 包含千分位逗號

---

### Requirement: 與 F08 資料源一致

F09 模組 MUST 使用與 F08 相同的 URL 和查詢參數。

#### Scenario: URL 參數驗證

- **WHEN** 模組構建請求 URL
- **THEN** URL 應包含：
  - `queryDate=2025/12/18`
  - `marketCode=0`
  - `commodity_id=TX`
  - `queryType=2` (盤後交易時段)
- **AND** 與 F08 使用相同 URL

---

### Requirement: 異常處理完整性

F09 模組 MUST 捕捉所有可能的異常並轉為統一文字格式。

#### Scenario: 連線逾時

- **WHEN** HTTP 請求超過 30 秒無響應
- **THEN** 模組應返回：`"YYYY.MM.DD  F09 錯誤: 連線逾時 [來源]"`

#### Scenario: 找不到漲跌欄位

- **WHEN** 表格中無「漲跌點數」或「漲跌」欄位
- **THEN** 模組應返回：`"YYYY.MM.DD  F09 錯誤: 無法取得漲跌點數 [來源]"`

#### Scenario: 找不到 TX 合約

- **WHEN** 表格中無 TX 合約資料
- **THEN** 模組應返回：`"YYYY.MM.DD  F09 錯誤: 找不到台指期(TX)資料 [來源]"`

---

### Requirement: 日誌記錄

F09 模組 MUST 使用 Python logging 模組記錄所有操作，日誌前綴為 `[F09]`。

#### Scenario: 成功抓取日誌

- **WHEN** 模組成功抓取資料
- **THEN** 日誌應包含：`"[F09] 2025-12-18 開始抓取夜盤漲跌資料"`
- **AND** 日誌應包含：`"[F09] 2025-12-18 夜盤漲跌點數: -108"`

#### Scenario: 失敗異常日誌

- **WHEN** 模組遇到異常
- **THEN** 日誌應包含：`"[F09] 執行過程發生錯誤"`
- **AND** 日誌應包含完整 traceback

---

### Requirement: 函式簽名一致性

F09 模組 MUST 提供統一的 `fetch(date: str) -> str` 函式介面。

#### Scenario: 函式簽名驗證

- **WHEN** 外部模組呼叫 F09
- **THEN** 應使用 `f09_fetcher.fetch(date)` 介面
- **AND** 參數 `date` 型別為 `str` (格式 YYYY-MM-DD)
- **AND** 返回值型別為 `str` (統一文字格式)

---

### Requirement: UTF-8 輸出支援

F09 模組 MUST 在 Windows 終端正確顯示中文字元。

#### Scenario: Windows 終端中文顯示

- **WHEN** 模組在 Windows cmd/PowerShell 執行
- **THEN** 所有中文字元應正常顯示
- **AND** 使用 UTF-8 編碼包裝

---

### Requirement: 資料驗證

F09 模組的輸出 MUST 與 F04、F08 的數據邏輯一致。

#### Scenario: 數據邏輯驗證

- **WHEN** F04 (日盤) = 27,591, F08 (夜盤) = 27,483
- **THEN** F09 (漲跌) 應約等於 -108
- **AND** 計算公式：F09 ≈ F08 - F04

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
**變更 ID**: add-f09-night-change
**狀態**: Proposed
**最後更新**: 2025-12-18
