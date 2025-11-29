20251129 12:40

📄 最終整合版 README.md
markdown
# Taifex-Debug 專案

## 專案目的
此專案用於自動化抓取台灣期交所 (TAIFEX) 各類金融指標 (F1–F20)，並保存原始快照、解析後資料與錯誤紀錄，方便後續 debug 與分析。  
專案設計重視 **模組化、可維護性、錯誤回報自動化**，並結合 GitHub 版本控管，提升協作效率。

---

## 專案結構

```
Taifex-Debug/
├── README.md               # 主專案說明
├── utils/                  # 共用工具模組
│   ├── error_reporter.py   # 自動產生錯誤紀錄
│   ├── html_cleaner.py     # 抽取 <select>/<table> DOM 區塊
│   ├── log_parser.py       # 附加 log 錯誤訊息
│   └── debug_pipeline.py   # 整合版 Debug Pipeline
├── f1/
│   ├── f1_fetcher.py
│   ├── raw/
│   ├── logs/
│   ├── data/
│   └── README_f1.md
├── f10/
│   ├── f10_fetcher.py
│   ├── raw/
│   ├── logs/
│   └── README_f10.md
└── issues/                 # 錯誤紀錄 Markdown 檔案
    ├── 2025-11-27_f10_error.md
    └── 2025-11-28_f1_missing_table.md
```


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
推薦 Commit Message 格式
為了版本控管清晰，建議使用以下格式：

程式碼
[錯誤紀錄] F10 TXO 表格載入失敗 - 2025-11-27
[修正] F1 模組 selector 更新
[新增] debug_pipeline.py 整合工具
程式碼

---


