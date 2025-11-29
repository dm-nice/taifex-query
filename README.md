##2025.11.29

README 範例段落
markdown
## Debug Pipeline 使用說明

為了提升錯誤回報與分析效率，本專案提供整合工具 `utils/debug_pipeline.py`。  
此模組會在程式執行出錯時，自動產生完整的錯誤紀錄 Markdown 檔案，並存放於 `issues/` 目錄下。

### 功能
- 自動建立錯誤紀錄 `.md` 檔案
- 紀錄錯誤摘要與完整 Traceback
- 抽取 HTML `<select>` 與 `<table>` 區塊，方便檢查 DOM 結構
- 附加 `logs/` 中的錯誤訊息，完整呈現執行過程

### 使用方式
在模組程式中加入以下範例：

```python
from utils.debug_pipeline import debug_pipeline

try:
    run_f10_fetcher()
except Exception as e:
    snapshots = [
        "raw/f10/f10_init_2025-11-27.html",
        "raw/f10/f10_after_2025-11-27.html",
        "raw/f10/f10_error_2025-11-27.html"
    ]
    log_file = "logs/f10_fetcher.log"

    # 一鍵完成錯誤紀錄
    debug_pipeline("F10", e, snapshots, log_file)
輸出結果
產生檔案：issues/YYYY-MM-DD_F10_error.md

內容包含：

錯誤摘要與 Traceback

DOM <select> 與 <table> 區塊

log 錯誤訊息

優點
錯誤回報流程完全自動化

Push 到 GitHub 後即可快速定位問題

減少人工複製貼上，提高 Debug 效率

程式碼

---

這樣一段放進 README，就能讓任何人（包括你未來的協作者）快速理解 `debug_pipeline.py` 的用途與操作方式。  

要不要我再幫你設計一個 **範例輸出 `.md`**（完整錯誤紀錄檔案），讓你直觀看到 debug_pipeline 生成的結果長什麼樣子？
今天
幫我產生一份最新的README.md 我要更新Github
好的，DM！我來幫你產生一份 最新的 README.md 範本，結合我們剛剛討論的專案結構、錯誤回報流程、以及整合版 debug_pipeline.py。你可以直接拿去更新 GitHub。

📄 最新 README.md 範本
markdown
# Taifex-Debug 專案

## 專案目的
此專案用於自動化抓取台灣期交所 (TAIFEX) 各類金融指標 (F1–F20)，並保存原始快照、解析後資料與錯誤紀錄，方便後續 debug 與分析。  
專案設計重視 **模組化、可維護性、錯誤回報自動化**，並結合 GitHub 版本控管，提升協作效率。

---

## 專案結構
Taifex-Debug/ ├── README.md # 主專案說明 ├── utils/ # 共用工具模組 │ ├── error_reporter.py # 自動產生錯誤紀錄 │ ├── html_cleaner.py # 抽取 <select>/<table> DOM 區塊 │ ├── log_parser.py # 附加 log 錯誤訊息 │ └── debug_pipeline.py # 整合版 Debug Pipeline ├── f1/ │ ├── f1_fetcher.py │ ├── raw/ │ ├── logs/ │ ├── data/ │ └── README_f1.md ├── f10/ │ ├── f10_fetcher.py │ ├── raw/ │ ├── logs/ │ ├── data/ │ └── README_f10.md ├── f20/ │ ├── f20_fetcher.py │ ├── raw/ │ ├── logs/ │ ├── data/ │ └── README_f20.md └── issues/ ├── 2025-11-27_f10_error.md └── 2025-11-28_f1_missing_table.md

程式碼

---

## 子模組說明
- [F1 模組說明](f1/README_f1.md)  
- [F10 模組說明](f10/README_f10.md)  
- [F20 模組說明](f20/README_f20.md)  

---

## 錯誤回報流程

### Debug Pipeline
專案提供整合工具 `utils/debug_pipeline.py`，在程式出錯時自動產生完整錯誤紀錄。

#### 功能
- 自動建立錯誤紀錄 `.md` 檔案  
- 紀錄錯誤摘要與完整 Traceback  
- 抽取 HTML `<select>` 與 `<table>` 區塊  
- 附加 `logs/` 中的錯誤訊息  

#### 使用方式
```python
from utils.debug_pipeline import debug_pipeline

try:
    run_f10_fetcher()
except Exception as e:
    snapshots = [
        "raw/f10/f10_init_2025-11-27.html",
        "raw/f10/f10_after_2025-11-27.html",
        "raw/f10/f10_error_2025-11-27.html"
    ]
    log_file = "logs/f10_fetcher.log"

    # 一鍵完成錯誤紀錄
    debug_pipeline("F10", e, snapshots, log_file)
輸出結果
產生檔案：issues/YYYY-MM-DD_F10_error.md

內容包含：

錯誤摘要與 Traceback

DOM <select> 與 <table> 區塊

log 錯誤訊息

檔案命名規則
raw/f10/f10_init_YYYY-MM-DD.html：初始頁面快照

raw/f10/f10_after_YYYY-MM-DD.html：查詢後頁面快照

raw/f10/f10_txo_YYYY-MM-DD.html：最終表格快照

raw/f10/f10_error_YYYY-MM-DD.html：錯誤快照

logs/f10/f10_fetcher.log：執行紀錄

issues/YYYY-MM-DD_module_error.md：錯誤紀錄

套件需求
請先安裝必要套件：

bash
pip install -r requirements.txt
優點
錯誤回報流程完全自動化

Push 到 GitHub 後即可快速定位問題

減少人工複製貼上，提高 Debug 效率

結構清楚，方便擴充與維護

程式碼

---

這份 `README.md` 已經整合了：  
- 專案結構  
- 子模組連結  
- Debug Pipeline 使用方式  
- 錯誤回報流程與範例  

你只要把它更新到 `c:\taifex\README.md`，GitHub 上就會有完整的專案說明。  

要不要我再幫你產生一份 **範例輸出錯誤紀錄 `.md`**，讓你直觀看到 `debug_pipeline` 生成的結果？






