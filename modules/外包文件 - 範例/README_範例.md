# 模組開發規範（F01～F20 通用）

此文件為外包商交付模組的統一規範。所有模組必須遵守以下要求，確保能被主程式 `run.py` 正確呼叫並支援獨立測試。

---

## 1. 檔案命名規範

- **正式模組**  
  - 放在 `fetchers/` 子目錄  
  - 檔名格式：`fXX_fetcher.py`  
    - 例如：`f01_fetcher.py`、`f02_fetcher.py` … `f20_fetcher.py`

- **外包回來、尚未驗收的程式**  
  - 放在 `outsource/` 子目錄  
  - 檔名格式：`fXX_fetcher_dev.py`  
    - 例如：`f01_fetcher_dev.py`、`f02_fetcher_dev.py`  
  - 驗收後再移到 `fetchers/` 並改名為正式檔案

---

## 2. 函式介面

- 每個模組必須提供函式：
  ```python
  def fetch(date: str) -> dict:
      ...



## 檔案命名規則
- `f10_init_YYYY-MM-DD.html`：初始頁面快照  
- `f10_after_YYYY-MM-DD.html`：查詢後頁面快照  
- `f10_txo_YYYY-MM-DD.html`：最終表格快照  
- `f10_error_YYYY-MM-DD.html`：錯誤快照  

---

## 使用方式
```bash
python f10_fetcher.py
