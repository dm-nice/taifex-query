# f01_fetcher 開發規格

> **模組代號**: `f01_fetcher`  
> **資料來源**: 台灣期貨交易所 (TAIFEX)  
> **難度**: ⭐⭐☆☆☆ (2/5)

## 📋 專案目標
抓取 **台指期貨外資的未平倉淨口數 (OI)**。

## 📂 交付檔案
請依照以下命名規則建立檔案：
- **檔名**: `f01_fetcher_dev.py`
- **MODULE 變數**: `"f01_fetcher_dev"`

## 📊 資料來源規格
- **URL**: `https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date=YYYY/MM/DD`
- **抓取方式**: HTML 表格爬蟲 (建議使用 `requests` + `pandas` 或 `BeautifulSoup`)
- **表格特徵**: 多層表頭 (MultiIndex)，需精確定位「外資」身份別
- **更新頻率**: 每日（交易日）

## 🔍 需抓取的欄位定義

| 類別 | 欄位名稱 | 說明 | 資料類型 | 範例值 |
|------|---------|------|---------|--------|
| 篩選條件 | 身份別 | 用於篩選 **「外資及陸資」** 的行 | str | "外資及陸資" |
| 目標資料 | 未平倉餘額 > 多方 > 口數 | 外資多方未平倉口數 | int | 18808 |
| 目標資料 | 未平倉餘額 > 空方 > 口數 | 外資空方未平倉口數 | int | 48032 |
| 計算欄位 | 多空淨額 | 多方口數 - 空方口數 | int | -29224 |

## 🛠️ 開發規範

### 1. 繼承與介面
您的程式碼必須繼承 `modules.base.BaseFetcher` 並實作 `fetch` 方法。

```python
from modules.base import BaseFetcher, FetchResult

MODULE = "f01_fetcher_dev"  # 必須與檔名一致 (不含 .py)

class TaifexFetcher(BaseFetcher):
    def fetch(self, date: str) -> dict:
        # 實作抓取邏輯
        # ...
        return FetchResult(
            module=MODULE,
            date=date,
            status="success",  # 或 "fail"
            data={
                "外資多方口數": 18808,
                "外資空方口數": 48032,
                "外資多空淨額": -29224
            },
            summary="F1: 台指期外資淨額：-29224（多：18808，空：48032）",
            source="TAIFEX"
        ).to_dict()
```

> [!CAUTION]
> **重要：data 的 key 名稱必須完全一致！**
> - ✅ 正確：`"外資多方口數"`, `"外資空方口數"`, `"外資多空淨額"`
> - ❌ 錯誤：`"外資多單口數"`, `"外資空單口數"` (系統會無法讀取資料)
> 
> 請務必使用上方範例中的 **exact key 名稱**，否則驗收會失敗。

### 2. 錯誤處理
- 若抓取失敗或無資料，請回傳 `status="fail"` 並在 `error` 欄位註明原因。
- 請勿直接拋出 Exception 導致程式崩潰，應捕捉異常並回傳錯誤結果。

```python
try:
    # 抓取邏輯
    url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={date.replace('-', '/')}"
    resp = requests.get(url, timeout=10)
    # ...
except Exception as e:
    return FetchResult(
        module=MODULE,
        date=date,
        status="fail",
        error=str(e),
        data={},
        source="TAIFEX"
    ).to_dict()
```

## 🎯 特殊處理邏輯

### 1. 多層表頭 (MultiIndex) 處理
台指期的表格使用 MultiIndex 結構，欄位名稱是 tuple 格式，例如：
```python
('Unnamed: 2_level_0', '身份別')
('未平倉餘額', '多方', '口數')
```

建議使用以下方式尋找欄位：
```python
# 找到身份別欄位
trader_col = None
for col in df.columns:
    if any('身份別' in str(c) for c in col):
        trader_col = col
        break
```

### 2. 身份別名稱
台指期的身份別欄位通常顯示為 **「外資及陸資」**，而不是「外資」。

建議優先找「外資及陸資」，找不到再嘗試「外資」：
```python
foreign_rows = df[df[trader_col] == '外資及陸資']
if len(foreign_rows) == 0:
    foreign_rows = df[df[trader_col] == '外資']
```

### 3. 資料型別轉換
從網頁抓取的資料可能包含千分位逗號，需要移除後轉為 int：
```python
def to_int(v):
    if pd.isna(v):
        return 0
    return int(str(v).replace(',', '').strip())
```

## 🧪 測試案例

### 測試日期與預期結果
請使用以下日期進行測試，確保結果符合預期：

| 測試日期 | 預期狀態 | 預期資料 | 備註 |
|---------|---------|---------|------|
| 2025-12-02 | success | 外資多方口數: 18808<br>外資空方口數: 48032<br>外資多空淨額: -29224 | 正常交易日 |
| 2025-11-30 | fail | - | 週六，無交易 |

### 自行測試 (必做)
請確保您的環境已安裝 `pytest`。在專案根目錄執行：

```bash
# 測試您的模組
pytest dev/f01_fetcher_dev.py
```

**驗收標準：**
1. 測試結果必須為 **PASSED**。
2. 產出的 JSON 格式必須完全符合上述定義。
3. 執行 `python run.py 2025-12-02 dev --module f01_fetcher_dev` 後，`data/` 目錄產生的 JSON 檔案數值不是 "-"。

## 📦 交付內容
1. `f01_fetcher_dev.py` (您的實作檔案)
2. 任何新增的依賴套件 (若有使用標準庫以外的套件，請註明)

## 📝 參考資料
- [台灣期貨交易所 - 三大法人交易資訊](https://www.taifex.com.tw/cht/3/futContractsDate)
