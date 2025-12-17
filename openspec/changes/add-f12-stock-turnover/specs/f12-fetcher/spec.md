# Spec: F12 台股每日成交金額抓取模組

## ADDED Requirements

### Requirement: 抓取指定日期的台股成交金額

系統 SHALL 從 TWSE（台灣證券交易所）官網抓取指定日期的台股每日成交金額數據，並 MUST 回傳統一格式的文字字串。

#### Scenario: 成功抓取交易日資料

- **GIVEN** TWSE 網站可正常訪問
- **AND** 查詢日期為有效交易日 "2025-12-17"
- **WHEN** 呼叫 `fetch("2025-12-17")`
- **THEN** 回傳格式化字串 `"2025.12.17  F12: 台股每日成交金額 : 4,567.89 [TWSE]"`
- **AND** 日期格式為 YYYY.MM.DD（將輸入的 - 轉換為 .）
- **AND** 數值使用千分位逗號
- **AND** 數值保留兩位小數
- **AND** 包含來源標記 `[TWSE]`

#### Scenario: 查詢假日或非交易日

- **GIVEN** 查詢日期為假日或非交易日 "2025-12-14"（週六）
- **WHEN** 呼叫 `fetch("2025-12-14")`
- **THEN** 回傳錯誤訊息 `"F12 錯誤: 該日無交易資料 [TWSE]"`
- **AND** 不拋出異常

#### Scenario: 查詢歷史日期

- **GIVEN** 查詢日期為有效歷史交易日 "2025-11-15"
- **WHEN** 呼叫 `fetch("2025-11-15")`
- **THEN** 回傳該日的歷史成交金額
- **AND** 格式符合統一規範

### Requirement: HTTP 請求與連線處理

系統 MUST 向 TWSE 官網發送 HTTP GET 請求，並 SHALL 妥善處理所有連線異常。

#### Scenario: 正常 HTTP 請求

- **GIVEN** TWSE 伺服器正常運作
- **WHEN** 發送 GET 請求至 `https://www.twse.com.tw/zh/trading/historical/fmtqik.html?date=20251217&response=html`
- **THEN** 接收 HTTP 200 回應
- **AND** 解析回應內容

#### Scenario: 連線逾時

- **GIVEN** TWSE 伺服器無回應超過 10 秒
- **WHEN** 呼叫 `fetch("2025-12-17")`
- **THEN** 回傳 `"F12 錯誤: 連線逾時 [TWSE]"`
- **AND** 不拋出異常

#### Scenario: HTTP 錯誤

- **GIVEN** TWSE 伺服器回傳 HTTP 404 或 500 錯誤
- **WHEN** 呼叫 `fetch("2025-12-17")`
- **THEN** 回傳 `"F12 錯誤: HTTP {status_code} [TWSE]"`
- **AND** 包含具體的 HTTP 狀態碼
- **AND** 不拋出異常

#### Scenario: 網路連線失敗

- **GIVEN** 無網路連線或 DNS 解析失敗
- **WHEN** 呼叫 `fetch("2025-12-17")`
- **THEN** 回傳 `"F12 錯誤: 網路連線失敗 [TWSE]"`
- **AND** 不拋出異常

### Requirement: 資料解析與提取

系統 MUST 從 TWSE 網頁的 HTML 表格中提取成交金額數據，並 SHALL 處理各種資料格式變異。

#### Scenario: 正常資料提取

- **GIVEN** TWSE 回傳包含成交金額的標準 HTML 表格
- **WHEN** 解析表格資料
- **THEN** 成功提取成交金額數值
- **AND** 數值格式正確

#### Scenario: 欄位名稱包含空白

- **GIVEN** 表格欄位名稱為 `"成 交金額"` 或 `"成交 金額"`（包含不規則空白）
- **WHEN** 嘗試識別欄位
- **THEN** 使用模糊匹配成功找到欄位
- **AND** 正確提取數值

#### Scenario: 數值包含逗號

- **GIVEN** 成交金額數值為 `"12,345.67"`（包含千分位逗號）
- **WHEN** 解析數值
- **THEN** 正確移除逗號並轉換為 float
- **AND** 重新格式化為千分位逗號輸出

#### Scenario: 資料解析失敗

- **GIVEN** TWSE 回傳的 HTML 格式異常或無法解析
- **WHEN** 呼叫 `fetch("2025-12-17")`
- **THEN** 回傳 `"F12 錯誤: 資料解析失敗 [TWSE]"`
- **AND** 不拋出異常

#### Scenario: 欄位缺失

- **GIVEN** TWSE 回傳的表格缺少成交金額欄位
- **WHEN** 呼叫 `fetch("2025-12-17")`
- **THEN** 回傳 `"F12 錯誤: 欄位缺失 [TWSE]"`
- **AND** 不拋出異常

### Requirement: 日期格式轉換

系統 SHALL 將輸入的日期格式轉換為 TWSE API 所需格式，並 MUST 在輸出時使用統一格式。

#### Scenario: 日期格式轉換（輸入 → 查詢參數）

- **GIVEN** 輸入日期為 `"2025-12-17"`（YYYY-MM-DD 格式）
- **WHEN** 準備 HTTP 請求
- **THEN** 轉換為 `"20251217"`（YYYYMMDD 格式）用於查詢參數
- **AND** 查詢 URL 為 `?date=20251217`

#### Scenario: 日期格式轉換（輸出格式）

- **GIVEN** 輸入日期為 `"2025-12-17"`
- **WHEN** 格式化輸出字串
- **THEN** 輸出日期為 `"2025.12.17"`（YYYY.MM.DD 格式）
- **AND** 使用點號分隔

#### Scenario: 無效日期格式

- **GIVEN** 輸入日期為無效格式 `"2025/12/17"` 或 `"17-12-2025"`
- **WHEN** 呼叫 `fetch(invalid_date)`
- **THEN** 回傳 `"F12 錯誤: 日期格式無效 [TWSE]"`
- **AND** 不拋出異常

### Requirement: 輸出格式規範

系統 MUST 遵循專案統一的 v5.0 文字格式規範，並 SHALL 確保與其他模組一致。

#### Scenario: 成功格式驗證

- **GIVEN** 成功抓取成交金額為 4567.89 億元
- **WHEN** 格式化輸出
- **THEN** 回傳 `"2025.12.17  F12: 台股每日成交金額 : 4,567.89 [TWSE]"`
- **AND** 包含日期（YYYY.MM.DD 格式）
- **AND** 包含模組代號 `F12:`
- **AND** 包含描述 `台股每日成交金額`
- **AND** 包含冒號分隔符 `: `
- **AND** 包含數值（千分位逗號 + 兩位小數）
- **AND** 包含來源標記 `[TWSE]`

#### Scenario: 錯誤格式驗證

- **GIVEN** 發生任何錯誤（連線、解析、欄位缺失等）
- **WHEN** 格式化錯誤訊息
- **THEN** 回傳 `"F12 錯誤: [具體錯誤訊息] [TWSE]"`
- **AND** 不包含日期（錯誤訊息簡化格式）
- **AND** 包含模組代號 `F12`
- **AND** 包含 `錯誤:` 關鍵字
- **AND** 包含具體錯誤說明
- **AND** 包含來源標記 `[TWSE]`

### Requirement: 日誌記錄

系統 MUST 記錄所有關鍵操作和錯誤，並 SHALL 使用統一的 `[F12]` 前綴。

#### Scenario: 成功執行日誌

- **GIVEN** 成功抓取成交金額
- **WHEN** 執行過程中
- **THEN** 記錄以下日誌：
  - `[F12] 2025-12-17 開始抓取資料`
  - `[F12] HTTP 請求成功，狀態碼 200`
  - `[F12] 成功提取成交金額: 4567.89`
  - `[F12] 回傳結果: 2025.12.17  F12: 台股每日成交金額 : 4,567.89 [TWSE]`

#### Scenario: 錯誤執行日誌

- **GIVEN** 發生連線逾時錯誤
- **WHEN** 執行過程中
- **THEN** 記錄以下日誌：
  - `[F12] 2025-12-17 開始抓取資料`
  - `[F12] 錯誤: 連線逾時`
  - `[F12] 回傳錯誤訊息: F12 錯誤: 連線逾時 [TWSE]`

### Requirement: 邊界情況處理

系統 SHALL 妥善處理各種邊界情況，包括零值、超大值和空資料。

#### Scenario: 零值處理

- **GIVEN** TWSE 回傳成交金額為 0.00
- **WHEN** 格式化輸出
- **THEN** 回傳 `"2025.12.17  F12: 台股每日成交金額 : 0.00 [TWSE]"`
- **AND** 正確顯示 0.00

#### Scenario: 超大數值處理

- **GIVEN** 成交金額為 99,999,999.99 億元
- **WHEN** 格式化輸出
- **THEN** 回傳 `"2025.12.17  F12: 台股每日成交金額 : 99,999,999.99 [TWSE]"`
- **AND** 千分位逗號正確顯示

#### Scenario: 空表格（假日）

- **GIVEN** TWSE 回傳空的 HTML 表格（無資料列）
- **WHEN** 呼叫 `fetch("2025-12-14")`
- **THEN** 回傳 `"F12 錯誤: 該日無交易資料 [TWSE]"`
- **AND** 不拋出異常

### Requirement: 函式簽名與介面

系統 MUST 提供統一的 `fetch(date: str) -> str` 函式介面，並 SHALL 與其他模組保持一致。

#### Scenario: 函式簽名驗證

- **GIVEN** F12 模組已載入
- **WHEN** 檢查 `fetch` 函式
- **THEN** 函式簽名為 `def fetch(date: str) -> str:`
- **AND** 接受單一字串參數（日期）
- **AND** 回傳字串類型

#### Scenario: 模組匯入

- **GIVEN** F12 模組位於 `modules/f12_fetcher.py`
- **WHEN** 執行 `import modules.f12_fetcher`
- **THEN** 模組成功載入
- **AND** `fetch` 函式可被呼叫
- **AND** 無匯入錯誤

### Requirement: 測試覆蓋率

系統 MUST 通過 21 個單元測試，並 SHALL 達到 90% 以上的代碼覆蓋率。

#### Scenario: 測試執行

- **GIVEN** 完整的測試套件（21 個測試）
- **WHEN** 執行 `pytest test_f12_openspec.py -v`
- **THEN** 所有 21 個測試通過
- **AND** 無測試失敗
- **AND** 覆蓋率報告顯示 90%+ 覆蓋率

#### Scenario: 測試分類完整性

- **GIVEN** 測試套件
- **WHEN** 檢查測試分類
- **THEN** 包含以下 6 大類：
  - 格式驗證測試（5 個）
  - 資料提取測試（4 個）
  - 異常處理測試（5 個）
  - 邊界情況測試（3 個）
  - 日誌測試（2 個）
  - 集成測試（2 個）

---

**規格版本**: v1.0
**建立日期**: 2025-12-17
**適用模組**: F12 台股每日成交金額抓取模組
