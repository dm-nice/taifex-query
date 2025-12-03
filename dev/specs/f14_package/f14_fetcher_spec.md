# f14_fetcher 開發規格

> **模組代號**: `f14_fetcher`  
> **資料來源**: 台灣期貨交易所 (TAIFEX) - 期貨每日交易行情  
> **難度**: ⭐⭐⭐☆☆ (3/5)

## 📋 專案目標
抓取 **台指期貨 (TX) 當日收盤價 (Day N Close)**。

## 📂 交付檔案
請依照以下命名規則建立檔案，並將其放置於**本目錄 (與本規格書相同目錄)**：
- **檔名**: `f14_fetcher_dev.py`
- **MODULE 變數**: `"f14_fetcher_dev"`
- **存放位置**: 請直接存放在本目錄下 (即 `f14_package/` 根目錄)

## 📊 資料來源規格
- **URL**: `https://www.taifex.com.tw/cht/3/futDailyMarketReport`
- **抓取方式**: HTML 表格爬蟲 或 API（需自行研究正確的請求方式）
- **目標商品**: 臺股期貨 (TX)
- **到期月份**: 當月近月合約（例如：202512）
- **目標欄位**: 收盤價
- **更新頻率**: 每日（交易日）

> [!IMPORTANT]
> **資料抓取挑戰**：
> 此網頁可能需要特定的查詢參數（例如 `queryDate=YYYY/MM/DD`）或使用 POST 請求。
> 請自行研究正確的請求方式，確保能穩定抓取到 TX 期貨的收盤價。

## 🔍 需抓取的欄位定義

| 類別 | 欄位名稱 | 說明 | 資料類型 | 範例值 |
|------|---------|------|---------|--------|
| 篩選條件 | 商品代號 | 用於篩選 **「TX」** 或 **「臺股期貨」** | str | "TX" |
| 篩選條件 | 到期月份 | 當月近月合約 | str | "202512" |
| 目標資料 | 收盤價 | 台指期貨當日收盤價 | float | 27758.0 |

## 🛠️ 開發規範

### 1. 繼承與介面
您的程式碼必須繼承 `modules.base.BaseFetcher` 並實作 `fetch` 方法。

```python
from modules.base import BaseFetcher, FetchResult

MODULE = "f14_fetcher_dev"  # 必須與檔名一致 (不含 .py)

class TXFuturesFetcher(BaseFetcher):
    def fetch(self, date: str) -> dict:
        # 實作抓取邏輯
        # ...
        return FetchResult(
            module=MODULE,
            date=date,
            status="success",  # 或 "fail"
            data={
                "台指期貨收盤價": 27758.0
            },
            summary="F14: 台指期貨收盤價：27758.0",
            source="TAIFEX"
        ).to_dict()
```

> [!CAUTION]
> **重要：data 的 key 名稱必須完全一致！**
> - ✅ 正確：`"台指期貨收盤價"`
> - ❌ 錯誤：`"期貨收盤價"`, `"TX收盤價"`, `"收盤價"` (系統會無法讀取資料)
> 
> 請務必使用上方範例中的 **exact key 名稱**，否則驗收會失敗。

### 2. 錯誤處理
- 若抓取失敗或無資料，請回傳 `status="fail"` 並在 `error` 欄位註明原因。
- 請勿直接拋出 Exception 導致程式崩潰，應捕捉異常並回傳錯誤結果。

```python
try:
    # 抓取邏輯
    url = f"https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate={date.replace('-', '/')}"
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

### 1. 商品代號篩選
需要從表格中找到商品代號為 **「TX」** 或 **「臺股期貨」** 的行。

### 2. 到期月份選擇
- 應選擇 **當月近月合約**（最接近的到期月份）
- 例如：2025年12月應選擇 202512 合約

### 3. 資料型別轉換
收盤價可能包含千分位逗號，需要移除後轉為 float：
```python
def to_float(v):
    if pd.isna(v):
        return 0.0
    return float(str(v).replace(',', '').strip())
```

### 4. 網頁請求方式
此網頁可能需要：
- 帶入日期參數：`queryDate=YYYY/MM/DD`
- 或使用 POST 請求
- 請自行測試並找出正確的請求方式

## 🧪 測試案例

### 測試日期與預期結果
請使用以下日期進行測試，確保結果符合預期：

| 測試日期 | 預期狀態 | 預期資料 | 備註 |
|---------|---------|---------|------|
| 2025-12-03 | success | 台指期貨收盤價: 27758.0 | 正常交易日 |
| 2025-12-07 | success | 台指期貨收盤價: [實際值] | 正常交易日 |
| 2025-12-08 | fail | - | 週日，無交易 |

### 自行測試 (必做)
請確保您的環境已安裝 `pytest`。在專案根目錄執行：

```bash
# 測試您的模組
pytest dev/f14_fetcher_dev.py
```

**驗收標準：**
1. 測試結果必須為 **PASSED**。
2. 產出的 JSON 格式必須完全符合上述定義。
3. 執行 `python run.py 2025-12-03 dev --module f14_fetcher_dev` 後，`data/` 目錄產生的 JSON 檔案數值不是 "-"。

## 📦 交付內容
1. `f14_fetcher_dev.py` (您的實作檔案)
2. 任何新增的依賴套件 (若有使用標準庫以外的套件，請註明)
3. **說明文件**：簡短說明您使用的抓取方式（GET/POST、參數格式等）

## ⚠️ 外包注意事項 (Q&A)

針對外包商常見問題，在此統一說明：

1. **Q: 是否需要額外的測試數據或 API 測試工具？**
   - **A**: 不需要。
     - 測試數據：請直接使用本規格書「🧪 測試案例」章節提供的日期。
     - 工具：使用瀏覽器開發者工具 (F12) 觀察 Network 請求即可。

2. **Q: 是否有特定的錯誤處理需求（例如：網路錯誤、數據格式錯誤）？**
   - **A**: 是，非常重要。
     - 請參閱「⚙️ 開發前須知 > 錯誤處理需求」章節。
     - 必須捕捉 ConnectionError, Timeout, ValueError 等異常。
     - **禁止**直接讓程式 Crash，必須回傳 `status="fail"` 的 `FetchResult`。

3. **Q: 是否需要支援多語系（例如：中文與英文）？**
   - **A**: 不需要。
     - 本專案僅需支援 **繁體中文**。
     - 錯誤訊息、Summary、Data Key 皆使用中文即可。

## 📝 參考資料
- [台灣期貨交易所 - 期貨每日交易行情](https://www.taifex.com.tw/cht/3/futDailyMarketReport)
- 建議先手動測試網頁，確認正確的請求方式後再開始開發
