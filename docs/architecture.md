# 專案架構說明 (architecture.md)

本文件用於解釋 **Taifex 專案**的目錄結構與設計理念，協助協作者快速理解各目錄的用途。

---

## 1. 根目錄
Taifex/ ├── README.md ├── requirements.txt ├── run.py ├── taifex_dashboard.py

程式碼

- **README.md**：專案簡介與使用說明  
- **requirements.txt**：依賴套件清單，方便一鍵安裝  
- **run.py**：主程式，統一呼叫 F01–F20 模組並分流結果  
- **taifex_dashboard.py**：儀表板整合程式，負責每日指標彙整與視覺化  

---

## 2. fetchers/ (資料抓取模組)
fetchers/ ├── f01_fetcher.py ├── f02_fetcher.py └── f20_fetcher.py

程式碼

- 存放 **F01–F20 抓取模組**  
- 每個模組獨立，統一介面 `fetch(date: str) -> dict`  
- 成功回傳 `data/`，失敗回報 `issues/`  

---

## 3. docs/ (文件專區)
docs/ ├── interface_spec.md └── architecture.md

程式碼

- **interface_spec.md**：模組介面規範，定義輸入/輸出格式  
- **architecture.md**：專案架構說明，解釋目錄分層與用途  

---

## 4. utils/ (共用工具)
utils/ └── debug_pipeline.py

程式碼

- **debug_pipeline.py**：錯誤回報工具，失敗時自動產生 Markdown 錯誤紀錄  

---

## 5. apis/ (API 模組)
apis/

程式碼

- 存放外部 API 串接模組 (例如金融行情 API)  

---

## 6. indicators/ (指標計算模組)
indicators/

程式碼

- 存放指標計算邏輯 (例如 OI 分析、期現貨同步分析)  

---

## 7. visualize/ (視覺化模組)
visualize/

程式碼

- 存放圖表與報表生成程式 (例如折線圖、K 線圖)  

---

## 8. tests/ (測試模組)
tests/

程式碼

- 存放單元測試與整合測試，確保模組正確性  

---

## 9. 資料分流目錄
data/ # 成功抓取的資料 logs/ # 執行紀錄 issues/ # 錯誤紀錄 (Markdown)

程式碼

- **data/**：每日成功抓取的 JSON/CSV  
- **logs/**：執行紀錄 (log 檔)  
- **issues/**：錯誤紀錄 (Markdown)，方便 debug 與回溯  

---

## 設計理念
1. **模組化**：F01–F20 各自獨立，主程式統一呼叫  
2. **分層清楚**：抓取、計算、視覺化、工具、文件各有目錄  
3. **易於維護**：失敗自動回報，成功自動存檔  
4. **可擴充**：未來可新增 F21–F30 或更多 API，不影響既有架構  
✅ 效果
協作者一打開 docs/architecture.md 就能理解整體設計理念

文件與程式結構一致，避免混亂





