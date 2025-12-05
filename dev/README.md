# 開發目錄說明

> **統一文字格式 v4.0** - 所有模組已升級到統一文字格式輸出

此目錄包含所有開發相關的文件、範本和驗收模組。

---

## 📂 目錄結構

```
dev/
├── README.md                    # 本文件
├── 共同開發規範書_V1.md         # 所有模組的通用開發規範 ⭐
├── _template_spec.md            # 新模組規格書範本
├── _template.py                 # 新模組程式碼範本
│
├── f01_package/                 # F01 模組開發包（範例）
│   ├── f01_fetcher_開發規範書.md
│   └── ... (其他 F01 相關檔案)
│
└── f14_package/                 # F14 模組開發包
    ├── f14_fetcher_spec.md      # F14 規格書
    ├── f14_fetcher_dev.py       # F14 開發版本
    └── _template.py             # F14 專用範本
```

---

## 🚀 快速開始

### 給新開發者

1. **閱讀核心文件**（必讀 ⭐）
   - [共同開發規範書_V1.md](共同開發規範書_V1.md) - 開頭有「快速參考」章節（10分鐘入門）

2. **參考完整範例**
   - 程式碼：[../modules/f01_fetcher.py](../modules/f01_fetcher.py)
   - 規格書：[f01_package/f01_fetcher_開發規範書.md](f01_package/f01_fetcher_開發規範書.md)

3. **使用範本開始開發**
   - 程式碼範本：[_template.py](_template.py)
   - 規格書範本：[_template_spec.md](_template_spec.md)

---

## 📋 開發流程

### 步驟 1: 創建模組開發包

為新模組建立專屬目錄：

```bash
# 建立模組目錄（例如：F02）
mkdir dev\f02_package
cd dev\f02_package
```

### 步驟 2: 複製範本

```bash
# 複製規格書範本
copy ..\\_template_spec.md f02_fetcher_開發規範書.md

# 複製程式碼範本
copy ..\\_template.py f02_fetcher_dev.py
```

### 步驟 3: 填寫規格書

編輯 `f02_fetcher_開發規範書.md`，填入：
- 模組目標
- 資料來源 URL
- 需抓取的欄位定義
- 測試案例

### 步驟 4: 實作程式碼

編輯 `f02_fetcher_dev.py`，實作：
- `fetch(date: str) -> str` 函式
- `format_f02_output()` 格式化函式
- 完整錯誤處理

### 步驟 5: 測試

```bash
# 1. 獨立測試
python dev\f02_package\f02_fetcher_dev.py 2025-12-03

# 2. 整合測試（驗收模式）
python run.py 2025-12-03 dev --module f02_fetcher_dev

# 3. 檢查輸出
type data\2025-12-03_f02_fetcher_dev.txt
```

### 步驟 6: 驗收通過後移至正式目錄

```bash
# 移動到 modules/ 並重新命名（移除 _dev）
move dev\f02_package\f02_fetcher_dev.py modules\f02_fetcher.py
```

---

## ✅ 必須遵循的規範

### 統一文字格式 v4.0

#### 成功時
```
[ YYYY.MM.DD  FXX{描述}   source: {來源} ]
```

**範例**：
```
[ 2025.12.03  F01台指期外資淨額 -29,439 口（多方 19,214，空方 48,653）   source: TAIFEX ]
```

#### 失敗/錯誤時
```
[ YYYY.MM.DD  FXX 錯誤: {錯誤訊息}   source: {來源} ]
```

**範例**：
```
[ 2025.11.30  F01 錯誤: 該日無交易資料（可能是假日或休市日）   source: TAIFEX ]
```

### 四大核心規範

1. ✅ **回傳類型**：必須是 `str`（統一文字格式）
2. ✅ **錯誤處理**：所有錯誤都轉換為文字格式，不拋出例外
3. ✅ **日期格式**：輸入 `YYYY-MM-DD` → 輸出 `YYYY.MM.DD`
4. ✅ **模組代號**：大寫（F01, F02...）

---

## 📝 程式碼範本骨架

```python
"""
FXX模組：[模組說明]
"""

import requests
import pandas as pd
from datetime import datetime
from typing import Dict, Optional

# 模組識別
MODULE_ID = "fxx"  # 小寫
SOURCE = "[資料來源]"


def format_fxx_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
    """格式化輸出為統一文字格式"""
    date_formatted = date.replace("-", ".")
    module_code = MODULE_ID.upper()

    if status == "success" and data:
        # 根據模組需求客製化輸出
        return f"[ {date_formatted}  {module_code}{描述}   source: {SOURCE} ]"
    else:
        error_msg = error or "未知錯誤"
        return f"[ {date_formatted}  {module_code} 錯誤: {error_msg}   source: {SOURCE} ]"


def fetch(date: str) -> str:
    """抓取指定日期的資料"""
    # 1. 驗證日期格式
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_fxx_output(date, "error", error="日期格式錯誤，請使用 YYYY-MM-DD")

    try:
        # 2. 發送 HTTP 請求
        # ... 實作邏輯

        # 3. 回傳成功結果
        return format_fxx_output(date, "success", data={...})

    except requests.Timeout:
        return format_fxx_output(date, "error", error="連線逾時，請檢查網路連線")
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

## 🔍 範例參考

### F01 模組（最佳實踐範例）

- **規格書**：[f01_package/f01_fetcher_開發規範書.md](f01_package/f01_fetcher_開發規範書.md)
- **程式碼**：[../modules/f01_fetcher.py](../modules/f01_fetcher.py)
- **功能**：抓取台指期貨外資未平倉資料

**學習重點**：
- 完整的錯誤處理範例
- MultiIndex 表頭處理
- 資料清洗和驗證
- 清晰的中文註解

### F14 模組（開發中範例）

- **規格書**：[f14_package/f14_fetcher_spec.md](f14_package/f14_fetcher_spec.md)
- **程式碼**：[f14_package/f14_fetcher_dev.py](f14_package/f14_fetcher_dev.py)
- **功能**：抓取台指期貨當日收盤價

**學習重點**：
- 統一文字格式 v4.0 實作
- 簡潔的程式碼結構
- 模組化的格式化函式

---

## ⚠️ 常見錯誤與解決方法

### 錯誤 1: 回傳類型錯誤

❌ **錯誤**：
```python
def fetch(date: str) -> dict:  # 錯誤：回傳 dict
    return {"status": "success", ...}
```

✅ **正確**：
```python
def fetch(date: str) -> str:  # 正確：回傳 str
    return "[ 2025.12.03  F01... ]"
```

### 錯誤 2: 拋出未處理的例外

❌ **錯誤**：
```python
def fetch(date: str) -> str:
    response = requests.get(url)  # 可能拋出例外
    return format_output(...)
```

✅ **正確**：
```python
def fetch(date: str) -> str:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return format_output(...)
    except requests.Timeout:
        return format_output(date, "error", error="連線逾時")
    except Exception as e:
        return format_output(date, "error", error=f"錯誤: {str(e)}")
```

### 錯誤 3: 日期格式不一致

❌ **錯誤**：
```python
# 輸出保留 "-" 分隔
return f"[ 2025-12-03  F01... ]"  # 錯誤
```

✅ **正確**：
```python
# 必須轉換為 "." 分隔
date_formatted = date.replace("-", ".")
return f"[ 2025.12.03  F01... ]"  # 正確
```

### 錯誤 4: 模組代號大小寫錯誤

❌ **錯誤**：
```python
MODULE_ID = "F01"  # 錯誤：應該小寫
return f"[ ... f01... ]"  # 錯誤：輸出應該大寫
```

✅ **正確**：
```python
MODULE_ID = "f01"  # 正確：定義時小寫
module_code = MODULE_ID.upper()  # 正確：輸出時轉大寫
return f"[ ... {module_code}... ]"  # 正確：F01
```

---

## 📚 相關文件

- **專案入口**：[../README.md](../README.md)
- **通用規範**：[共同開發規範書_V1.md](共同開發規範書_V1.md) ⭐
- **Claude 配置**：[../CLAUDE_CONFIG.md](../CLAUDE_CONFIG.md)

---

## 💡 提示與最佳實踐

### 開發提示

1. **優先閱讀「快速參考」**：開頭10分鐘就能掌握核心規範
2. **參考 F01 範例**：最完整的實作參考
3. **使用範本**：避免從零開始，減少錯誤
4. **頻繁測試**：邊寫邊測，及早發現問題

### 測試提示

1. **測試三種情況**：
   - 正常交易日（應該成功）
   - 假日/休市日（應該失敗）
   - 特殊日期（邊界情況）

2. **檢查輸出格式**：
   - 中括號、空格、日期格式
   - 模組代號大寫
   - source 標記

3. **驗證錯誤處理**：
   - 故意輸入錯誤日期格式
   - 測試網路逾時情況
   - 確認不會拋出例外

### 程式碼品質提示

1. **清晰的註解**：使用中文註解說明邏輯
2. **有意義的變數名稱**：`close_price` 優於 `cp`
3. **適當的函式拆分**：一個函式只做一件事
4. **避免過度工程**：保持簡單直接

---

## 🔄 版本變更說明（v4.0）

### 重大變更

**從 base.py 架構升級到統一文字格式**：

| 項目 | 舊版（v3.x） | 新版（v4.0） |
|------|-------------|-------------|
| 回傳類型 | `dict` | `str` |
| 依賴 | `BaseFetcher`, `FetchResult` | 無依賴 |
| 輸出檔案 | `.json` | `.txt` |
| 格式驗證 | Pydantic | 字串模式匹配 |

### 已移除

- ❌ `base.py`（BaseFetcher, FetchResult 類別）
- ❌ `pytest` 測試框架依賴
- ❌ JSON 格式輸出

### 升級指南

如果您有使用舊版 base.py 的程式碼，請參考 `_template.py` 進行升級。

---

## 📞 需要協助？

- 參考文件：[共同開發規範書_V1.md](共同開發規範書_V1.md)
- 查看 FAQ：規範書內有常見問題解答
- 參考範例：F01 和 F14 模組

---

**版本**: 4.0
**最後更新**: 2025-12-05
**適用專案**: 台指期貨20因子預測系統
