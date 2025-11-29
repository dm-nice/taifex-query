##2025.11.29 PM 12:21

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

python

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





程式碼






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