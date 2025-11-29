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