# Project Context

## Purpose

**F01 模組** - 抓取台指期貨外資的未平倉淨口數 (Open Interest)

- 目標：從 TAIFEX 網站抓取台指期貨外資的未平倉多方、空方口數
- 用途：用於分析外資籌碼變化，預測台指期貨走勢
- 難度：⭐⭐☆☆☆ (2/5)
- 資料來源：台灣期貨交易所 (TAIFEX)

## Tech Stack

- **語言**: Python 3.9+
- **核心套件**: requests, pandas, beautifulsoup4, lxml
- **資料格式**: HTML 表格解析（MultiIndex 支援）
- **輸出格式**: 文字格式 v5.0（統一規範）

## Project Conventions

### Code Style

- **文件編碼**: UTF-8
- **命名規則**: 
  - 模組代號: `fXX` (小寫, e.g., `f01`)
  - 函式名: snake_case (e.g., `fetch()`, `format_f01_output()`)
  - 常數名: UPPER_CASE (e.g., `MODULE_ID = "f01"`)

- **註解**: 中文註解，清晰說明邏輯和已知限制
- **日誌記錄**: 使用 Python logging 模組

### Architecture Patterns

- **統一介面**: 所有模組提供 `fetch(date: str) -> dict` 方法
- **錯誤處理**: 完整的 try-catch 和錯誤日誌
- **資料轉換**: 
  - 字串轉整數（處理千分位逗號）
  - MultiIndex 表頭支援
  - 統一輸出格式（日期.欄位: 數值 [來源]）

### Testing Strategy

- **單元測試**: 使用 pytest（見 `test_f01_auto.py`）
- **測試案例**:
  - 驗證抓取成功（返回正確欄位）
  - 驗證資料類型（整數/字串）
  - 驗證錯誤處理（網路異常/無效日期）
  
- **驗收模式**: `python run.py <date> dev` 模式

### Git Workflow

- **分支**: 在 `dev/` 目錄開發，穩定版在 `modules/` 目錄
- **提交**: 包含清晰的 commit message（中英文皆可）
- **版本控制**: 規格書 (.md) 和程式碼 (.py) 分開管理

## Domain Context

### TAIFEX 資料特徵

- **URL**: `https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date=YYYY/MM/DD`
- **表格結構**: MultiIndex（多層表頭）
  - 第一層：交易對象（「外資及陸資」、「投信」等）
  - 第二層：「未平倉多方」、「未平倉空方」等欄位

- **目標欄位**: 
  - 交易對象：外資及陸資（或外資）
  - 未平倉多方：Long position (口)
  - 未平倉空方：Short position (口)
  - 計算得出：淨額 = 多方 - 空方

### 輸出格式（v5.0）

**成功**:
```
2025.12.04  F01: 台指期貨外資 [未平倉] [多空淨額] : -26,823 口 [TAIFEX]
```

**失敗**:
```
F01 錯誤: 網路連線失敗 [TAIFEX]
```

## Important Constraints

⚠️ **關鍵限制：API 無視日期參數**

- TAIFEX 的 futContractsDate 端點**無論傳入什麼日期，都回傳最後交易日的資料**
- 已測試驗證：2025-12-04、2025-11-28、2024-12-04 回傳內容完全相同
- 根本原因：期交所網頁需要 JavaScript 互動（datepicker + 表單提交）
- 現在的 requests 方案無法觸發 JavaScript
- **解決方案**：若需支援歷史日期，需升級至 Selenium 或 Playwright（完整瀏覽器自動化）

## External Dependencies

### 主要資料源
- **期交所官網**: https://www.taifex.com.tw/
- **查詢介面**: futContractsDate 頁面
- **更新頻率**: 每個交易日

### Python 套件依賴
- `requests` - HTTP 請求
- `pandas` - 資料分析和表格操作
- `beautifulsoup4` - HTML 標籤解析（備用方案）
- `lxml` - HTML 解析加速器

### 相關規範文件
- [共同開發規範書](../../共同開發規範書_V1.md) - 所有模組的通用規範
- [F01 規格書](../f01_fetcher_開發規範書.md) - F01 專屬詳細規格
