# TAIFEX 爬蟲開發問題記錄 (Troubleshooting & Lessons Learned)

**記錄日期**: 2026-01-16
**針對指標**: F01-F03 (台指期外資持倉)
**目標網址**: https://www.taifex.com.tw/cht/3/totalTableDate

---

## 1. 遇到的主要問題與挑戰

### 1.1 繁體與簡體關鍵字不匹配
*   **初期狀況**: 使用 `台股期貨` 作為關鍵字搜尋表格內容，結果完全找不到資料。
*   **分析原因**: 期交所官網使用的是繁體正字 **`臺股期貨`**。在 Web Scraping 中「台」與「臺」是完全不同的字元。
*   **解決方案**: 統一將代碼中的搜尋關鍵字改為 **`臺`**。

### 1.2 期交所的 POST 請求限制
*   **初期狀況**: 單純使用 `requests.post()` 帶入 `queryDate` 無法獲取正確的 HTML 內容（返回 404 或 預設空白頁面）。
*   **分析原因**: 期交所伺服器會檢查以下內容：
    *   **Cookie**: 若沒有先進行 GET 請求獲取 session cookie，POST 請求會失效。
    *   **Referer/Origin Header**: 檢查請求是否來自官網內部，避免外部非法調用。
    *   **偽裝 User-Agent**: 預設的 python-requests UA 會被攔截。
*   **解決方案**: 
    *   採用 `requests.Session()` 維持連線狀態。
    *   手補 `Referer` 與 `User-Agent` 標頭。
    *   補齊完整表單參數（如 `queryType`, `goDay`, `doQuery` 等空白欄位）。

### 1.3 表格定位複雜度 (Table Layout)
*   **初期狀況**: 網頁上有多個 class 為 `table_f` 的表格。
*   **分析原因**: 同一個頁面存在兩個 `table_f`：第一個是「成交量」，第二個才是我們要的「未平倉量」。
*   **解決方案**: 
    *   使用 `soup.find_all('table', class_='table_f')` 獲取所有表格。
    *   透過檢查表格內的文字（如是否包含 `未平倉`）來動態定位正確的數據表。

### 1.4 欄位解析的不確定性 (TD/TH Index)
*   **初期狀況**: 使用固定的欄位索引 (Index) 有時會報錯。
*   **分析原因**: 「身份別」欄位（自營商、投信、外資）在 HTML 裡面有時是 `<td>` 有時是 `<th>`，且第一行可能有 `rowspan` 影響後面的索引起始點。
*   **解決方案**: 
    *   使用 `row.find_all(['td', 'th'])` 同時抓取所有格子。
    *   根據外資行的固定結構 `[身份別, 多方口, 多方額, 空方口, 空方額, 淨額口, 淨額額]`。
    *   F01 定位在 Index 5，F02 定位在 Index 1，F03 定位在 Index 3。

---

## 2. 日後維護建議

1.  **關鍵字監控**: 若未來期交所將「臺」改回「台」，或修改選單名稱，需優先檢查代碼中的 string match。
2.  **API Fallback**: 若 `totalTableDate` (總表) 持續不穩定，可考慮切換到 `futContractsDate` (產品分頁)，雖然解析較繁瑣，但資料更直接。
3.  **防爬蟲策略**: 若未來出現 403 Forbidden，可能需要更高級的 `Session` 處理或更換 User-Agent 列表。

---

## 3. 成功範例 (2026.01.15)
*   **URL**: https://www.taifex.com.tw/cht/3/totalTableDate (POST queryDate=2026/01/15)
*   **外資未平倉淨額**: -181389
*   **外資未平倉多方**: 308949
*   **外資未平倉空方**: 490338
