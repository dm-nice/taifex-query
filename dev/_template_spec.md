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

## ⚙️ 開發前須知

### 測試數據與工具
- **測試數據**: 請使用下方「🧪 測試案例」章節提供的測試日期進行開發
- **API 測試工具**: 建議使用瀏覽器開發者工具 (F12) 或 Postman 測試 API，無需額外工具
- **依賴套件**: 專案已安裝常用套件 (`requests`, `pandas`, `beautifulsoup4`)，若需其他套件請在交付時註明

### 錯誤處理需求
> [!IMPORTANT]
> **必須處理以下錯誤情境**：
> 1. **網路錯誤**: 連線逾時、HTTP 錯誤 (使用 `timeout=10` 參數)
> 2. **資料格式錯誤**: 找不到目標欄位、資料為空、格式異常
> 3. **非交易日**: 週末或國定假日無資料時，回傳 `status="fail"` 並註明原因
> 
> **所有錯誤都必須捕捉並回傳 `FetchResult` 物件，不可直接拋出 Exception。**

### 語系支援
- **僅需支援繁體中文**: 所有 data key 名稱、summary、error 訊息皆使用繁體中文
- **無需多語系**: 本專案不需要英文或其他語言支援

### 開發環境
- **Python 版本**: 3.12+
- **虛擬環境**: 請使用專案提供的 `venv32` 虛擬環境
- **測試框架**: pytest (已安裝)

## 🛠️ 開發規範

### 1. 必須實作的介面

您的程式碼必須實作 `fetch` 函式，回傳統一格式的文字字串。

```python
from typing import Dict, Optional

MODULE_ID = "fxx"  # 模組代號 (小寫)
MODULE_NAME = "fxx_fetcher_dev"  # 必須與檔名一致 (不含 .py)


def format_fxx_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
    """
    格式化輸出為統一文字格式

    Args:
        date: 日期 (YYYY-MM-DD)
        status: 狀態 ("success" / "failed" / "error")
        data: 成功時的資料字典
        error: 失敗時的錯誤訊息

    Returns:
        統一格式文字字串
    """
    date_formatted = date.replace("-", ".")  # 2025-12-03 → 2025.12.03

    if status == "success" and data:
        # 根據您的模組特性格式化輸出
        # 範例：
        value = data.get("some_value", 0)
        return f"[ {date_formatted}  FXX{描述} {value:,}   source: {來源} ]"
    else:
        error_msg = error or "未知錯誤"
        return f"[ {date_formatted}  FXX 錯誤: {error_msg}   source: {來源} ]"


def fetch(date: str) -> str:
    """
    抓取指定日期的資料

    Args:
        date: 查詢日期，格式 YYYY-MM-DD

    Returns:
        統一格式的文字字串
        格式: [ YYYY.MM.DD  FXX{描述}   source: {來源} ]
    """
    # 實作抓取邏輯
    # ...

    # 成功時
    data = {
        "some_value": 12345,
        # ... 其他資料
    }
    return format_fxx_output(date, "success", data=data)
```

> [!IMPORTANT]
> **重要規範**：
> - ✅ 回傳類型必須是 `str`（統一文字格式）
> - ✅ 模組內部可以使用 dict 處理邏輯，最後轉換為文字
> - ✅ 所有錯誤都必須轉換為文字格式回傳
> - ❌ 不可拋出例外，所有錯誤都用錯誤格式文字表示

### 2. 錯誤處理

所有錯誤都必須捕捉並轉換為統一的文字格式回傳，不可拋出例外。

```python
def fetch(date: str) -> str:
    """抓取指定日期的資料"""

    # 1. 驗證日期格式
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_fxx_output(date, "error", error="日期格式錯誤，請使用 YYYY-MM-DD")

    try:
        # 2. 發送 HTTP 請求
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # 3. 解析資料
        tables = pd.read_html(response.text)
        if len(tables) == 0:
            return format_fxx_output(date, "failed", error="該日無交易資料（可能是假日或休市日）")

        # 4. 提取資料
        data = extract_data(tables[0], date)
        if data.get("status") == "success":
            return format_fxx_output(date, "success", data=data.get("data"))
        else:
            return format_fxx_output(date, "failed", error=data.get("error", "資料提取失敗"))

    except requests.Timeout:
        return format_fxx_output(date, "error", error="連線逾時，請檢查網路連線")

    except requests.HTTPError as e:
        return format_fxx_output(date, "error", error=f"HTTP 錯誤 {e.response.status_code}")

    except Exception as e:
        logger.exception("未預期的錯誤")
        return format_fxx_output(date, "error", error=f"未預期的錯誤: {str(e)}")
```

**錯誤處理規範**：
- ✅ 所有錯誤都必須轉換為文字格式
- ✅ 使用適當的錯誤訊息（中文）
- ❌ 不可讓例外向上傳播
- ❌ 不可回傳 None 或其他類型

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
（如果有相關的官方文件或參考連結，請列在此處）

- [資料源官方網站](https://example.com)
- [API 文件](https://example.com/api-docs)
