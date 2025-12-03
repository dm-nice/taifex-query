# [模組名稱] 開發規格

> **模組代號**: `fXX_fetcher`  
> **資料來源**: [資料源名稱]  
> **難度**: ⭐⭐☆☆☆ (1-5 星)

## 📋 專案目標
簡述本模組的目標，例如：抓取 **[資料名稱]** 的 **[特定欄位]**。

## 📂 交付檔案
請依照以下命名規則建立檔案：
- **檔名**: `fXX_fetcher_dev.py`
- **MODULE 變數**: `"fXX_fetcher_dev"`

## 📊 資料來源規格
- **URL**: `https://example.com/path?param=value`
- **抓取方式**: [HTML 表格爬蟲 / API / JSON / CSV 等]
- **表格特徵**: [描述表格結構，例如：多層表頭 (MultiIndex)、單層表頭等]
- **更新頻率**: [每日 / 每週 / 即時]

## 🔍 需抓取的欄位定義

| 類別 | 欄位名稱 | 說明 | 資料類型 | 範例值 |
|------|---------|------|---------|--------|
| 篩選條件 | [欄位名] | 用於篩選特定資料 | str | "外資及陸資" |
| 目標資料 | [欄位名] | [說明] | int | 18808 |
| 目標資料 | [欄位名] | [說明] | int | 48032 |

## 🛠️ 開發規範

### 1. 繼承與介面
您的程式碼必須繼承 `modules.base.BaseFetcher` 並實作 `fetch` 方法。

```python
from modules.base import BaseFetcher, FetchResult

MODULE = "fXX_fetcher_dev"  # 必須與檔名一致 (不含 .py)

class [ClassName]Fetcher(BaseFetcher):
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
            summary="[簡短摘要，例如：F1: 台指期外資淨額：-29224]",
            source="[資料源名稱，例如：TAIFEX]"
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
    ...
except Exception as e:
    return FetchResult(
        module=MODULE,
        date=date,
        status="fail",
        error=str(e),
        data={},
        source="[資料源名稱]"
    ).to_dict()
```

## 🎯 特殊處理邏輯
（如果有特殊的資料處理需求，請在此說明）

例如：
- 需要處理多層表頭 (MultiIndex)
- 需要計算衍生欄位（例如：多空淨額 = 多方口數 - 空方口數）
- 需要處理特殊字元或編碼問題

## 🧪 測試案例

### 測試日期與預期結果
請使用以下日期進行測試，確保結果符合預期：

| 測試日期 | 預期狀態 | 預期資料 | 備註 |
|---------|---------|---------|------|
| 2025-11-28 | success | 外資多方口數: 18268 | 正常交易日 |
| 2025-11-30 | fail | - | 週六，無交易 |

### 自行測試 (必做)
請確保您的環境已安裝 `pytest`。在專案根目錄執行：

```bash
# 測試您的模組
pytest dev/fXX_fetcher_dev.py
```

**驗收標準：**
1. 測試結果必須為 **PASSED**。
2. 產出的 JSON 格式必須完全符合上述定義。

## 📦 交付內容
1. `fXX_fetcher_dev.py` (您的實作檔案)
2. 任何新增的依賴套件 (若有使用標準庫以外的套件，請註明)

## 📝 參考資料
（如果有相關的官方文件或參考連結，請列在此處）

- [資料源官方網站](https://example.com)
- [API 文件](https://example.com/api-docs)
