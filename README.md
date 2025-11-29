20251129 13:50

本專案使用 [Mermaid](https://mermaid-js.github.io/) 流程圖語法，請在 GitHub 上開啟「顯示流程圖」功能以正確呈現。



📄 最終整合版 README.md
markdown
# Taifex-Debug 專案

## 目錄
- [專案目的](#專案目的)
- [專案結構](#專案結構)
- [子模組說明](#子模組說明)
- [錯誤回報流程](#錯誤回報流程)
  - [Debug Pipeline 使用方式](#debug-pipeline)
  - [檔案命名規則](#檔案命名規則)
- [套件需求](#套件需求)
  - [requirements.txt](#套件需求)
  - [requirements-dev.txt](#requirements-devtxt)
- [Commit Message 規範](#推薦-commit-message-格式)
- [流程圖總覽](#流程圖總覽)
  - [Commit 流程圖](#commit-流程圖)
  - [開發流程圖](#開發流程圖)
  - [專案總覽圖](#專案總覽圖)
  - [錯誤回報流程圖](#錯誤回報流程圖)
  - [資料流程圖](#資料流程圖)
  - [專案維護流程圖](#專案維護流程圖)


## 專案目的
此專案用於自動化抓取台灣期交所 (TAIFEX) 各類金融指標 (F1–F20)，並保存原始快照、解析後資料與錯誤紀錄，方便後續 debug 與分析。  
專案設計重視 **模組化、可維護性、錯誤回報自動化**，並結合 GitHub 版本控管，提升協作效率。

---

## 專案結構

```
Taifex-Debug/
├── README.md                    # 專案總說明文件
├── requirements.txt             # 執行環境套件需求
├── requirements-dev.txt         # 開發環境套件需求 (測試/格式化/型別檢查)
├── .gitignore                   # Git 忽略規則
├── .pre-commit-config.yaml      # pre-commit 設定檔 (black/flake8/isort/mypy)

├── run.py                       # 主程式入口，統一執行流程
├── taifex_dashboard.py          # 儀表板整合，視覺化金融指標
├── Taifex.txt                   # 臨時文字紀錄

├── utils/                       # 共用工具模組
│   ├── error_reporter.py        # 自動產生錯誤紀錄
│   ├── html_cleaner.py          # 抽取 <select>/<table> DOM 區塊
│   ├── log_parser.py            # 附加 log 錯誤訊息
│   └── debug_pipeline.py        # 整合錯誤回報流程，一鍵生成 issues

├── f1.py                        # F1 指標抓取程式
├── f10_fetcher.py               # F10 指標抓取程式
├── f20/                         # F20 模組目錄 (抓取程式與資料)

├── f8_api.py                    # F8 API 抓取程式
├── f9_api.py                    # F9 API 抓取程式
├── get_tx_foreign_oi.py         # 外資 OI API 抓取程式
├── factors_taifex.py            # 指標計算 (因子分析)

├── taifex_dom_foreign_simple.py       # 外資 DOM 簡化版
├── taifex_dom_foreign_week.py         # 外資 DOM 週資料
├── taifex_foreign_html.py             # 外資 HTML 抓取
├── taifex_foreign_html_multi.py       # 外資 HTML 多頁抓取
├── taifex_fullpage_screenshot.ocr.py  # 全頁截圖 + OCR 處理

├── debug_f1.py                  # F1 模組除錯腳本
├── debug_f2.py                  # F2 模組除錯腳本
├── test_20.py                   # F20 測試腳本
├── test_api.py                  # API 測試腳本

├── data/                        # 解析後的資料存放
├── raw/                         # 原始快照 HTML
├── logs/                        # 執行紀錄 log
├── issues/                      # 錯誤紀錄 Markdown
├── visualize/                   # 視覺化模組 (折線圖、趨勢圖)
├── factors/                     # 技術指標與因子模組
├── screenshot/                  # 執行過程截圖或 OCR 輸出
├── TEMP/                        # 暫存或未整合模組
├── venv32/                      # Python 虛擬環境 (32bit)
├── __pycache__/                 # Python 編譯快取
├── .git/                        # Git 版本控制資料夾
└── .github/                     # GitHub CI/CD 或專案設定
```











「專案狀態徽章」

```markdown
![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Last Update](https://img.shields.io/badge/Last_Update-2025--11--29-yellow)


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
若使用虛擬環境，請先執行 `python -m venv venv32 && source venv32/bin/activate`。


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

## Commit 流程圖

```mermaid
flowchart TD
    A[程式執行出錯] --> B[debug_pipeline 自動產生 issues/ 錯誤紀錄]
    B --> C[git add .]
    C --> D[git commit -m "錯誤紀錄 F10 - 2025-11-27"]
    D --> E{pre-commit 檢查}
    E -->|通過| F[git push 到 GitHub]
    E -->|失敗| G[修正程式碼並重新 commit]


-------------------


## ✅ 效果
- 在 GitHub README 中會顯示一個 **Mermaid 流程圖**  
- 清楚展示完整流程：  
  1. 程式出錯  
  2. `debug_pipeline` 自動產生錯誤紀錄  
  3. commit 前跑 pre-commit 檢查  
  4. 通過才 push 到 GitHub  

---
## 開發流程圖

```mermaid
flowchart TD
    A[新增模組需求] --> B[建立模組目錄 (f1/f10/f20)]
    B --> C[撰寫 fetcher.py 抓取程式]
    C --> D[本地測試與除錯]
    D --> E[debug_pipeline 自動產生 issues/ 錯誤紀錄]
    E --> F[git add .]
    F --> G[git commit -m "新增 F10 模組"]
    G --> H{pre-commit 檢查}
    H -->|通過| I[git push 到 GitHub]
    H -->|失敗| J[修正程式碼並重新 commit]


---

## ✅ 效果
- 在 GitHub README 中會顯示一個 **Mermaid 流程圖**  
- 清楚展示完整開發週期：  
  1. 新增模組需求  
  2. 建立目錄並撰寫 `fetcher.py`  
  3. 測試與除錯  
  4. `debug_pipeline` 自動產生錯誤紀錄  
  5. commit 前跑 pre-commit 檢查  
  6. 通過才 push 到 GitHub  

---

## 專案總覽圖

```mermaid
graph TD
    subgraph Utils [utils/ 工具模組]
        U1[error_reporter.py]
        U2[html_cleaner.py]
        U3[log_parser.py]
        U4[debug_pipeline.py]
    end

    subgraph F1 [f1 模組]
        F1A[f1_fetcher.py]
    end

    subgraph F10 [f10 模組]
        F10A[f10_fetcher.py]
    end

    subgraph F20 [f20 模組]
        F20A[f20_fetcher.py]
    end

    %% 關聯線
    F1A --> U1
    F1A --> U2
    F1A --> U3
    F1A --> U4

    F10A --> U1
    F10A --> U2
    F10A --> U3
    F10A --> U4

    F20A --> U1
    F20A --> U2
    F20A --> U3
    F20A --> U4


---

## ✅ 效果
- 在 GitHub README 中會顯示一個 **Mermaid 圖表**  
- 清楚展示：  
  - `f1/f10/f20` 模組都依賴 `utils/` 工具模組  
  - `debug_pipeline.py` 是核心，所有模組都會呼叫它來產生錯誤紀錄  

---

這樣你的 README 就同時有：
- **Commit 流程圖**  
- **開發流程圖**  
- **專案總覽圖**  

-------
## 錯誤回報流程圖

```mermaid
flowchart TD
    A[程式執行出錯] --> B[debug_pipeline.py 啟動]
    B --> C[error_reporter.py 建立錯誤紀錄檔案]
    B --> D[html_cleaner.py 抽取 <select>/<table> 區塊]
    B --> E[log_parser.py 附加 log 錯誤訊息]
    C --> F[產生 issues/YYYY-MM-DD_module_error.md]
    D --> F
    E --> F
    F --> G[錯誤紀錄完成，推送到 GitHub]


---

## ✅ 效果
- 在 GitHub README 中會顯示一個 **Mermaid 流程圖**  
- 清楚展示：  
  1. 程式出錯 → `debug_pipeline.py` 啟動  
  2. 呼叫 `error_reporter.py` 建立錯誤紀錄  
  3. 呼叫 `html_cleaner.py` 抽取 DOM 區塊  
  4. 呼叫 `log_parser.py` 附加 log 訊息  
  5. 最終產生 `.md` 錯誤紀錄檔，放到 `issues/`  

--------

## 資料流程圖

```mermaid
flowchart LR
    A[Fetcher.py 抓取資料] --> B[raw/ 原始快照]
    B --> C[logs/ 執行紀錄]
    C --> D[data/ 解析後資料]
    D --> E{是否出錯?}
    E -->|否| F[正常流程完成]
    E -->|是| G[issues/ 錯誤紀錄 .md]
    G --> H[推送到 GitHub]



---

## ✅ 效果
- 在 GitHub README 中會顯示一個 **Mermaid 流程圖**  
- 清楚展示資料流向：  
  1. `fetcher.py` 抓取資料  
  2. 存到 `raw/` 原始快照  
  3. 產生 `logs/` 執行紀錄  
  4. 解析後存到 `data/`  
  5. 若出錯 → `issues/` 自動生成錯誤紀錄  
  6. 最後推送到 GitHub  

---



## 專案維護流程圖

```mermaid
flowchart TD
    A[程式執行出錯] --> B[debug_pipeline 產生 issues/ 錯誤紀錄]
    B --> C[檢視錯誤紀錄並分析問題]
    C --> D[修正程式碼]
    D --> E[本地測試與驗證]
    E --> F{測試是否通過?}
    F -->|否| D
    F -->|是| G[git add .]
    G --> H[git commit -m "修正錯誤並更新模組"]
    H --> I{pre-commit 檢查}
    I -->|通過| J[git push 到 GitHub]
    I -->|失敗| D
    J --> K[更新 README.md 說明]
    K --> L[專案維護完成]



---

## ✅ 效果
- 在 GitHub README 中會顯示一個 **Mermaid 流程圖**  
- 清楚展示完整維護週期：  
  1. 程式出錯 → `debug_pipeline` 產生錯誤紀錄  
  2. 分析錯誤並修正程式碼  
  3. 測試驗證 → commit → pre-commit 檢查  
  4. push 到 GitHub  
  5. 更新 README.md 說明 → 維護完成  

---

這樣你的 README 就同時擁有：  
- **Commit 流程圖**  
- **開發流程圖**  
- **專案總覽圖**  
- **錯誤回報流程圖**  
- **資料流程圖**  
- **專案維護流程圖**  


