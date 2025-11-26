📁 TAIFEX 自動化查詢專案（進階版）
此專案用於自動查詢台灣期交所（TAIFEX）法人交易資料，支援指定日期查詢、CSV 儲存、畫面擷取、OCR 分析，並規劃多日查詢、自動排程與視覺化分析。

📂 目錄結


C:\Yuanta\QAPI\Taifex\
├── scripts\                          # 程式碼
│   ├── taifex_save_csv_20251124.py          # 主流程：查詢指定日期並存成 CSV
│   ├── taifex_totalTable_query_20251124.py  # 查詢頁面測試＋畫面擷取
│   ├── taifex_dom_foreign_simple.py         # 外資資料抽取（簡化版）
│   ├── taifex_dom_foreign_week.py           # 外資週資料抽取
│   ├── taifex_foreign_html.py               # 外資資料解析（HTML DOM）
│   ├── taifex_foreign_html_multi.py         # 多表格解析測試
│   ├── ocr_parse_foreign.py                 # OCR 解析外資資料
│   ├── ocr_parse_foreign_strong.py          # 強化版 OCR 抽取
│   └── utils.py                             # 共用工具（未來可新增）
├── data\                             # 儲存 CSV 資料
│   ├── taifex_20251124_trading.csv
│   └── taifex_20251124_openinterest.csv
├── screenshot\                       # 儲存畫面擷圖
│   └── taifex_20251124_screen.png
├── visualize\                        # 視覺化分析輸出
│   └── foreign_net_trend.png
├── README.md                         # 專案說明文件
└── .gitignore                        # Git 忽略規則



C:\Yuanta\QAPI\Taifex
├── scripts\                          # 程式碼 │   ├── taifex_save_csv_20251124.py          # 主流程：查詢指定日期並存成 CSV │   ├── taifex_totalTable_query_20251124.py  # 查詢頁面測試＋畫面擷取 │   ├── taifex_dom_foreign_simple.py         # 外資資料抽取（簡化版） │   ├── taifex_dom_foreign_week.py           # 外資週資料抽取 │   ├── taifex_foreign_html.py               # 外資資料解析（HTML DOM） │   ├── taifex_foreign_html_multi.py         # 多表格解析測試 │   ├── ocr_parse_foreign.py                 # OCR 解析外資資料 │   ├── ocr_parse_foreign_strong.py          # 強化版 OCR 抽取 │   └── utils.py                             # 共用工具（未來可新增） ├── data\                             # 儲存 CSV 資料 │   ├── taifex_20251124_trading.csv │   └── taifex_20251124_openinterest.csv ├── screenshot\                       # 儲存畫面擷圖 │   └── taifex_20251124_screen.png ├── visualize\                        # 視覺化分析輸出 │   └── foreign_net_trend.png ├── README.md                         # 專案說明文件 └── .gitignore                        # Git 忽略規則


---

## 環境需求

- Python 3.9+（支援 32/64-bit，依你的環境）
- 套件：Playwright、pandas（未來擴充）、opencv/pytesseract（若使用 OCR）
- 瀏覽器：Playwright 安裝瀏覽器二進位（`playwright install`）

---

## 快速開始

```bash
# 建立與啟動虛擬環境（範例）
python -m venv venv32
venv32\Scripts\activate

# 安裝相依套件
pip install playwright
playwright install
# 依需求：pip install pandas opencv-python pytesseract

# 單日查詢並儲存 CSV
python scripts/taifex_save_csv_20251124.py

# 查詢頁面畫面擷取
python scripts/taifex_totalTable_query_20251124.py

# OCR 外資資料解析（如需）
python scripts/ocr_parse_foreign.py




🛠 執行方式

# 單日查詢並儲存 CSV
python scripts/taifex_save_csv_20251124.py

# 查詢頁面畫面擷取
python scripts/taifex_totalTable_query_20251124.py

# OCR 外資資料解析
python scripts/ocr_parse_foreign.py

# 外資週資料抽取
python scripts/taifex_dom_foreign_week.py

📂 輸出資料說明
- data/
- 存放法人交易資料 CSV
- 檔名格式：taifex_YYYYMMDD_trading.csv、taifex_YYYYMMDD_openinterest.csv
- screenshot/
- 存放查詢畫面擷圖，供人工驗證
- 檔名格式：taifex_YYYYMMDD_screen.png
- visualize/
- 存放視覺化分析結果（折線圖、趨勢圖）
- 檔名格式：foreign_net_trend.png


作業流程（單日）
1. 	指定日期（範例：）
2. 	進入查詢頁：
3. 	程式自動填入日期 → 模擬 Enter → 等待「日期YYYY/MM/DD」文字出現
4. 	解析兩張表格 → 儲存 CSV → 擷取畫面供人工核對



擴充功能規劃
多日查詢
• 	輸入日期範圍或讀取清單
• 	迴圈查詢並儲存多日 CSV
• 	可選合併總表（pandas）





自動排程（Windows）
• 	使用 Task Scheduler
• 	每天早上自動執行
• 	自動判斷前一交易日（排除週末與國定假日）



視覺化分析
• 	外資淨額折線圖
• 	投信 vs 自營商對比
• 	未平倉（OI）趨勢


欄位標頭清理
• 	統一 CSV 欄位：身份別、多方口數、多方金額、空方口數、空方金額、淨額口數、淨額金額
• 	方便 Excel/pandas 後續分析


Git 規範
• 	.gitignore 建議（根目錄）
• 	, , , 
• 	, , 
• 	, 
• 	, , , , 
• 	Commit message 標準
• 	 新增功能
• 	 修正錯誤
• 	 更新文件
• 	 程式重構
• 	 例行維護



🚀 未來方向
- 整合 Azure / GitHub Actions → 自動每日更新並推送到雲端
- 加入 API 介面 → 提供即時查詢服務
- 建立 Dashboard → 即時顯示法人淨額趨勢



常見問題
- 查不到資料？
- 確認日期是否為交易日
- 檢查是否正確等待「日期YYYY/MM/DD」文字
- 報表欄位不對齊？
- 先以擷圖核對，再檢查 CSV 解析是否包含表頭列
- 無法啟動瀏覽器？
- 確認已執行 playwright install

Roadmap
- [ ] 多日查詢＋合併總表
- [ ] 前一交易日自動判斷
- [ ] 外資淨額視覺化 Dashboard
- [ ] GitHub Actions 每日自動抓取
- [ ] 模組化 utils（日期、下載、解析、驗證）










