# Implementation Tasks: F12 台股每日成交金額模組

## 1. 前期準備 (Preparation)

- [x] 1.1 研究 TWSE 成交金額網頁結構（https://www.twse.com.tw/zh/trading/historical/fmtqik.html）
- [x] 1.2 確認資料欄位名稱與位置（成交金額、日期格式）
- [x] 1.3 測試不同日期的資料格式一致性
- [x] 1.4 確認假日/非交易日的回應行為

## 2. 核心實現 (Core Implementation)

- [x] 2.1 建立 `dev/f12_package/f12_openspec_dev.py` 基礎結構
- [x] 2.2 實現 `fetch(date: str) -> str` 主函式
- [x] 2.3 實現日期格式轉換（YYYY-MM-DD → YYYYMMDD 查詢參數）
- [x] 2.4 實現 HTTP 請求邏輯（GET 請求 + JSON API）
- [x] 2.5 實現 JSON 資料解析（使用原生 json 模組）
- [x] 2.6 實現資料提取邏輯（找到成交金額欄位）
- [x] 2.7 實現數值格式化（千分位逗號、單位轉換為億元）
- [x] 2.8 實現統一輸出格式（v5.0 規範）

## 3. 異常處理 (Error Handling)

- [x] 3.1 處理 `requests.Timeout` 異常（連線逾時）
- [x] 3.2 處理 `requests.HTTPError` 異常（HTTP 4xx/5xx）
- [x] 3.3 處理 `requests.ConnectionError` 異常（網路連線失敗）
- [x] 3.4 處理 `ValueError` / `KeyError` 異常（資料解析失敗）
- [x] 3.5 處理 `IndexError` 異常（欄位缺失）
- [x] 3.6 處理假日/非交易日情況（API stat != OK）
- [x] 3.7 統一異常訊息格式（`F12 錯誤: [訊息] [TWSE]`）

## 4. 日誌記錄 (Logging)

- [x] 4.1 配置 logger（使用 `[F12]` 前綴）
- [x] 4.2 記錄關鍵步驟（開始抓取、HTTP 請求、資料解析）
- [x] 4.3 記錄錯誤與異常（含完整 traceback）
- [x] 4.4 記錄成功結果（含數值）

## 5. 測試開發 (Testing)

- [x] 5.1 建立 `dev/f12_package/test_f12_openspec.py` 測試檔案
- [x] 5.2 實現格式驗證測試（5 個測試）
  - [x] 5.2.1 成功格式驗證（日期、模組代號、數值、來源）
  - [x] 5.2.2 錯誤格式驗證
  - [x] 5.2.3 日期格式轉換（- → .）
  - [x] 5.2.4 千分位逗號驗證
  - [x] 5.2.5 單位驗證（億元）
- [x] 5.3 實現資料提取測試（4 個測試）
  - [x] 5.3.1 正常資料提取
  - [x] 5.3.2 數值格式處理（逗號、小數點）
  - [x] 5.3.3 欄位名稱變異處理
  - [x] 5.3.4 多個可能欄位的優先級
- [x] 5.4 實現異常處理測試（5 個測試）
  - [x] 5.4.1 Timeout 異常
  - [x] 5.4.2 HTTP 錯誤（404, 500）
  - [x] 5.4.3 資料解析失敗
  - [x] 5.4.4 欄位缺失
  - [x] 5.4.5 格式異常
- [x] 5.5 實現邊界情況測試（3 個測試）
  - [x] 5.5.1 空表格（假日）
  - [x] 5.5.2 零值處理
  - [x] 5.5.3 超大數值
- [x] 5.6 實現日誌測試（2 個測試）
  - [x] 5.6.1 成功日誌驗證
  - [x] 5.6.2 失敗日誌驗證
- [x] 5.7 實現集成測試（2 個測試）
  - [x] 5.7.1 模組匯入測試
  - [x] 5.7.2 函式簽名驗證
- [x] 5.8 執行測試並達到 90%+ 覆蓋率（23/23 passed）

## 6. 文檔撰寫 (Documentation)

- [x] 6.1 撰寫模組 docstring（功能說明、參數、回傳值）
- [x] 6.2 撰寫函式註解（中文說明）
- [x] 6.3 建立 `dev/f12_package/IMPLEMENTATION_REPORT.md` 實現報告
- [x] 6.4 更新 `README.md`（新增 F12 說明）

## 7. 部署上線 (Deployment)

- [x] 7.1 複製 `dev/f12_package/f12_openspec_dev.py` → `modules/f12_fetcher.py`
- [x] 7.2 使用 `run.py` 驗證模組自動載入
- [x] 7.3 執行生產驗證（實時資料測試）
  - [x] 7.3.1 測試今日資料
  - [x] 7.3.2 測試歷史資料（2025-12-16）- 成功：4,934.41 億元
  - [x] 7.3.3 測試假日資料（2025-12-14 週六）
- [x] 7.4 確認輸出檔案正確生成（`data/YYYY-MM-DD_HHMM_f12_fetcher.txt`）

## 8. 驗證與歸檔 (Validation & Archive)

- [x] 8.1 執行 `openspec validate add-f12-stock-turnover --strict`
- [x] 8.2 修正所有驗證錯誤
- [x] 8.3 請求使用者批准
- [ ] 8.4 歸檔變更（`openspec archive add-f12-stock-turnover --yes`）

---

**預估時間**: 4.5 小時（OpenSpec 4-Phase 標準）
- Phase 1 文檔化: 1.5 小時
- Phase 2 代碼實現: 1.5 小時
- Phase 3 測試: 1 小時
- Phase 4 部署: 0.5 小時
