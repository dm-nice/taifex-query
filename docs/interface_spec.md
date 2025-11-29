# 模組介面規範 (Interface Specification)

本文件定義 F1–F20 以及其他模組的 **檔名規範、函式介面、輸入/輸出格式、錯誤回報方式**。  
所有協作者必須遵守此規範，確保主程式能統一呼叫並整合結果。

---

## 1. 檔名規範

- 抓取模組：`fXX_fetcher.py`  
  - XX 為兩位數 (01–20)，例如：`f01_fetcher.py`、`f10_fetcher.py`
- API 模組：`api_xx.py` (例如 `f8_api.py`)
- 指標計算模組：`indicator_xx.py`
- 工具模組：放在 `utils/` 目錄下，命名為 `功能名稱.py`

---

## 2. 函式介面規範

每個模組必須提供一個主要函式：

```python
def fetch(date: str) -> dict:
    """
    輸入:
        date (str): 日期字串，格式 YYYY-MM-DD
    輸出:
        dict: 統一格式如下
    """
```

---

## 3. 輸入格式 (Input)

- **date**: 字串，格式 `YYYY-MM-DD`
- 主程式會統一傳入日期字串，模組根據該日期抓取資料

---

## 4. 回傳格式 (Output)

### 成功時：
```python
{
    "module": "f10",              # 模組代號 (如 f10)
    "date": "2025-11-29",         # 資料日期
    "status": "success",          # 狀態標記
    "data": {...}                 # 抓取到的資料 (dict 或 DataFrame)
}
```

### 失敗時：
```python
{
    "module": "f10",
    "date": "2025-11-29",
    "status": "fail",
    "error": "錯誤訊息 (例如: 連線失敗)"
}
```

---

## 5. 錯誤回報規範

- 若模組失敗，必須回傳 `status = "fail"` 並附上 `error` 訊息
- 主程式會呼叫 `utils/debug_pipeline.py`，自動產生 `issues/YYYY-MM-DD_module_error.md`

---

## 6. 測試規範

每個模組需能獨立執行測試：

```python
if __name__ == "__main__":
    result = fetch("2025-11-29")
    print(result)
```

測試至少包含：
- 正常輸入 → 成功回傳
- 錯誤輸入 → 正確回報錯誤

---

## 7. 主程式整合規範

主程式 (`run.py`) 呼叫方式：

```python
from fetchers.f10_fetcher import fetch as f10

result = f10("2025-11-29")
if result["status"] == "success":
    # 寫入 data/
else:
    # 呼叫 debug_pipeline
```

---

## 8. F1–F20 檔名清單

- f01_fetcher.py   # F1 指標抓取程式
- f02_fetcher.py   # F2 指標抓取程式
- f03_fetcher.py   # F3 指標抓取程式
- f04_fetcher.py   # F4 指標抓取程式
- f05_fetcher.py   # F5 指標抓取程式
- f06_fetcher.py   # F6 指標抓取程式
- f07_fetcher.py   # F7 指標抓取程式
- f08_fetcher.py   # F8 指標抓取程式
- f09_fetcher.py   # F9 指標抓取程式
- f10_fetcher.py   # F10 指標抓取程式
- f11_fetcher.py   # F11 指標抓取程式
- f12_fetcher.py   # F12 指標抓取程式
- f13_fetcher.py   # F13 指標抓取程式
- f14_fetcher.py   # F14 指標抓取程式
- f15_fetcher.py   # F15 指標抓取程式
- f16_fetcher.py   # F16 指標抓取程式
- f17_fetcher.py   # F17 指標抓取程式
- f18_fetcher.py   # F18 指標抓取程式
- f19_fetcher.py   # F19 指標抓取程式
- f20_fetcher.py   # F20 指標抓取程式
```
