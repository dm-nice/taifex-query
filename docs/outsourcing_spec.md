# 發包說明文件 (outsourcing_spec.md)

## 專案背景
本專案用於 **抓取台灣期交所 (TAIFEX) 與台灣證交所 (TWSE)** 各類金融指標，並進行模組化的資料分析與視覺化。  
所有模組需遵守統一介面規範，確保主程式能 plug-and-play。

---

## 工作範圍
- 撰寫指定模組 (例如 F01)，放置於 `fetchers/` 目錄下。
- 模組需依照 `docs/interface_spec.md` 規範設計：
  - 統一介面：`fetch(date: str) -> dict`
  - 統一回傳格式：成功 / 失敗
  - 錯誤回報：失敗時需回傳 `status="fail"` 並附上 `error`

---

## F1 模組需求
- **指標名稱**：台指期貨外資及陸資淨口數 (Open Interest, OI)  
- **資料來源**：台灣期貨交易所 (TAIFEX) 官方網站  
- **網頁位置**：每日交易統計 → 外資及陸資 OI 報表  
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

## 交付內容
1. **程式碼**
   - 例如：`fetchers/f01_fetcher.py`
   - 必須能獨立執行測試 (`python f01_fetcher.py`)
2. **文件**
   - 若有特殊需求或額外欄位，需補充在 `docs/interface_spec.md` 或附加說明
3. **測試結果**
   - 提供至少一個測試日期的執行結果 (JSON dict)

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

## 注意事項
- 請勿修改主程式 `run.py`，僅需完成模組。  
- 請遵守 `docs/interface_spec.md` 與 `docs/architecture.md` 文件規範。  
- 若資料來源不足，請提出需求，我方會補充。  

