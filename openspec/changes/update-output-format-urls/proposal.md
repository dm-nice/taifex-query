# Change: 更新模組輸出格式，將資料來源從簡寫改為完整 URL

## Why

目前所有模組的輸出格式使用簡寫的資料來源標記（如 `[TWSE]`、`[TAIFEX]`、`[twse.com.tw]`），這對用戶來說不夠明確，無法直接得知具體的資料來源 API 端點。

**問題**:
1. 用戶無法從輸出直接得知資料的確切來源 URL
2. 不同模組使用不同的簡寫方式（`[TWSE]` vs `[twse.com.tw]`），缺乏一致性
3. 調試時需要查看程式碼才能確認實際的 API 端點
4. 不符合資料透明度的最佳實踐

## What Changes

將以下模組的輸出格式從簡寫改為完整的資料來源 URL：

### TAIFEX 模組
- **F04** (台指期貨當日收盤價): `[TAIFEX]` → `[https://www.taifex.com.tw/cht/3/futDailyMarketReport]`
- **F05** (台指期貨選擇權總成交量): `[TAIFEX]` → `[https://www.taifex.com.tw/cht/3/optDailyMarketReport]`
- **F06** (臺指選擇權波動率指數): `[TAIFEX]` → `[https://mis.taifex.com.tw/futures/VolatilityQuotes]`
- **F07** (臺指選擇權買賣權未平倉量比率): `[TAIFEX]` → `[https://www.taifex.com.tw/cht/3/pcRatio]`

### TWSE 模組
- **F11** (加權股價收盤指數): `[TWSE]` → `[https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html]`
- **F12** (台股每日成交金額): `[TWSE]` → `[https://www.twse.com.tw/rwd/zh/afterTrading/FMTQIK]`
- **F13** (台灣加權股價指數與 20 日均線距離): `[twse.com.tw]` → `[https://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX.html]` *(修正為使用者可訪問的網頁)*
- **F14** (台積電當日收盤價): `[twse.com.tw]` → `[https://www.twse.com.tw/zh/trading/historical/stock-day.html]` *(修正為使用者可訪問的網頁)*
- **F15** (台積電當日漲跌價差): `[TWSE]` → `[https://www.twse.com.tw/zh/trading/historical/stock-day.html]` *(修正為使用者可訪問的網頁)*
- **F16** (台積電當日成交股數): `[twse.com.tw]` → `[https://www.twse.com.tw/zh/trading/historical/stock-day.html]` *(修正為使用者可訪問的網頁)*
- **F17** (台灣股票外資及陸資買賣差額): `[twse.com.tw]` → `[https://www.twse.com.tw/fund/BFI82U]`

**同時修復**:
- F04, F05, F06, F07, F13, F14, F15, F16, F17: 添加 UTF-8 輸出處理的錯誤處理機制，防止多模組同時執行時出現 "I/O operation on closed file" 錯誤

## Impact

### 受影響的模組
- **TAIFEX 模組**: F04, F05, F06, F07
- **TWSE 模組**: F11, F12, F13, F14, F15, F16, F17

### 受影響的檔案
- `modules/f04_fetcher.py`
- `modules/f05_fetcher.py`
- `modules/f06_fetcher.py`
- `modules/f07_fetcher.py`
- `modules/f11_fetcher.py`
- `modules/f12_fetcher.py`
- `modules/f13_fetcher.py`
- `modules/f14_fetcher.py`
- `modules/f15_fetcher.py`
- `modules/f16_fetcher.py`
- `modules/f17_fetcher.py`

### 輸出格式變更

**變更前**:
```
2025.12.18  F11: 加權股價收盤指數 : 27525.17 [TWSE]
2025.12.18  F13 錯誤: 該日無交易資料 [twse.com.tw]
```

**變更後**:
```
2025.12.18  F11: 加權股價收盤指數 : 27525.17 [https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html]
2025.12.18  F13 錯誤: 該日無交易資料 [https://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX.html]
2025.12.17  F14: 台積電當日收盤價 : 1,430.00 [https://www.twse.com.tw/zh/trading/historical/stock-day.html]
```

### 向後兼容性
- **非破壞性變更**: 輸出格式的基本結構保持不變，只是資料來源部分更詳細
- **解析影響**: 如果有解析程式依賴 `[來源]` 的確切格式，需要更新正則表達式以支持 URL

### 好處
1. ✅ **提高透明度**: 用戶可直接看到資料來源
2. ✅ **便於調試**: 快速定位 API 端點問題
3. ✅ **統一格式**: 所有模組使用一致的完整 URL 格式
4. ✅ **提升穩定性**: UTF-8 錯誤處理防止多模組同時執行時崩潰
5. ✅ **文檔價值**: 輸出本身就是資料來源的文檔

### OpenSpec 規範更新

此變更屬於**格式/輸出變更**，已更新以下文檔：
- ✅ `openspec/project.md`: 更新輸出格式範例與規範說明

**不需要 spec deltas**: 此專案目前尚未建立正式的 capability specs (`openspec/specs/`)，因此此變更直接更新 project.md 中的格式規範即可。未來若建立正式的輸出格式 capability spec，可參考此 change proposal 作為歷史記錄。
