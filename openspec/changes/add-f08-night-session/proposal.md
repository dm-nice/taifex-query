# Change: Add F08 台指期貨夜盤收盤價模組

## Why

目前系統只有 F04 台指期貨日盤收盤價，缺少夜盤（盤後交易時段）的收盤價資料。夜盤收盤價是重要的預測因子，因為：

1. **夜盤反映國際市場影響** - 夜盤期間（15:00-05:00）包含美股、歐股開盤時間，能反映國際市場對台股的影響
2. **隔日開盤參考** - 夜盤收盤價往往是隔日開盤價的重要參考依據
3. **完整籌碼分析** - 與 F04 日盤收盤價搭配，可進行日夜盤價差分析

## What Changes

- 新增 F08 模組：`modules/f08_fetcher.py`
- 資料來源：TAIFEX 期貨每日交易行情 (https://www.taifex.com.tw/cht/3/futDailyMarketReport)
- 關鍵差異：**交易時段參數從「一般交易時段」切換至「盤後交易時段」**
- 輸出格式：`2025.12.18  F08: 台指期貨夜盤收盤價 : [數值] [來源URL]`

### 新增功能

- ✅ 抓取台指期貨 (TX) 近月合約夜盤收盤價
- ✅ 支援歷史日期查詢 (YYYY-MM-DD)
- ✅ 異常處理：連線逾時、無資料、解析失敗
- ✅ 統一輸出格式 (v5.0)

### 技術方法

- **HTTP + HTML 解析** (參考 F04 實現)
- 使用 `requests` + `pandas.read_html`
- 查詢參數：`queryDate` + `marketCode=0` + `commodity_id=TX` + **`queryType=2`** (盤後)

## Impact

### 影響的規格

- **新增**: `specs/f08-night-session-price/spec.md` (新功能規格)

### 影響的代碼

- **新增**: `modules/f08_fetcher.py` (約 230 行)
- **新增**: `dev/f08_package/f08_openspec_dev.py` (開發版)
- **新增**: `dev/f08_package/test_f08_openspec.py` (測試套件)
- **修改**: `run.py` (整合 F08 模組到主程式)
- **更新**: `dev/README.md` (更新模組清單)

### 依賴性

- 無破壞性變更
- 參考 F04 實現模式 (相同資料源，不同交易時段)
- 與現有模組獨立，不影響其他模組運作

---

**Change ID**: `add-f08-night-session`
**預計開發時間**: 4.5 小時 (OpenSpec 4-Phase)
**優先級**: Medium
**狀態**: Proposed
