# Change: 新增 F12 台股每日成交金額抓取模組

## Why

為了完善台指期貨20因子預測系統，需要新增 F12 模組來抓取台股每日成交金額數據。此數據反映市場交易活絡度，是重要的市場情緒指標，有助於預測台指期貨隔日漲跌趨勢。

目前系統已有 F01-F07（期貨籌碼）和 F11, F13-F17（股票相關）模組，但缺少台股成交金額這個關鍵指標。

## What Changes

- 新增 F12 fetcher 模組（`modules/f12_fetcher.py`）
- 從 TWSE 官網（https://www.twse.com.tw/zh/trading/historical/fmtqik.html）抓取指定日期的台股成交金額
- 輸出統一 v5.0 文字格式：`YYYY.MM.DD  F12: 台股每日成交金額 : [數值 (億元)] [TWSE]`
- 完整異常處理（連線逾時、HTTP錯誤、資料解析失敗、假日無資料等）
- 符合 OpenSpec 4-Phase 標準（文檔、實現、測試、部署）

## Impact

**Affected specs:**
- `f12-fetcher` (新增規格)

**Affected code:**
- `modules/f12_fetcher.py` (新增檔案)
- `run.py` (無需修改，自動偵測新模組)
- `dev/f12_package/` (新增開發包目錄)

**Breaking changes:**
- 無破壞性變更

**Dependencies:**
- 現有依賴：`requests`, `pandas`, `beautifulsoup4`, `lxml`
- 無需新增外部依賴

## Success Criteria

1. ✅ F12 模組能成功從 TWSE 抓取指定日期的台股成交金額
2. ✅ 輸出格式符合專案統一規範（v5.0 文字格式）
3. ✅ 完整異常處理，包含 5+ 種異常類型
4. ✅ 通過 21 個單元測試，覆蓋率 90%+
5. ✅ 整合到 `run.py` 並正常運行
6. ✅ 通過 `openspec validate --strict` 驗證
