# F10 模組說明

## 模組目的
抓取台指選擇權每日交易行情，並保存原始 HTML 快照與解析後資料。

---

## 檔案結構
- `raw/`：HTML 快照 (init, after, txo, error)  
- `logs/`：執行紀錄 (含錯誤訊息)  
- `data/`：解析後 CSV/JSON  

---

## 檔案命名規則
- `f10_init_YYYY-MM-DD.html`：初始頁面快照  
- `f10_after_YYYY-MM-DD.html`：查詢後頁面快照  
- `f10_txo_YYYY-MM-DD.html`：最終表格快照  
- `f10_error_YYYY-MM-DD.html`：錯誤快照  

---

## 使用方式
```bash
python f10_fetcher.py



輸出檔案：
• 	：HTML 快照
• 	：執行紀錄
• 	：解析後 CSV/JSON