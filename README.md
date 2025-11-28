📅 最新更新日期：2025/11/26
# TAIFEX 自動化查詢專案（每日更新）

📅 更新：每日 06:00 台灣時間
本專案每天自動抓取 TAIFEX 資料，並更新目錄結構與分析結果。


## 📊 外資淨額趨勢圖

![外資淨額趨勢](visualize/foreign_net_trend.png)

本專案每天早上 06:00 自動抓取前一交易日資料，並更新目錄結構與折線圖。





此專案用於自動查詢台灣期交所（TAIFEX）法人交易資料，支援指定日期查詢、CSV 儲存、畫面擷取、OCR 分析，並規劃多日查詢、自動排程與視覺化分析。

## 📂 專案目錄結構


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

=============================
子 README

Taifex-Debug/
├── README.md                # 主 README，專案總覽
├── f1/
│   ├── f1_fetcher.py
│   ├── raw/
│   ├── logs/
│   ├── data/
│   └── README_f1.md         # 子 README，專門描述 F1 模組
├── f10/
│   ├── f10_fetcher.py
│   ├── raw/
│   ├── logs/
│   ├── data/
│   └── README_f10.md        # 子 README，專門描述 F10 模組
├── f20/
│   ├── f20_fetcher.py
│   ├── raw/
│   ├── logs/
│   ├── data/
│   └── README_f20.md        # 子 README，專門描述 F20 模組
└── issues/
    ├── 2025-11-27_f10_error.md
    └── 2025-11-28_f1_missing_table.md

=======================================





C:\Yuanta\QAPI\Taifex
├── scripts\                          # 程式碼 │   ├── taifex_save_csv_20251124.py          # 主流程：查詢指定日期並存成 CSV │   ├── taifex_totalTable_query_20251124.py  # 查詢頁面測試＋畫面擷取 │   ├── taifex_dom_foreign_simple.py         # 外資資料抽取（簡化版） │   ├── taifex_dom_foreign_week.py           # 外資週資料抽取 │   ├── taifex_foreign_html.py               # 外資資料解析（HTML DOM） │   ├── taifex_foreign_html_multi.py         # 多表格解析測試 │   ├── ocr_parse_foreign.py                 # OCR 解析外資資料 │   ├── ocr_parse_foreign_strong.py          # 強化版 OCR 抽取 │   └── utils.py                             # 共用工具（未來可新增） ├── data\                             # 儲存 CSV 資料 │   ├── taifex_20251124_trading.csv │   └── taifex_20251124_openinterest.csv ├── screenshot\                       # 儲存畫面擷圖 │   └── taifex_20251124_screen.png ├── visualize\                        # 視覺化分析輸出 │   └── foreign_net_trend.png ├── README.md                         # 專案說明文件 └── .gitignore                        # Git 忽略規則


├── scripts │   ├── taifex_save_csv_20251124.py │   ├── taifex_totalTable_query_20251124.py │   ├── ocr_parse_foreign.py │   └── ... ├── data │   ├── taifex_20251126_trading.csv │   └── taifex_20251126_openinterest.csv ├── screenshot │   └── taifex_20251126_screen.png ├── visualize │   └── foreign_net_trend.png ├── README.md └── .github └── workflows └── taifex-readme-combined.yml



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


====================================================================
📘 Taifex 專案說明文件（README.md）
🧠 專案簡介
本專案為台灣期貨交易所（TAIFEX）資料自動化抓取與視覺化分析工具，支援 API 抓取外資法人、期貨行情、選擇權指標等資料，並每日更新 CSV 與折線圖。

📂 專案結構

C:\Taifex\
├── venv32\                  # 專案虛擬環境（Python 3.9 / 32bit）
├── data\                   # 儲存每日 CSV 資料
├── visualize\              # 儲存折線圖圖片
├── screenshot\             # 擷取網頁畫面（如有）
├── taifex_dom_foreign_simple.py  # 外資資料抓取主程式
├── test_api.py             # API 測試工具
├── run_taifex.bat          # 啟動批次檔（可選）
└── README.md               # 本說明文件




環境啟動方式

PowerShell 啟動流程：

cd C:\Taifex
.\venv32\Scripts\Activate.ps1
python taifex_dom_foreign_simple.py



cmd.exe 啟動流程：

cd /d C:\Taifex
call .\venv32\Scripts\activate.bat
python taifex_dom_foreign_simple.py


🧪 API 測試工具
執行  可確認 TAIFEX API 是否正常回傳資料：

python test_api.py


📁 路徑管理建議（程式內）
請使用以下方式自動抓取專案根目錄，避免硬編路徑：

import os
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")


📌 虛擬環境管理建議
• 	每個專案擁有獨立venv32 ，避免套件衝突
• 	套件安裝建議使用 ：requirements.txt

pip freeze > requirements.txt
pip install -r requirements.txt


🚀 建議建立啟動批次檔 

run_taifex.bat

@echo off
cd /d C:\Taifex
call .\venv32\Scripts\activate.bat
python taifex_dom_foreign_simple.py
pause


📎 備註
• 	若需與其他專案（如元大 API）共用套件，請勿混用虛擬環境
• 	建議每個專案獨立管理、獨立啟動，維護更穩定
• 	若需排程自動執行，可搭配 Windows Task Scheduler 指向 

=====================================================
20251128

# Taifex-Debug 專案

## 專案目的
此專案用於自動化抓取台灣期交所 (TAIFEX) 各類金融指標 (F1–F20)，並保存原始快照、解析後資料與錯誤紀錄，方便後續 debug 與分析。

---

## 專案結構
- `f1/`：台指期貨外資淨口數  
- `f10/`：台指選擇權每日交易行情  
- `f20/`：其他金融指標  
- `issues/`：錯誤紀錄 (Markdown 格式)  
- `README.md`：專案總覽  
- `requirements.txt`：套件需求  

---

## 子模組說明
- [F1 模組說明](f1/README_f1.md)  
- [F10 模組說明](f10/README_f10.md)  
- [F20 模組說明](f20/README_f20.md)  

---

## 錯誤回報流程
1. 錯誤時自動產生 `error.html` 與 `error.png`  
2. 在 `issues/` 建立 Markdown 紀錄，包含：
   - 日期  
   - 模組名稱  
   - 錯誤訊息  
   - 對應快照檔案  
3. 上傳到 GitHub，方便 Copilot debug


