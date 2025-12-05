# [模組名稱] 開發規格

> **模組代號**: `fXX_fetcher`
> **資料來源**: [資料源名稱]
> **難度**: ⭐⭐☆☆☆ (1-5 星)

---

## 📖 使用說明

> 💡 **給外包開發者**：
> 1. 請先閱讀 [共同開發規範書](共同開發規範書_V1.md) 了解通用規範（快速參考章節 10 分鐘即可）
> 2. 本文件僅包含 **FXX 模組特定** 的需求與規格
> 3. 遇到問題請參考共同開發規範書的 FAQ 章節

---

## 📋 專案目標

簡述本模組的目標，例如：

抓取 **[資料名稱]** 的 **[特定欄位]**，用於分析 [用途說明]。

---

## 📂 交付檔案

請依照以下命名規則建立檔案：

- **檔名**: `fXX_fetcher_dev.py`
- **MODULE_ID 變數**: `"fxx"` (小寫)
- **存放位置**: `dev/` 目錄

---

## 📊 資料來源規格

### 基本資訊
- **URL**: `https://example.com/path?param=value`
- **抓取方式**: [HTML 表格爬蟲 / API / JSON / CSV 等]
- **表格特徵**: [描述表格結構，例如：多層表頭 (MultiIndex)、單層表頭等]
- **更新頻率**: [每日 / 每週 / 即時]
- **資料來源標記**: `source: "[來源名稱]"` (用於輸出格式)

### 挑戰與注意事項
> [!IMPORTANT]
> **資料抓取挑戰**：
> - [列出此模組的特殊挑戰，例如：需要特定參數、POST 請求、動態載入等]
> - [建議的解決方法或測試方式]

---

## 🔍 需抓取的欄位定義

| 類別 | 欄位名稱 | 說明 | 資料類型 | 範例值 |
|------|---------|------|---------|--------|
| 篩選條件 | [欄位名] | 用於篩選特定資料 | str | "外資及陸資" |
| 目標資料 | [欄位名] | [說明] | int | 18808 |
| 目標資料 | [欄位名] | [說明] | int | 48032 |

> [!CAUTION]
> **重要：欄位名稱必須完全一致！**
> - ✅ 正確：使用上表定義的 exact 名稱
> - ❌ 錯誤：自行簡化或改寫欄位名（系統會無法讀取資料）

---

## 📝 輸出格式定義

### 成功時
```
[ YYYY.MM.DD  FXX[具體描述 + 數值]   source: [來源] ]
```

**範例**：
```
[ 2025.12.03  FXX外資多方口數 18,268，空方口數 47,300   source: [來源] ]
```

### 失敗時
```
[ YYYY.MM.DD  FXX 錯誤: [錯誤訊息]   source: [來源] ]
```

**範例**：
```
[ 2025.11.30  FXX 錯誤: 該日無交易資料（可能是假日或休市日）   source: [來源] ]
```

---

## 🛠️ 實作程式碼範本

```python
"""
FXX模組：[模組說明]

資料來源：[來源名稱]
更新頻率：[頻率]
"""

import requests
import pandas as pd
from datetime import datetime
from typing import Dict, Optional

# 模組識別
MODULE_ID = "fxx"  # 小寫，對應模組代號
SOURCE = "[來源名稱]"  # 資料來源標記


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
    module_code = MODULE_ID.upper()  # fxx → FXX

    if status == "success" and data:
        # 🔧 根據您的模組需求客製化這裡的輸出格式
        # 範例：
        value1 = data.get("key1", 0)
        value2 = data.get("key2", 0)
        return f"[ {date_formatted}  {module_code}[描述] {value1:,} [單位]，{value2:,} [單位]   source: {SOURCE} ]"
    else:
        error_msg = error or "未知錯誤"
        return f"[ {date_formatted}  {module_code} 錯誤: {error_msg}   source: {SOURCE} ]"


def fetch(date: str) -> str:
    """
    抓取指定日期的資料

    Args:
        date: 查詢日期，格式 YYYY-MM-DD

    Returns:
        統一格式的文字字串
    """
    # 1. 驗證日期格式
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_fxx_output(date, "error", error="日期格式錯誤，請使用 YYYY-MM-DD")

    try:
        # 2. 發送 HTTP 請求
        url = f"[您的 URL]?date={date}"  # 🔧 修改為實際 URL
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # 3. 解析資料
        # 🔧 根據資料源類型選擇解析方式：
        # - HTML 表格: tables = pd.read_html(response.text)
        # - JSON: data = response.json()
        # - CSV: df = pd.read_csv(...)

        tables = pd.read_html(response.text)
        if len(tables) == 0:
            return format_fxx_output(date, "failed", error="該日無交易資料（可能是假日或休市日）")

        # 4. 提取目標資料
        df = tables[0]
        # 🔧 實作您的資料提取邏輯
        # ...

        # 5. 回傳成功結果
        data = {
            "key1": 12345,  # 🔧 替換為實際欄位
            "key2": 67890,
        }
        return format_fxx_output(date, "success", data=data)

    except requests.Timeout:
        return format_fxx_output(date, "error", error="連線逾時，請檢查網路連線")

    except requests.HTTPError as e:
        return format_fxx_output(date, "error", error=f"HTTP 錯誤 {e.response.status_code}")

    except Exception as e:
        return format_fxx_output(date, "error", error=f"未預期的錯誤: {str(e)}")


def main():
    """獨立測試用"""
    import sys
    test_date = sys.argv[1] if len(sys.argv) > 1 else '2025-12-03'
    result = fetch(test_date)
    print(result)


if __name__ == '__main__':
    main()
```

---

## 🎯 特殊處理邏輯

（如果有特殊的資料處理需求，請在此詳細說明）

### 1. [特殊需求 1]
- **問題**: [描述問題]
- **解決方法**: [說明如何處理]
- **範例代碼**:
```python
# 範例代碼
```

### 2. [特殊需求 2]
- **問題**: [描述問題]
- **解決方法**: [說明如何處理]

---

## 🧪 測試案例

### 測試日期與預期結果

請使用以下日期進行測試，確保結果符合預期：

| 測試日期 | 預期狀態 | 預期資料 | 備註 |
|---------|---------|---------|------|
| YYYY-MM-DD | success | [具體數值] | 正常交易日 |
| YYYY-MM-DD | success | [具體數值] | 正常交易日 |
| YYYY-MM-DD | failed | - | 週末/假日，無交易 |

### 測試方法

```bash
# 1. 獨立測試
python dev/fXX_fetcher_dev.py YYYY-MM-DD

# 2. 整合測試（驗收模式）
python run.py YYYY-MM-DD dev --module fXX_fetcher_dev

# 3. 檢查輸出
type data\YYYY-MM-DD_fXX_fetcher_dev.txt
```

---

## 📦 交付檢查清單

- [ ] `fXX_fetcher_dev.py` 檔案（已存放在 `dev/` 目錄）
- [ ] 獨立測試通過（執行 `python fXX_fetcher_dev.py` 無錯誤）
- [ ] 整合測試通過（執行 `python run.py ... dev` 產生正確輸出）
- [ ] 輸出格式符合規範（使用 [ YYYY.MM.DD FXX... ] 格式）
- [ ] 所有測試案例都通過
- [ ] 錯誤處理完整（不會拋出未處理的例外）
- [ ] 簡短說明文件（說明您使用的抓取方式與遇到的挑戰）

---

## ⚠️ 常見問題

### Q1: 資料抓取遇到問題怎麼辦？
**A**:
1. 使用瀏覽器開發者工具 (F12) → Network 標籤觀察請求
2. 確認 URL 參數格式是否正確
3. 檢查是否需要特定的 headers 或 cookies

### Q2: 輸出格式該如何調整？
**A**:
- 修改 `format_fxx_output()` 函式中成功時的輸出格式
- 確保包含所有必要元素：日期、模組代號、描述、數值、來源
- 參考 [F01 模組範例](f01_package/f01_fetcher_開發規範書.md)

### Q3: 如何處理多層表頭？
**A**:
```python
df.columns = df.columns.get_level_values(1)  # 取第二層
# 或
df.columns = ['_'.join(col).strip() for col in df.columns.values]  # 合併多層
```

---

## 📝 參考資料

- [共同開發規範書](共同開發規範書_V1.md) - 必讀！包含所有通用規範
- [F01 模組範例](f01_package/f01_fetcher_開發規範書.md) - 完整實作參考
- [資料源官方網站](https://example.com)
- [API 文件](https://example.com/api-docs)（如果有）

---

**範本版本**: 4.0
**最後更新**: 2025-12-05
**適用專案**: 台指期貨20因子預測系統
