# f01_fetcher_dev 開發規範書

## 📋 專案目標
本專案目標為抓取 **台指期貨外資的未平倉淨口數 (OI)**。
您將負責實作資料抓取的邏輯，並確保產出的資料格式符合系統要求。

## 📂 交付檔案結構
請依照以下結構進行開發與交付：

```text
project_root/
├── modules/
│   └── base.py          # [提供] 基礎類別定義 (BaseFetcher, FetchResult)
├── dev/
│   ├── _template.py     # [提供] 開發範本
│   └── f01_fetcher_dev.py # [交付] 您的實作檔案 (檔名需與模組變數一致)
└── ...
```

## 📊 數據來源規格
- **URL**: `https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date=YYYY/MM/DD`
- **抓取方式**: HTML 表格爬蟲 (建議使用 `requests` + `pandas` 或 `BeautifulSoup`)
- **表格特徵**: 多層表頭 (MultiIndex)，需精確定位「外資」身份別。

## 🔍 需抓取的欄位定義
| 類別 | 欄位名稱 | 說明 |
|------|--------|------|
| 身份別 | 身份別 | 用於篩選 **「外資及陸資」** 的行 |
| 未平倉餘額 | 多方 > 口數 | 外資多單未平倉口數 (需轉為 int) |
| 未平倉餘額 | 空方 > 口數 | 外資空方未平倉口數 (需轉為 int) |
| 未平倉餘額 | 多空淨額 > 口數 | 外資多空淨額 (需轉為 int) |

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
            status="success", # 或 "fail"
            data={
                "外資多方口數": 18268,
                "外資空方口數": 47300,
                "外資多空淨額": -29032
            },
            summary="F1: 台指期外資淨額：-29032...",
            source="TAIFEX"
        ).to_dict()
```

### 2. 錯誤處理
- 若抓取失敗或無資料，請回傳 `status="fail"` 並在 `error` 欄位註明原因。
- 請勿直接拋出 Exception 導致程式崩潰，應捕捉異常並回傳錯誤結果。

## 🧪 測試與驗收

### 自行測試 (必做)
請確保您的環境已安裝 `pytest`。在專案根目錄執行：

```bash
# 測試您的模組
pytest dev/f01_fetcher_dev.py
```

**驗收標準：**
1. 測試結果必須為 **PASSED**。
2. 產出的 JSON 格式必須完全符合上述定義。

## 📦 交付內容
1. `f01_fetcher_dev.py` (或是您命名的檔案)
2. 任何新增的依賴套件 (若有使用標準庫以外的套件)
