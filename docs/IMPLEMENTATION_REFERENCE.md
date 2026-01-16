# F01-F25 實作總結與技術參考手冊

這份文件詳細記錄了專案中所有指標 (F01-F25) 的實作狀態、數據來源、技術細節與「踩坑」經驗。下次開發或維護時，請優先參考此文件以避免重複錯誤。

**最後更新時間**: 2026-01-16
**實作狀態**:
*   ✅ 已完成: F01-F05, F07, F11-F17, F21-F22
*   ❌ 未實作/暫緩: F06 (資料源問題), F23-F25 (待接入 Wantgoo)

---

## 1. 一般交易時段 (Daytime) - `scrapers/daytime.py`

### 🟢 期貨與選擇權 (來源: Taifex 台灣期貨交易所)

| 指標 | 描述 | 實作方式 (Method) | URL / API | 關鍵技術點 (Gotchas) |
| :--- | :--- | :--- | :--- | :--- |
| **F01-F03** | **外資期貨籌碼**<br>(淨額, 多方, 空方) | **HTML Parsing**<br>(POST) | `/cht/3/totalTableDate` | 1. 需帶 `User-Agent` 與 `Referer`。<br>2. 尋找 `class="table_f"`。<br>3. 定位文字 "外資" 所在的 row。<br>4. 欄位順序固定，需去除逗號。 |
| **F04** | **台指期收盤價** | **HTML Parsing**<br>(POST) | `/cht/3/futDailyMarketReport` | 1. Payload: `queryType=2`, `marketCode=0` (日盤), `commodity_id=TX`。<br>2. 找到第一欄含 "TX" 的列。<br>3. 收盤價通常在第 6 欄 (`tds[5]`)。 |
| **F05** | **選擇權成交量** | **HTML Parsing**<br>(POST) | `/cht/3/optDailyMarketReport` | 1. Payload: `commodity_id=TXO`。<br>2. **陷阱**: 表格極大。需搜尋文字 "小計" 的列。<br>3. 該列中第一個純數字欄位即為成交量。 |
| **F06** | **VIX 波動率** | ❌ **暫緩** | `/cht/7/vixMinNew` | **問題**: 官方頁面按鈕無效或回傳 404。舊版 API `/cht/3/vix` 已失效。需尋找替代來源。 |
| **F07** | **P/C Ratio** | **HTML Parsing**<br>(GET) | `/cht/3/pcRatio` | 1. 表格包含大量歷史數據。<br>2. 需精確比對日期字串 (例如 `2026/01/16`)，避免抓錯日期。 |

### 🔵 大盤與個股 (來源: TWSE 台灣證券交易所)

**重要共通規則**: TWSE API 對 Header 檢查嚴格，必須使用 `requests.Session()` 維持連線，並帶上正確的 `Referer`。

| 指標 | 描述 | 實作方式 (Method) | API Endpoint (JSON) | 關鍵技術點 (Gotchas) |
| :--- | :--- | :--- | :--- | :--- |
| **F11** | **加權指數** | **JSON API** | `MI_5MINS_HIST` | 1. API 網址路徑可以取得整月數據。<br>2. 日期參數格式通常為 `YYYYMMDD`。<br>3. 回傳資料日期為**民國年** (`115/01/16`)，需轉換。 |
| **F12** | **大盤成交量** | **JSON API** | `MI_INDEX` (`type=MS`) | 1. 需遍歷 `tables` 尋找標題含 "大盤統計資訊" 的表。<br>2. 尋找 row[0] 含 "總計" 的列。 |
| **F13** | **20日均線乖離** | **內部計算** | (使用 F11 數據) | **策略**: 不爬 Wantgoo。<br>1. 利用 F11 API 抓取**本月**與**上個月**的收盤價歷史。<br>2. 拼接後取最後 20 筆計算平均 (MA20)。<br>3. 優點: 穩定、不依賴第三方。 |
| **F14-F16**| **台積電**<br>(收盤, 漲跌, 量) | **JSON API** | `STOCK_DAY` | 1. 參數 `stockNo=2330`。<br>2. 漲跌價差欄位可能含 "X" (除權息) 或 "+/-" 符號，需清洗。<br>3. 成交量單位是「股」，需除以 1000 轉「張」。 |
| **F17** | **外資買賣超** | **JSON API** | `BFI82U` | 1. 尋找 "外資及陸資" 的列。<br>2. 注意欄位順序：買進, 賣出, **差額**。 |

---

## 2. 盤後交易時段 (Nighttime) - `scrapers/nighttime.py`

| 指標 | 描述 | 實作方式 | 來源 | 關鍵技術點 |
| :--- | :--- | :--- | :--- | :--- |
| **F21** | **盤後台指收盤** | HTML (POST) | Taifex `futDailyMarketReport` |Payload: `marketCode=1` (這代表**夜盤**)。<br>其餘解析邏輯同 F04。 |
| **F22** | **盤後台指成交量**| HTML (POST) | Taifex `futDailyMarketReport` | 同上，通常在第 9 欄 (`tds[8]`) 或依位置判斷。 |
| **F23-25**| **美股/ADR** | ❌ **未實作** | Wantgoo (預定) | 尚未開發。預計需處理動態載入問題。 |

---

## 3. 專案架構與維護指南

### 檔案結構
*   `scrapers/daytime.py`: 包含 F01-F17 的所有邏輯。
*   `scrapers/nighttime.py`: 包含 F21-F22 的所有邏輯。
*   `utils/helpers.py`: 通用的存檔、版本號管理工具。

### 如何增加新指標？
1.  **決定時段**: 是日盤還夜盤？放入對應檔案。
2.  **決定來源**: 優先找 JSON API (TWSE/Taifex)，其次才解析 HTML。
3.  **整合**: 在 `query_daytime_data` 或 `query_nighttime_data` 中加入呼叫，並處理 `res.extend()`。

### 常見錯誤排除
1.  **IndentationError**: Python 縮排敏感，修改代碼時請小心混用 Tab 和 Space。
2.  **403 Forbidden / 429 Too Many Requests**: 
    *   檢查 `User-Agent` 是否像瀏覽器。
    *   檢查 `Referer` 是否正確 (TWSE 非常在意這個)。
    *   增加 `time.sleep()` 延遲。
3.  **資料抓不到 (None)**:
    *   檢查當天是否為休市日。
    *   程式已內建「自動回溯前一日」功能 (僅限日盤)，會嘗試抓上一天的資料。

### 未來優化方向
*   **F13 優化**: 目前每次都重抓兩個月歷史資料，可考慮快取 (Cache)。
*   **例外處理**: 目前多數錯誤只 print，可加入 Log 檔案記錄。
