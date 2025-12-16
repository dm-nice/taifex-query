# F11 Project Context

## Project Overview

模組編號: F11  
模組名稱: 加權股價收盤指數 (Taiwan Weighted Stock Index)  
功能說明: 自動從 TWSE 官網抓取加權股價收盤指數，輸出統一格式

## Objective

新增一個 F11 模組，提供實時加權股價收盤指數的抓取功能。

- 從 TWSE 官網自動抓取數據
- 輸出統一格式：`YYYY.MM.DD  F11: 加權股價收盤指數 : [數值] [數據來源]`
- 完整的異常處理和日誌記錄
- 遵循 OpenSpec 4 相位框架

## Data Source

- **URL**: <https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html>
- **Type**: Web Scraping (HTML)
- **Format**: HTML Table
- **Source Name**: TWSE (台灣證券交易所)

## Output Format

```
成功: 2025.12.17  F11: 加權股價收盤指數 : 18254.50 [TWSE]
失敗: F11 錯誤: 該日無交易資料（可能是假日或休市日） [TWSE]
異常: F11 錯誤: 網路連線失敗 [TWSE] (2025-12-17 14:30:45)
```

## Tech Stack

- **Runtime**: Python 3.9 (venv32)
- **Web Scraping**: requests + BeautifulSoup4 或 Selenium
- **Data Processing**: pandas
- **Testing**: pytest
- **Logging**: Python logging module

## Development Conventions

遵循 OpenSpec 4 相位框架：

- **Phase 1**: 文檔化 (design.md, tasks.md, specifications)
- **Phase 2**: 代碼實現 (f11_openspec_dev.py)
- **Phase 3**: 測試 (test_f11_openspec.py, pytest)
- **Phase 4**: 部署 (modules/f11_fetcher.py)

## Key Files Structure

```
f11_package/
├── openspec/                    # OpenSpec 配置
│   ├── project.md              # 本文件
│   ├── AGENTS.md               # AI Assistant 工作流程
│   ├── specs/                  # 規格文檔
│   └── changes/                # 變更提案
├── design.md                   # Phase 1: 設計文檔
├── tasks.md                    # Phase 1: 16 個任務清單
├── f11_openspec_dev.py         # Phase 2: 代碼實現
├── test_f11_openspec.py        # Phase 3: 測試套件
└── README.md                   # 模組說明
```

## Team & Communication

- 開發者: 自己完成
- 評審者: Claude AI Assistant
- 通訊方式: 終端機命令行

## Success Criteria

- [ ] design.md 完成（>300 行，詳細規格）
- [ ] tasks.md 完成（16 個任務，全部標記完成）
- [ ] f11_openspec_dev.py 完成並本地測試通過
- [ ] test_f11_openspec.py 完成，15+ 個測試全過
- [ ] 生產部署：modules/f11_fetcher.py 已上線
- [ ] 生產驗證：實時抓取成功，輸出正確格式
