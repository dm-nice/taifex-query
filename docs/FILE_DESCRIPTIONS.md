# 專案檔案功能說明清單

此文件列出專案 `C:\AI\Taifex` 下所有主要檔案與目錄的功能說明。

## 🚀 核心執行檔 (Project Root)
這些是用來啟動程式的入口。

| 檔案名稱 | 功能說明 |
| :--- | :--- |
| **`daytime_query.py`** | **[日盤] 主程式**。負責抓取 F01-F17 指標 (外資期貨、選擇權、大盤、個股、均線)，並產生當日報告。自動回補缺漏資料。 |
| **`nighttime_query.py`** | **[夜盤] 主程式**。負責抓取 F21-F22 指標 (盤後台指期收盤、成交量)，並產生夜盤報告。 |
| `predict_dashboard.py` | (尚未啟用) 預測模型儀表板的草稿或舊檔。 |
| [`README.md`](README.md) | **專案使用手冊**。包含安裝教學、指令說明、指標列表與專案結構圖。 |
| `20因子 輸出格式.md` | 用戶定義的輸出格式參考文件。 |

## ⚙️ 邏輯核心 (scrapers/)
存放實際去網站抓資料的程式碼。

| 檔案名稱 | 功能說明 |
| :--- | :--- |
| **`daytime.py`** | **[日盤] 爬蟲邏輯庫**。包含 F01-F05, F07 (Taifex HTML) 與 F11-F17 (TWSE JSON API) 的所有具體實作函式。 |
| **`nighttime.py`** | **[夜盤] 爬蟲邏輯庫**。包含 F21-F22 的 Taifex 盤後資料解析邏輯。 |

## 🛠️ 工具支援 (utils/)
存放被多個程式共用的輔助工具。

| 檔案名稱 | 功能說明 |
| :--- | :--- |
| **`date_utils.py`** | **日期處理工具**。功能：取得目前台灣時間、判斷是否為交易日、計算「前一個交易日」。 |
| **`helpers.py`** | **檔案處理工具**。功能：將抓到的資料轉存為 Markdown (`save_to_markdown`)、自動產生版本號 (`_v1`, `_v2`)。 |

## 🧪 開發與測試 (dev/)
存放開發過程中的測試腳本、診斷工具與舊檔存檔。程式執行時不會用到這裡的檔案。

| 檔案名稱 | 功能說明 |
| :--- | :--- |
| `tests/` (目錄) | **品質檢測程式**。包含 `test_daytime_all.py`，用 `pytest` 指令執行可快速檢查爬蟲是否運作正常。 |
| `archive_taifex_scraper.py`| **舊版主程式封存**。包含舊的選單介面與鍵盤監聽功能，僅供參考。 |
| `diagnose_*.py` | **診斷腳本**。開發過程中用來測試特定 API 連線 (如 TWSE, VIX) 的一次性腳本。 |

## 📚 文件 (docs/)
存放詳細的專案說明文件。

| 檔案名稱 | 功能說明 |
| :--- | :--- |
| **`IMPLEMENTATION_REFERENCE.md`** | ** [推薦閱讀] 技術實作手冊**。詳細記錄每個指標的 API URL、參數與開發注意事項。 |
| `QUICK_REFERENCE.md` | 速查表。 |
| `TAIFEX_PROJECT_SPECIFICATION.md` | 完整的專案規格書。 |
| `CODE_FRAMEWORK.md` | 代碼架構說明。 |
| `troubleshooting_f01_f03.md` | 針對 F01-F03 開發時遇到的問題排除紀錄。 |

## 📂 資料夾說明
*   `output/`: 程式執行後產生的 `.md` 報告檔案都放在這裡。
*   `venv32/`: Python 虛擬環境 (包含所有安裝的套件)。
*   `.git/`: (隱藏) Git 版本控制資料庫。
*   `.claude/`: (隱藏) AI 助手相關設定。


開發目錄規範
檔案類型	放置目錄	範例
爬蟲程式	scrapers/	
daytime.py
, 
nighttime.py
工具函式	utils/	
helpers.py
, 
date_utils.py
單元測試	dev/tests/	test_daytime_all.py
輸出資料	output/	taifex_YYYY.MM.DD_v*.md
文件說明	docs/	IMPLEMENTATION_REFERENCE.md
開發測試	dev/	diagnose_*.py
注意事項
根目錄放程式入口：daytime_query.py, nighttime_query.py

