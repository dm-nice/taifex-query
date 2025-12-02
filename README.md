20251130 13:25

README.md 範例
markdown
Taifex 指標自動化專案
本專案用於自動化抓取台灣期貨交易所 (TAIFEX) 的每日指標資料，並統一輸出格式，方便後續分析與儀表板展示。

📂 專案結構
text
C:\Taifex\
├── run.py                  # 主控程式，執行模組並集中輸出 JSON 與 log 到 data/
├── run_test.py             # 驗收測試用，可單獨執行指定模組
├── run_bak.py              # 舊版備份，可保留比對或刪除
├── README.md               # 專案說明文件
├── .pre-commit-config.yaml # Git pre-commit 設定（格式化、lint 等）
├── .gitignore              # 排除 venv、log、data 等不需 commit 的檔案
│
├── data\                   # 所有執行結果集中輸出目錄（由 run.py 控制）
│   ├── YYYY-MM-DD_f01.json
│   ├── YYYY-MM-DD_run.log
│   ├── YYYY-MM-DD_f01_dev.json
│   ├── YYYY-MM-DD_run_dev.log
│   └── ...
│
├── dev\                    # 驗收模組目錄，外包商交付放這裡
│   ├── f01_fetcher_dev.py
│   └── ...
│
├── modules\                # 正式模組目錄，驗收通過後移入
│   ├── f01_fetcher.py
│   └── ...
│
├── utils\                  # 工具模組（供 run.py 或模組引用）
│   ├── debug_pipeline.py   # run.py 用來格式化錯誤訊息
│   ├── __init__.py         # 套件初始化，讓 utils 可被 import
│   └── __pycache__\        # Python 快取目錄，自動產生可忽略
│
├── TEMP\                   # 暫存資料夾，可排除版本控管
├── venv32\                 # Python 虛擬環境（32bit）
├── .github\                # GitHub CI/CD 或 issue template 可放這裡
└── .git\                   # Git 版本控管資料夾（勿動）
⚙️ 執行流程
使用者執行：

bash
python run.py 2025-12-01 dev --module f01_fetcher_dev_xxx
run.py 透過 importlib.import_module() 載入指定模組（例如 dev/f01_fetcher_dev_xxx.py）。

呼叫模組的 fetch(date) 函式，並將查詢日期傳入。

模組回傳一個 dict，包含 status、module、source 與 data 欄位。

run.py 接收後的處理：

檢查回傳格式是否正確（必須是 dict 且含有 status）。

呼叫 build_flat_record()，將模組回傳的 dict 轉換成「平坦化資料」。

寫入檔案：

JSON → data/{執行日}_{模組}.json 或 data/{執行日}_{模組}_dev.json

Log → data/{執行日}_run.log 或 data/{執行日}_run_dev.log

Log 檔案中會記錄：

[START] / [SUCCESS] / [FAIL] / [ERROR] / [INVALID]

一行平坦資料（TSV 格式），方便人工檢視。

📘 外包開發指南
1. 文件參考
docs/interface_spec.md：定義模組輸入輸出格式與錯誤回報規範

docs/outsourcing_spec.md：各指標資料來源與欄位說明（例如 F1）

2. 開發規範
請在 dev/ 目錄下建立對應模組檔案，例如：

程式碼
dev/f01_fetcher_dev.py
程式需提供函式：

python
def fetch(date: str) -> dict
成功輸出範例：
json
{
  "module": "f01",
  "date": "2025-12-01",
  "status": "success",
  "summary": "F1: 台指期貨外資淨口數 (OI): 1334（來源：TAIFEX）"
}
失敗輸出範例：
json
{
  "module": "f01",
  "date": "2025-12-01",
  "status": "fail",
  "error": "找不到欄位 '交易人名稱'，df.columns = ['交易人', '多單口數', '空單口數']"
}
3. 驗收流程
執行：

bash
python run.py 2025-12-01 dev
成功時會產生 data/ 下的 JSON 檔案

失敗時會產生 data/ 下的錯誤紀錄（log 檔案中有詳細訊息）

============================================================================
📂 README.md 範例內容
markdown
# 專案說明

本專案主要透過 `run.py` 統一呼叫各模組（如 f01），並將結果落地到 `data/` 與 `logs/` 目錄。以下說明執行流程與關鍵設計。

---

### 執行流程：run.py → f01
1. 使用者執行：
   ```bash
   python run.py 2025-12-01 dev --module f01_fetcher_dev_xxx
run.py 透過 importlib.import_module() 載入指定模組（例如 dev/f01_fetcher_dev_xxx.py）。

呼叫模組的 fetch(date) 函式，並將查詢日期傳入。

模組回傳一個 dict，包含 status、module、source 與 data 欄位。

run.py 接收後的處理
檢查回傳格式是否正確（必須是 dict 且含有 status）。

呼叫 build_flat_record()，將模組回傳的 dict 轉換成「平坦化資料」。

寫入檔案：

JSON → data/{執行日}_{模組}.json 或 data/{執行日}_{模組}_dev.json

Log → logs/{執行日}_run.log 或 logs/{執行日}_run_dev.log

Log 檔案中會記錄：

[START] / [SUCCESS] / [FAIL] / [ERROR] / [INVALID]

一行平坦資料（TSV 格式），方便人工檢視。

關鍵點
模組責任：外包商依照規範書撰寫 fetch()，負責抓取資料並回傳 dict。

run.py 責任：驗收模組回傳 → 平坦化 → 落地 JSON 與 log。

資料一致性：不管成功或失敗，run.py 都會寫入一筆 JSON 與一行 log，確保每次執行都有紀錄。

平坦化設計：同一行包含多項欄位（日期、數值、來源、狀態、模組），方便後續分析。

程式碼

---

📌  README.md 就能清楚交代 **執行流程 → 接收處理 → 關鍵點**，外包商或團隊成員一看就懂。  






