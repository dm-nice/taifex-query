設計理念
統一介面：所有模組都用 fetch(date)

統一回傳格式：主程式能自動分流

易於維護：失敗自動回報，成功自動存檔

程式碼

---

## 2️⃣ `docs/architecture.md`

```markdown
# 專案架構說明 (architecture.md)

本文件解釋 **Taifex 專案**的目錄結構與設計理念，協助協作者快速理解。

---

## 根目錄

Taifex/ ├── README.md ├── requirements.txt ├── run.py ├── taifex_dashboard.py


程式碼

- **README.md**：專案簡介與使用說明  
- **requirements.txt**：依賴套件清單  
- **run.py**：主程式，統一呼叫 F01–F20  
- **taifex_dashboard.py**：儀表板整合程式  

---

## fetchers/ (資料抓取模組)
- 存放 **F01–F20** 抓取模組  
- 每個模組獨立，統一介面 `fetch(date: str) -> dict`  

---

## docs/ (文件專區)
- **interface_spec.md**：模組介面規範  
- **architecture.md**：專案架構說明  

---

## utils/ (共用工具)
- **debug_pipeline.py**：錯誤回報工具  

---

## 其他目錄
- **apis/**：外部 API 串接  
- **indicators/**：指標計算模組  
- **visualize/**：視覺化模組  
- **tests/**：測試模組  
- **data/**：成功抓取的資料  
- **logs/**：執行紀錄  
- **issues/**：錯誤紀錄 (Markdown)  

---

## 設計理念
1. **模組化**：F01–F20 各自獨立  
2. **分層清楚**：抓取、計算、視覺化、工具、文件各有目錄  
3. **易於維護**：失敗自動回報，成功自動存檔  
4. **可擴充**：未來可新增 F21–F30 或更多 API  




