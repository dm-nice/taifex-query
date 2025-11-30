# 發包說明文件 (outsourcing_spec.md)

## 專案背景
本專案用於 **抓取台灣期交所 (TAIFEX) 與台灣證交所 (TWSE)** 各類金融指標，並進行模組化的資料分析與視覺化。  
所有模組需遵守統一介面規範，確保主程式能 plug-and-play。

---

## 工作範圍
- 撰寫指定模組 (例如 F01)，放置於 `outsource/` 目錄下。
- 模組需依照 `docs/interface_spec.md` 規範設計：
  - 統一介面：`fetch(date: str) -> dict`
  - 統一回傳格式：成功 / 失敗
  - 錯誤回報：失敗時需回傳 `status="fail"` 並附上 `error`

---

## F1 模組需求
- **指標名稱**：台指期貨外資及陸資淨口數 (Open Interest, OI)  
- **資料來源**：台灣期貨交易所 (TAIFEX) 官方網站  
- **需抓取欄位**：
  - 外資多單口數  
  - 外資空單口數  
  - 外資淨口數 (多 - 空)  
  - 陸資多單口數  
  - 陸資空單口數  
  - 陸資淨口數 (多 - 空)  
- **輸入**：`date (YYYY-MM-DD)`  
- **輸出**：dict 格式，符合 `interface_spec.md` 規範  

---

## 外包交付檔名規範
- **交付目錄**：請放在 `outsource/` 子目錄，不要直接放到 `fetchers/`  
- **檔名格式**：`fXX_fetcher_dev.py`  
  - 例如：`f01_fetcher_dev.py`、`f10_fetcher_dev.py`  
- **驗收流程**：
  1. 外包交付 → 放在 `outsource/`  
  2. 測試時 → 使用 `run_test.py` 指向 `outsource/` 裡的檔案  
  3. 驗收成功 → 改名並移到 `fetchers/`，取代骨架  
  4. 驗收失敗 → 保留在 `outsource/`，並在 `issues/` 留下錯誤紀錄  

---

## 驗收標準
- 模組能正確執行，並符合以下規範：
  - 成功回傳：
    ```python
    {
        "module": "f01",
        "date": "2025-11-28",
        "status": "success",
        "data": {...}
    }
    ```
  - 失敗回傳：
    ```python
    {
        "module": "f01",
        "date": "2025-11-28",
        "status": "fail",
        "error": "錯誤訊息"
    }
    ```
- 模組可獨立執行測試 (`__main__` 測試入口)。  
- 主程式 `run.py` 呼叫模組時能正常分流至 `data/`、`logs/`、`issues/`。  
- 錯誤時會觸發 `utils/debug_pipeline.py`，自動產生 Markdown 錯誤紀錄。  

---

## Log 格式規範 (僅供內部參考)
> ⚠️ 此章節僅供我們自己檢查，外包人員不用處理 log 檔案。

主程式 `run.py` 會自動產生執行紀錄檔 `logs/YYYY-MM-DD_run.log`，格式如下：



