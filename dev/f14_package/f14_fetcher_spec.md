# f14_fetcher 開發規格與交付說明

> **模組代號**: `f14_fetcher`  
> **資料來源**: 台灣期貨交易所 (TAIFEX) - 期貨每日交易行情  
> **難度**: ⭐⭐⭐☆☆ (3/5)

## 📋 專案目標
抓取 **台指期貨 (TX) 當日收盤價 (Day N Close)**。

## 🚀 開發流程指引

請依照以下步驟進行開發：

### 1. 閱讀順序
1. **README.md** - 了解整體架構與開發流程
2. **[共同開發規範書](../共同開發規範書_V1.md)** - 了解統一文字格式 v4.0 規範 ⭐
3. **本規格書** - 了解 F14 的具體需求與交付規定
4. **_template.py** - 作為開發起點

### 2. 設定開發環境
```bash
# 建議使用 Python 3.9+
pip install requests pandas pytest
```

### 3. 建立開發檔案
複製 `_template.py` 並重新命名為 `f14_fetcher_dev.py`，**並直接存放在本目錄下**：
```bash
cp _template.py f14_fetcher_dev.py
```

### 4. 實作與測試
- 根據下方的「資料來源規格」與「開發規範」實作 `fetch` 方法。
- 執行 pytest 測試：`pytest f14_fetcher_dev.py`

## 📂 交付檔案與清單
請依照以下命名規則建立檔案，並將其放置於**本目錄 (與本規格書相同目錄)**：

- **檔名**: `f14_fetcher_dev.py`
- **MODULE 變數**: `"f14_fetcher_dev"`
- **存放位置**: 請直接存放在本目錄下 (即 `f14_package/` 根目錄)

### 交付檢查清單
- [ ] `f14_fetcher_dev.py` 檔案（已存放在本目錄下）
- [ ] 實作 `fetch(date: str) -> str` 函式（回傳統一文字格式）
- [ ] 獨立測試通過（執行 `python f14_fetcher_dev.py` 無錯誤）
- [ ] 整合測試通過（執行 `python run.py ... dev` 產生正確輸出）
- [ ] 輸出格式符合規範（使用 [ YYYY.MM.DD F14... ] 格式）
- [ ] 錯誤處理完整（不會拋出未處理的例外）
- [ ] 簡短說明文件（說明您使用的抓取方式）

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

### 1. 必須實作的介面（統一文字格式 v4.0）

您的程式碼必須實作 `fetch(date: str) -> str` 函式，回傳統一格式的文字字串。

```python
from typing import Dict, Optional
from datetime import datetime
import requests
import pandas as pd

MODULE_ID = "f14"  # 模組代號（小寫）
SOURCE = "TAIFEX"


def format_f14_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
    """格式化輸出為統一文字格式"""
    date_formatted = date.replace("-", ".")  # 2025-12-03 → 2025.12.03

    if status == "success" and data:
        close_price = data.get("台指期貨收盤價", 0.0)
        return f"[ {date_formatted}  F14台指期貨收盤價 {close_price:,.1f}   source: {SOURCE} ]"
    else:
        error_msg = error or "未知錯誤"
        return f"[ {date_formatted}  F14 錯誤: {error_msg}   source: {SOURCE} ]"


def fetch(date: str) -> str:
    """
    抓取指定日期的台指期貨收盤價

    Returns:
        統一格式的文字字串
    """
    # 實作抓取邏輯
    # ...
    data = {"台指期貨收盤價": 27758.0}
    return format_f14_output(date, "success", data=data)
```

> [!CAUTION]
> **重要：data 的 key 名稱必須完全一致！**
> - ✅ 正確：`"台指期貨收盤價"`
> - ❌ 錯誤：`"期貨收盤價"`, `"TX收盤價"`, `"收盤價"` (系統會無法讀取資料)
> 
> 請務必使用上方範例中的 **exact key 名稱**，否則驗收會失敗。

### 2. 錯誤處理（必須遵守）

所有錯誤都必須轉換為統一文字格式回傳，**不可拋出例外**。

```python
def fetch(date: str) -> str:
    # 1. 驗證日期格式
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_f14_output(date, "error", error="日期格式錯誤，請使用 YYYY-MM-DD")

    try:
        # 2. 發送 HTTP 請求
        url = f"https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryDate={date.replace('-', '/')}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # 3. 解析資料
        tables = pd.read_html(response.text)
        if len(tables) == 0:
            return format_f14_output(date, "failed", error="該日無交易資料（可能是假日或休市日）")

        # ... 提取資料邏輯

    except requests.Timeout:
        return format_f14_output(date, "error", error="連線逾時，請檢查網路連線")

    except requests.HTTPError as e:
        return format_f14_output(date, "error", error=f"HTTP 錯誤 {e.response.status_code}")

    except Exception as e:
        return format_f14_output(date, "error", error=f"未預期的錯誤: {str(e)}")
```

**錯誤處理規範**：
- ✅ 所有錯誤都必須轉換為文字格式
- ✅ 使用中文錯誤訊息
- ❌ 不可讓例外向上傳播
- ❌ 不可回傳 None 或其他類型

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

## 🧪 測試案例與驗收標準

### 測試日期與預期結果
請使用以下日期進行測試，確保結果符合預期：

| 測試日期 | 預期狀態 | 預期資料 | 備註 |
|---------|---------|---------|------|
| 2025-12-03 | success | 台指期貨收盤價: 27758.0 | 正常交易日 |
| 2025-12-07 | success | 台指期貨收盤價: [實際值] | 正常交易日 |
| 2025-12-08 | fail | - | 週日，無交易 |

### 自行測試 (必做)

```bash
# 1. 獨立測試
python dev/f14_package/f14_fetcher_dev.py 2025-12-03

# 2. 整合測試（驗收模式）
python run.py 2025-12-03 dev --module f14_fetcher_dev

# 3. 檢查輸出
type data\2025-12-03_f14_fetcher_dev.txt
```

**驗收標準：**
1. 獨立測試通過（執行 `python f14_fetcher_dev.py 2025-12-03` 無錯誤）
2. 輸出格式符合統一文字格式規範
3. 執行 `python run.py 2025-12-03 dev --module f14_fetcher_dev` 後，`data/` 目錄產生的 `.txt` 檔案包含正確數據

## ⚠️ 外包注意事項 (Q&A)

針對外包商常見問題，在此統一說明：

1. **Q: 是否需要額外的測試數據或 API 測試工具？**
   - **A**: 不需要。
     - 測試數據：請直接使用本規格書「🧪 測試案例」章節提供的日期。
     - 工具：使用瀏覽器開發者工具 (F12) 觀察 Network 請求即可。

2. **Q: 是否有特定的錯誤處理需求（例如：網路錯誤、數據格式錯誤）？**
   - **A**: 是，非常重要。
     - 請參閱「🛠️ 開發規範 > 錯誤處理」章節。
     - 必須捕捉 ConnectionError, Timeout, ValueError 等異常。
     - **禁止**直接讓程式 Crash，必須回傳統一文字格式的錯誤訊息。

3. **Q: 是否需要支援多語系（例如：中文與英文）？**
   - **A**: 不需要。
     - 本專案僅需支援 **繁體中文**。
     - 錯誤訊息、Summary、Data Key 皆使用中文即可。

## 📝 參考資料
- [台灣期貨交易所 - 期貨每日交易行情](https://www.taifex.com.tw/cht/3/futDailyMarketReport)
- 建議先手動測試網頁，確認正確的請求方式後再開始開發
