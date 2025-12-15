# F15 模組開發規格書

**模組名稱**: f15_fetcher_dev.py
**功能**: 台積電當日漲跌價差抓取模組
**版本**: v1.0
**最後更新**: 2025-12-15

---

## 📋 目錄

1. [模組概述](#模組概述)
2. [資料來源](#資料來源)
3. [核心功能](#核心功能)
4. [函式規格](#函式規格)
5. [資料結構](#資料結構)
6. [輸出格式](#輸出格式)
7. [錯誤處理](#錯誤處理)
8. [使用範例](#使用範例)
9. [測試案例](#測試案例)
10. [維護指南](#維護指南)

---

## 模組概述

### 用途

`f15_fetcher_dev.py` 是用於抓取**台積電 (股票代號 2330)** 當日漲跌價差的資料抓取模組。

### 主要特性

- ✅ 從 TWSE (台灣證券交易所) 官方 API 抓取資料
- ✅ 提供統一的 `fetch(date: str) -> str` 介面
- ✅ 返回當日漲跌價差資訊
- ✅ 完整的錯誤處理和日誌記錄
- ✅ 支援 TypedDict 類型提示
- ✅ UTF-8 重複包裝防護

### 設計原則

基於 **F01 v7.0 架構**，遵循以下原則：
1. **統一介面**: 所有 fetcher 模組使用相同的函數簽章
2. **錯誤容錯**: 錯誤以文字訊息返回，不拋出例外
3. **日誌完整**: 記錄所有操作和錯誤資訊
4. **格式統一**: 輸出格式符合 run.py 要求

---

## 資料來源

### TWSE API

**API 端點**:
```
https://www.twse.com.tw/exchangeReport/STOCK_DAY
```

**請求參數**:
- `response`: json (固定值)
- `date`: YYYYMMDD (查詢日期)
- `stockNo`: 2330 (台積電股票代號)

**完整範例**:
```
https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=20251215&stockNo=2330
```

### 資料格式

**回應結構**:
```json
{
  "stat": "OK",
  "date": "114年12月",
  "title": "114年12月 2330 各日成交資訊",
  "fields": [
    "日期",
    "成交股數",
    "成交金額",
    "開盤價",
    "最高價",
    "最低價",
    "收盤價",
    "漲跌價差",
    "成交筆數"
  ],
  "data": [
    [
      "114/12/15",
      "46,234,589",
      "67,123,456,789",
      "1,450.00",
      "1,455.00",
      "1,445.00",
      "1,450.00",
      "-30.00",
      "45,678"
    ]
  ]
}
```

### 欄位說明

| 欄位索引 | 欄位名稱 | 說明 | 範例 |
|---------|---------|------|------|
| 0 | 日期 | 民國年格式 | "114/12/15" |
| 1 | 成交股數 | 當日成交股數 | "46,234,589" |
| 2 | 成交金額 | 當日成交總金額 | "67,123,456,789" |
| 3 | 開盤價 | 當日開盤價格 | "1,450.00" |
| 4 | 最高價 | 當日最高價格 | "1,455.00" |
| 5 | 最低價 | 當日最低價格 | "1,445.00" |
| 6 | 收盤價 | 當日收盤價格 | "1,450.00" |
| 7 | **漲跌價差** | 相對前日價格變化 | "-30.00" |
| 8 | 成交筆數 | 當日成交筆數 | "45,678" |

### 漲跌價差格式

| 值 | 意義 | 處理方式 |
|----|------|---------|
| "+30.00" | 上漲 30 元 | 顯示 "+30.00" |
| "-30.00" | 下跌 30 元 | 顯示 "-30.00" |
| "X" | 不比價 (新上市/特殊情況) | 顯示 "0" |
| "0.00" | 平盤 | 顯示 "0" |

---

## 核心功能

### 1. fetch(date: str) -> str

**主要入口函數**

從 TWSE API 抓取台積電股票資料並返回漲跌價差。

**參數**:
- `date` (str): 查詢日期，格式 YYYY-MM-DD

**返回值**:
- `str`: 格式化的文字結果

**特性**:
- ✅ 自動轉換日期格式（YYYY-MM-DD → YYYYMMDD）
- ✅ 自動處理民國年/西元年轉換
- ✅ 假日自動使用最後交易日資料
- ✅ 完整錯誤處理和日誌

**流程**:
```
1. 日期格式轉換 (YYYY-MM-DD → YYYYMMDD)
2. 呼叫 fetch_stock_data() 抓取資料
3. 依據狀態格式化輸出:
   - success → format_f15_output(success)
   - failed → format_f15_output(failed)
   - error → format_f15_output(error + context)
4. 返回文字結果
```

---

### 2. fetch_stock_data(date: str, timeout: int) -> FetchResultDict

**資料抓取核心函數**

從 TWSE API 抓取原始資料並解析。

**參數**:
- `date` (str): 查詢日期 (YYYY-MM-DD)
- `timeout` (int): 請求逾時秒數，預設 30

**返回值**:
- `FetchResultDict`: 包含狀態和資料的字典

**處理邏輯**:
1. **日期轉換**: YYYY-MM-DD → YYYYMMDD
2. **API 請求**: 發送 HTTP GET 請求
3. **狀態檢查**: 檢查 API 回應狀態
4. **資料驗證**: 確認有資料可用
5. **日期比對**: 尋找目標日期資料
6. **欄位解析**: 提取漲跌價差等欄位
7. **錯誤處理**: 5 層異常處理機制

**異常處理**:
- `requests.Timeout` → 連線逾時錯誤
- `requests.HTTPError` → HTTP 錯誤
- `requests.RequestException` → 網路請求失敗
- `ValueError` → 日期格式錯誤
- `Exception` → 系統錯誤

---

### 3. format_f15_output(...) -> str

**輸出格式化函數**

將抓取結果轉換為統一文字格式。

**參數**:
- `date` (str): 查詢日期
- `status` (str): 狀態 ("success"/"failed"/"error")
- `data` (Optional[StockDataDict]): 成功時的資料
- `error` (Optional[str]): 失敗時的錯誤訊息
- `timestamp` (Optional[str]): 異常時間戳
- `context` (Optional[ErrorContextDict]): 異常上下文

**返回值**:
- `str`: 格式化的文字字串

**格式規則**:

1. **成功格式**:
   ```
   {date}  F15: 台積電當日漲跌價差 : {change} 元 [TWSE]
   ```
   範例: `"2025.12.15  F15: 台積電當日漲跌價差 : -30.00 元 [TWSE]"`

2. **失敗格式**:
   ```
   F15 錯誤: {error} [TWSE]
   ```
   範例: `"F15 錯誤: 該日無交易資料（可能是假日或休市日） [TWSE]"`

3. **異常格式**:
   ```
   F15 錯誤: {error} [TWSE] ({timestamp})
   ```
   範例: `"F15 錯誤: 連線逾時，請檢查網路連線 [TWSE] (2025-12-15 14:30:45)"`

4. **異常+上下文格式**:
   ```
   F15 錯誤: {error} [TWSE] ({timestamp}, {context})
   ```
   範例: `"F15 錯誤: 連線逾時，請檢查網路連線 [TWSE] (2025-12-15 14:30:45, timeout=30s)"`

---

### 4. 輔助函數

#### parse_price_change(value: str) -> str
**功能**: 解析並標準化漲跌價差值

**處理邏輯**:
- `"+30.00"` → `"+30.00"`
- `"-30.00"` → `"-30.00"`
- `"X"` → `"0"` (不比價)
- `"0.00"` → `"0"`

#### convert_date_format(date_str: str) -> str
**功能**: YYYY-MM-DD → YYYYMMDD

**範例**:
- `"2025-12-15"` → `"20251215"`

#### convert_roc_date_to_ad(roc_date: str) -> str
**功能**: 民國年 → 西元年

**範例**:
- `"114/12/15"` → `"2025-12-15"`

---

## 資料結構

### StockDataDict (TypedDict)

```python
class StockDataDict(TypedDict):
    """股票資料字典結構"""
    price_change: str      # 漲跌價差 (必須)
    open_price: str       # 開盤價
    high_price: str       # 最高價
    low_price: str        # 最低價
    close_price: str      # 收盤價
    source: str           # 資料來源
```

### ErrorContextDict (TypedDict)

```python
class ErrorContextDict(TypedDict, total=False):
    """錯誤上下文字典"""
    timeout: int          # 逾時秒數
    status_code: int      # HTTP 狀態碼
    step: str             # 失敗步驟
    error_type: str       # 異常類型
```

### FetchResultDict (TypedDict)

```python
class FetchResultDict(TypedDict, total=False):
    """fetch 結果字典"""
    module: str           # 模組 ID ("f15")
    date: str             # 查詢日期
    status: str           # "success"/"failed"/"error"
    summary: str          # 成功摘要
    error: str            # 錯誤訊息
    data: StockDataDict   # 成功資料
    source: str           # 資料來源
    timestamp: str        # 時間戳
    context: ErrorContextDict  # 錯誤上下文
```

---

## 輸出格式

### 成功輸出

**格式**:
```
{日期}  F15: 台積電當日漲跌價差 : {漲跌} 元 [TWSE]
```

**範例**:
```
2025.12.15  F15: 台積電當日漲跌價差 : -30.00 元 [TWSE]
2025.12.16  F15: 台積電當日漲跌價差 : +25.00 元 [TWSE]
2025.12.17  F15: 台積電當日漲跌價差 : 0 元 [TWSE]
```

### 失敗輸出

**格式**:
```
F15 錯誤: {錯誤訊息} [TWSE]
```

**範例**:
```
F15 錯誤: 該日無交易資料（可能是假日或休市日） [TWSE]
F15 錯誤: API 返回錯誤: INVALID_DATE [TWSE]
```

### 異常輸出

**格式**:
```
F15 錯誤: {錯誤訊息} [TWSE] ({時間戳}, {上下文})
```

**範例**:
```
F15 錯誤: 連線逾時，請檢查網路連線 [TWSE] (2025-12-15 14:30:45, timeout=30s)
F15 錯誤: HTTP 錯誤 500 [TWSE] (2025-12-15 14:32:10, status_code=500)
F15 錯誤: 網路請求失敗，請檢查網路連線 [TWSE] (2025-12-15 14:35:00, error_type=ConnectionError)
```

---

## 錯誤處理

### 錯誤分類

| 錯誤類型 | 狀態 | 原因 | 解決方案 |
|---------|------|------|---------|
| 日期格式錯誤 | error | 輸入非 YYYY-MM-DD | 檢查日期格式 |
| 連線逾時 | error | 網路延遲/TWSE 無回應 | 檢查網路、稍後重試 |
| HTTP 錯誤 | error | 伺服器返回 4xx/5xx | 檢查 API 端點 |
| JSON 解析失敗 | error | 資料格式改變 | 更新解析邏輯 |
| 無交易資料 | failed | 假日或休市日 | 改查交易日期 |
| API 錯誤 | failed | API 返回非 OK 狀態 | 檢查 API 狀態 |
| 系統錯誤 | error | 未預期的異常 | 檢查日誌詳情 |

### 5 層異常處理機制

```python
try:
    # 1. 正常流程
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    data = response.json()

except requests.Timeout:
    # 2. 連線逾時
    return error with timeout context

except requests.HTTPError as e:
    # 3. HTTP 錯誤
    return error with status_code context

except requests.RequestException as e:
    # 4. 網路請求失敗
    return error with error_type context

except Exception as e:
    # 5. 系統錯誤
    return error with error_type context
```

### 日誌記錄

**INFO 級別**:
- 模組啟動
- 開始抓取資料
- 成功抓取資料
- 輸出結果

**WARNING 級別**:
- API 返回非 OK 狀態
- 找不到目標日期資料（使用最後交易日）
- 失敗情況

**ERROR 級別**:
- 連線逾時
- HTTP 錯誤
- 網路請求失敗
- 系統錯誤

**DEBUG 級別**:
- API URL 和參數
- 目標民國年日期
- 詳細股價資料

---

## 使用範例

### Example 1 - 基本使用

```python
from f15_fetcher_dev import fetch

# 抓取 2025-12-15 的資料
result = fetch("2025-12-15")
print(result)

# 輸出:
# 2025.12.15  F15: 台積電當日漲跌價差 : -30.00 元 [TWSE]
```

### Example 2 - 假日查詢

```python
# 查詢週六（假日）
result = fetch("2025-12-14")
print(result)

# 輸出（自動使用最後交易日資料）:
# 2025.12.14  F15: 台積電當日漲跌價差 : -30.00 元 [TWSE]
```

### Example 3 - 命令列執行

```bash
# 指定日期
python f15_fetcher_dev.py 2025-12-15

# 使用今天日期
python f15_fetcher_dev.py
```

### Example 4 - 整合到 run.py

```python
# run.py 自動載入
# 模組位於 C:\Taifex\dev\f15_fetcher_dev.py

# 執行
python run.py 2025-12-15 dev --module f15_fetcher_dev

# 輸出檔案: C:\Taifex\data\2025-12-15_HHMM_f15_fetcher_dev.txt
# 內容: 2025.12.15  F15: 台積電當日漲跌價差 : -30.00 元 [TWSE]
```

---

## 測試案例

### Test Case 1 - 正常交易日

**輸入**: `fetch("2025-12-15")`
**預期**: `"2025.12.15  F15: 台積電當日漲跌價差 : -30.00 元 [TWSE]"`
**狀態**: ✅ PASS

### Test Case 2 - 假日（週末）

**輸入**: `fetch("2025-12-14")`
**預期**: 使用最後交易日資料
**狀態**: ✅ PASS

### Test Case 3 - 上漲情況

**輸入**: `fetch("2025-12-XX")` (上漲日)
**預期**: `"2025.12.XX  F15: 台積電當日漲跌價差 : +25.00 元 [TWSE]"`
**狀態**: 待測試

### Test Case 4 - 平盤情況

**輸入**: `fetch("2025-12-XX")` (平盤日)
**預期**: `"2025.12.XX  F15: 台積電當日漲跌價差 : 0 元 [TWSE]"`
**狀態**: 待測試

### Test Case 5 - 網路錯誤

**模擬**: 斷網情況
**預期**: `"F15 錯誤: 網路請求失敗，請檢查網路連線 [TWSE] (timestamp, error_type=...)"`
**狀態**: 待測試

---

## 維護指南

### 定期檢查項目

**每月**:
- ✅ 驗證 TWSE API 端點是否變更
- ✅ 檢查資料格式是否改變
- ✅ 測試假日和交易日情況

**每季**:
- ✅ 檢查日誌記錄是否正常
- ✅ 驗證錯誤處理機制
- ✅ 更新依賴套件版本

**每年**:
- ✅ 全面測試所有功能
- ✅ 更新文檔和範例
- ✅ 效能優化評估

### API 變更應對

如果 TWSE API 格式改變：

1. **欄位順序變更**:
   - 更新 `fetch_stock_data()` 中的欄位索引
   - 參考 `fields` 欄位動態解析

2. **日期格式變更**:
   - 更新 `convert_roc_date_to_ad()` 函數
   - 調整日期比對邏輯

3. **新增欄位**:
   - 評估是否需要使用新欄位
   - 更新 `StockDataDict` 結構

### 問題排查

**問題**: 連線逾時頻繁發生
**排查**:
1. 檢查網路連線
2. 增加 timeout 參數（預設 30 秒）
3. 檢查 TWSE 網站狀態

**問題**: 資料解析失敗
**排查**:
1. 檢查 API 回應格式
2. 查看 DEBUG 日誌
3. 驗證欄位索引是否正確

**問題**: 假日資料不正確
**排查**:
1. 確認是否為交易日
2. 檢查最後交易日邏輯
3. 驗證日期轉換函數

---

## 版本歷史

### v1.0 (2025-12-15) - 初始版本

**新增功能**:
- ✅ 基於 F01 v7.0 架構開發
- ✅ TWSE API 資料抓取
- ✅ 台積電漲跌價差提取
- ✅ 完整錯誤處理機制
- ✅ TypedDict 類型提示
- ✅ UTF-8 重複包裝防護
- ✅ 5 層異常處理
- ✅ 詳細日誌記錄

**測試狀態**:
- ✅ 基本功能測試通過
- ✅ 假日處理測試通過
- ⏳ 完整測試套件待建立

**已知限制**:
- 僅支援台積電 (2330) 單一股票
- 無歷史資料批次查詢功能
- 依賴 TWSE API 可用性

---

**維護者**: 全端架構師 (Claude)
**創建日期**: 2025-12-15
**文檔版本**: 1.0
**狀態**: ✅ Active
