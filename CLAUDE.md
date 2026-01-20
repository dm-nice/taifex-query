# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TAIFEX 爬蟲系統 - 自動化爬取台灣期貨交易所及台股相關金融指標。

**核心功能**:
- 自動抓取 25 個金融指標 (F01-F25)
- 每日執行兩次排程：日盤 (F01-F20) + 夜盤 (F21-F25)
- 資料不完整時自動降級查詢前一交易日
- 同日多次執行時版本號自動遞增 (v1, v2, ...)

## Quick Start

### Installation & Setup

```bash
# 安裝依賴
pip install -r requirements.txt

# 首次運行前必須安裝 Playwright 瀏覽器
playwright install chromium
```

### Running the Scrapers

```bash
# 日盤爬蟲 (F01-F20)
python daytime_query.py

# 夜盤爬蟲 (F21-F25)
python nighttime_query.py
```

### Development & Debugging

```bash
# 完整測試
python dev/tests/test_daytime_all.py

# 診斷工具 (測試特定資料來源)
python dev/diagnose_daytime.py         # 日盤各項指標 (F01-F20)
python dev/diagnose_twse.py            # TWSE API (F11-F17)
python dev/diagnose_remaining.py       # F08-F10 & 其他指標
python dev/test_nighttime_wantgoo.py   # Wantgoo 爬蟲 (F21-F25)
```

## Architecture

### Entry Points

**`daytime_query.py`** & **`nighttime_query.py`**:
- 單純的入口點，呼叫對應爬蟲函式並將結果存檔
- 輸出檔案格式: `taifex_YYYY.MM.DD_v{version}.md` (日盤) 或 `taifex_night_YYYY.MM.DD_v{version}.md` (夜盤)

### Core Components

**Scrapers** (`scrapers/`):
- `daytime.py`:
  - `query_daytime_data()` - 主入口，協調 F01-F20 的抓取
  - TAIFEX 抓取: `query_taifex_foreign_holdings()` (F01-F03), `query_taifex_settlement()` (F04), `query_taifex_options_volume()` (F05), `query_taifex_pc_ratio()` (F07)
  - TWSE 抓取: `query_twse_market_data()` (F11-F12), `query_twse_stock_day()` (F14-F16), `query_twse_foreign_buy()` (F17)
  - F13 計算: `calculate_f13_ma20()` (依賴 F11 與歷史收盤數據計算 20 日均線)
  - 降級邏輯: 當日資料缺失時自動遞迴查詢前一交易日

- `nighttime.py`:
  - `query_nighttime_data()` - 主入口，協調 F21-F25 的抓取
  - `query_wantgoo_nighttime()` - 使用 Playwright 動態渲染抓取 Wantgoo 全球市場數據 (F21-F25)
  - 使用反偵測技巧 (禁用 webdriver 標誌、自訂 User-Agent、等待 DOM 加載)

**Utils** (`utils/`):
- `date_utils.py`:
  - `get_current_taiwan_date()` - 取得台灣當前日期 (格式 YYYY.MM.DD)
  - `get_previous_trading_day()` - 取得前一交易日
  - `is_trading_day()` - 判斷是否為交易日 (排除週末/國定假日)
  - 國定假日硬編碼在此，需定期更新

- `helpers.py`:
  - `save_to_markdown(data_list, date_str, version, filename_prefix)` - 存檔
  - `get_next_version(date_str, filename_prefix)` - 自動版本遞增邏輯
  - 輸出格式: `2026.01.15 F01 台指期貨-外資 [ 未平倉 多空淨額: -181389口 ]`

### Data Flow - Daytime (F01-F20)

```
daytime_query.py
    ↓
scrapers/daytime.py (query_daytime_data)
    ├─ query_taifex_foreign_holdings() → F01, F02, F03
    ├─ query_taifex_settlement() → F04
    ├─ query_taifex_options_volume() → F05
    ├─ query_taifex_pc_ratio() → F07
    ├─ query_twse_market_data() → F11, F12
    ├─ query_twse_stock_day(session) → F14, F15, F16
    ├─ query_twse_foreign_buy(session) → F17
    └─ calculate_f13_ma20(session) → F13 (依賴 F11 收盤價 + 歷史收盤數據)
    ↓
檢查缺失: expected_codes (F01-F07, F11-F17) - actual_codes
    ├─ 若有缺失 → 遞迴呼叫 query_daytime_data(前一交易日)
    └─ 補齊缺失的指標
    ↓
utils/helpers.py (save_to_markdown)
    ↓
output/taifex_YYYY.MM.DD_v{version}.md
```

### Data Flow - Nighttime (F21-F25)

```
nighttime_query.py
    ↓
scrapers/nighttime.py (query_nighttime_data)
    ↓
query_wantgoo_nighttime() [使用 Playwright]
    ├─ 啟動 Chromium 瀏覽器 (headless 模式)
    ├─ 訪問 https://www.wantgoo.com/global
    ├─ 等待 DOM 加載 + 4 秒等待 JavaScript 執行
    ├─ 提取頁面文本並按行解析
    └─ 匹配指標關鍵詞 (NASDAQ, 費城半導體, EM-ND, ADR, 台指期盤後)
        → F21, F22, F23, F24, F25
    ↓
utils/helpers.py (save_to_markdown, filename_prefix="taifex_night_")
    ↓
output/taifex_night_YYYY.MM.DD_v{version}.md
```

### Session Management

多個爬蟲函式需要共用 HTTP Session 以維持 cookies 及連接池：
- `query_twse_market_data()` 會自動建立 session (獨立)
- `query_twse_stock_day()` 及 `query_twse_foreign_buy()` 接收 `session` 參數 (共用)
- `calculate_f13_ma20()` 接收 `session` 參數 (需要多次請求)

## Key Data Structure

所有爬蟲函式回傳 None 或 List[Dict]，字典結構：

```python
{
    "f_code": "F01",                    # 指標代碼
    "name": "台指期貨-外資",             # 名稱
    "field": "未平倉 多空淨額",         # 欄位說明
    "value": "-181389",                 # 值 (字串)
    "unit": "口"                         # 單位
}
```

特殊值：
- `value == "查詢失敗"`: 爬蟲失敗，輸出為 `[ 查詢失敗 ]`
- `value == "保留項目"`: F08-F10 保留，輸出為 `[保留項目]`

## Important Notes

### Date Handling

- 所有日期使用 **台灣時區** (UTC+8) 並採用 `YYYY.MM.DD` 格式
- `get_current_taiwan_date()` 自動計算台灣時刻 (from `utils/date_utils.py:get_taiwan_now()`)
- TWSE API 使用民國年格式 (例: 115/01/15)，轉換邏輯: `year - 1911`
- 交易日判定: 排除週末 + 國定假日 (在 `utils/date_utils.py` 中硬編碼，需定期維護)

### 爬蟲來源與特性

| 指標 | 來源 | 技術 | 特性 |
|------|------|------|------|
| F01-F03 | TAIFEX | BeautifulSoup | 外資未平倉部位 |
| F04 | TAIFEX | BeautifulSoup | 台指期貨當日收盤 |
| F05 | TAIFEX | BeautifulSoup | 台指選擇權成交量 |
| F07 | TAIFEX | BeautifulSoup | P/C 未平倉量比率 |
| F11-F12 | TWSE JSON API | Requests | 大盤加權指數 & 成交金額 |
| F13 | TWSE JSON API | Requests | 20 日均線距離 (依賴 F11) |
| F14-F16 | TWSE JSON API | Requests | TSMC 收盤資訊 |
| F17 | TWSE JSON API | Requests | 外資買賣差額 |
| F21-F25 | Wantgoo | Playwright | 全球市場指數 (NASDAQ/費城半導體/ADR等) |

**TAIFEX (台灣期貨交易所)**: F01-F07
- HTML 抓取 (BeautifulSoup)
- POST 請求需要 form payload，目標頁面: https://www.taifex.com.tw

**TWSE (台灣證券交易所)**: F11-F17
- JSON API 回傳
- 必須正確設置 Referer/Header 以通過反爬蟲檢查
- 共用 Session 以維持 cookies 及連接池
- 隨機延遲 0.5-1.0 秒 (via `_random_sleep()`) 避免頻繁請求
- 民國年轉換邏輯: `year - 1911` (例: 2026 → 115)

**Wantgoo (全球市場數據)**: F21-F25
- JavaScript 動態渲染頁面 (https://www.wantgoo.com/global)
- 使用 **Playwright** (無頭 Chromium 瀏覽器) 執行
- 反偵測設定: 禁用 webdriver 標誌、自訂 User-Agent
- 等待 DOM 加載後再提取文本

### F13 計算邏輯 (20 日均線距離)

計算公式: `F13 = 當日收盤 (F11) - 20日平均收盤價`

- 依賴 F11 (當日收盤) 作為目標價格
- 需要撈取本月 + 上個月的收盤價歷史 (最多 ~40 筆 via TWSE API)
- 向後搜尋，找到匹配當日收盤的位置，往前取 19 筆 + 自己 = 20 筆
- 容許小數點誤差 (<0.01) 以應對浮點數舍入

### Error Handling & Fallback

在 `scrapers/daytime.py:query_daytime_data()` 中的容錯邏輯：
1. 先嘗試抓取當日資料
2. 若缺失指標，遞迴呼叫 `query_daytime_data(前一交易日)` 從前一交易日補齊
3. 若最終仍有缺失指標，標記為 `value="查詢失敗"` 輸出
4. 版本號會遞增 (透過 `get_next_version()`) 以避免覆蓋當日多次執行的結果

**重要**: 不應使用遞迴深度限制，交易日假日邏輯由 `is_trading_day()` 處理。

## GitHub Actions Automation

自動排程兩次執行：

**日盤排程** (`.github/workflows/daytime.yml`)
- **觸發時間**: 每天 13:00 UTC = 台灣 21:00 (交易日後市收盤後)
- **頻率**: 週一至週五 (排除假日)
- **採集**: F01-F20 (TAIFEX + TWSE)
- **輸出**: `output/taifex_YYYY.MM.DD_v{N}.md`

**夜盤排程** (`.github/workflows/nighttime.yml`)
- **觸發時間**: 每天 21:30 UTC = 隔日 05:30 台灣時間 (國際市場開盤後)
- **頻率**: 週日至週四晚上 (採集隔日亞洲開盤數據)
- **採集**: F21-F25 (Wantgoo 全球市場)
- **輸出**: `output/taifex_night_YYYY.MM.DD_v{N}.md`

**Workflow 步驟**:
1. Git 檢出代碼 (fetch-depth: 0 保留完整歷史)
2. 安裝 Python 3.9 + 依賴快取
3. 安裝 Playwright Chromium 瀏覽器
4. 執行爬蟲指令 (daytime_query.py 或 nighttime_query.py)
5. 驗證生成的輸出檔案
6. 自動配置 Git 信息 (action@github.com)
7. 提交到 GitHub (自動 commit 和 push)

## File Structure

```
taifex-query/
├── daytime_query.py              # 日盤執行入口 (呼叫 scrapers/daytime.py)
├── nighttime_query.py            # 夜盤執行入口 (呼叫 scrapers/nighttime.py)
│
├── scrapers/
│   ├── daytime.py                # 日盤爬蟲實現 (F01-F20)
│   │   └── query_daytime_data()  # 主協調函式，呼叫所有子爬蟲
│   └── nighttime.py              # 夜盤爬蟲實現 (F21-F25 via Playwright)
│       └── query_wantgoo_nighttime()  # Playwright 實現
│
├── utils/
│   ├── helpers.py                # save_to_markdown() & get_next_version()
│   └── date_utils.py             # 台灣時區 & 交易日邏輯
│
├── dev/
│   ├── diagnose_daytime.py       # 開發診斷：測試日盤各項指標
│   ├── diagnose_twse.py          # 開發診斷：測試 TWSE API
│   ├── diagnose_remaining.py     # 開發診斷：測試其他指標
│   ├── test_nighttime_wantgoo.py # 開發診斷：測試 Wantgoo 爬蟲
│   └── tests/
│       ├── test_daytime_all.py   # 完整日盤測試
│       └── archive_test_f01_f03.py # 歷史測試檔案
│
├── .github/workflows/
│   ├── daytime.yml               # GitHub Actions：日盤排程 (每日 13:00 UTC)
│   └── nighttime.yml             # GitHub Actions：夜盤排程 (每日 21:30 UTC)
│
├── output/                       # 爬蟲輸出檔案目錄
│   ├── taifex_YYYY.MM.DD_v{N}.md # 日盤輸出
│   └── taifex_night_YYYY.MM.DD_v{N}.md # 夜盤輸出
│
├── requirements.txt              # Python 依賴 (playwright, requests, beautifulsoup4, lxml, python-dateutil, pytz)
├── README.md                     # 項目說明 & 快速開始
├── CLAUDE.md                     # 本文件 (Claude Code 指南)
└── line.py, predict_dashboard.py # 其他工具腳本 (非核心功能)
```

## Adding or Modifying Indicators

### 新增日盤指標 (F01-F20)

1. 在 `scrapers/daytime.py` 新增函式，命名規則: `query_source_name(date_str=None, session=None) → Optional[List[Dict]]`
2. 返回 `List[Dict]` 結構 (參見 Key Data Structure 段)，或 `None` 失敗
3. 在 `query_daytime_data()` 中：
   - 呼叫新函式
   - 將 F-code 加入 `expected_codes` 集合
4. 測試: `python daytime_query.py` 或 `python dev/diagnose_daytime.py`

**注意**: 使用 `session` 參數而非建立新連線，以維持 cookies 及連接池。

### 修改夜盤指標 (F21-F25)

1. 編輯 `scrapers/nighttime.py:query_wantgoo_nighttime()` 的 `INDICATOR_CONFIG` 字典
   - 鍵: 頁面上的關鍵詞 (例: `'NASDAQ'`)
   - 值: `(f_code, display_name)` 元組
2. 若關鍵詞匹配邏輯需要調整，修改 `_parse_indicator_line()` 的正則表達式
3. 測試: `python dev/test_nighttime_wantgoo.py`

### 故障排除

| 問題 | 原因 | 解決方式 |
|------|------|--------|
| 爬蟲無資料 | 目標網站改版或已關閉 | `curl -I` 檢查可連通性；檢查 HTML 結構是否改變 |
| TWSE 返回 `stat != 'OK'` | API 返回錯誤 | 檢查是否超過請求頻率限制；驗證民國年轉換 (`year - 1911`) |
| Wantgoo 無法截取 | 頁面更新、JS 動態內容載入延遲 | `python dev/test_nighttime_wantgoo.py` 除錯；調整等待時間或關鍵詞 |
| F13 計算失敗 | 無法取得歷史收盤數據 | 驗證 F11 值是否正確；檢查浮點誤差邏輯 (<0.01) |
| 無法寫入檔案 | `output/` 目錄不存在或無權限 | `mkdir -p output/`；`touch output/test.txt` 驗證權限 |

### 維護國定假日表

編輯 `utils/date_utils.py:is_trading_day()` 中的 `holidays` 清單：
- 新增當年新假日: `datetime.date(YYYY, M, D)`
- 刪除已過期假日
- 驗證格式：`datetime.date(2026, 2, 28)` (無前置零)

## Dependencies

- `playwright>=1.40.0` - 動態渲染爬蟲 (F21-F25 Wantgoo)
- `requests>=2.31.0` - HTTP 請求 (TAIFEX/TWSE API)
- `beautifulsoup4>=4.12.2` - HTML 解析 (TAIFEX 爬蟲)
- `lxml>=4.9.3` - XML/HTML 高速解析器 (BeautifulSoup 後端)
- `python-dateutil>=2.8.2` - 日期工具
- `pytz>=2024.1` - 時區處理 (台灣 UTC+8)

**注意**: 運行 Playwright 爬蟲前需執行 `playwright install chromium` 以下載瀏覽器二進制檔案。

## Integration Notes

### Session & Connection Management

- `query_twse_market_data()` 自動建立新 session (獨立使用)
- `query_twse_stock_day()` 和 `query_twse_foreign_buy()` 接收 session 參數 (共用)
- `calculate_f13_ma20()` 接收 session 參數 (需多次請求)
- 所有爬蟲函式都支援 `date_str` 參數以便測試特定日期

### Anti-Scraping Measures

- TAIFEX: 需要設置 Referer header，使用 POST 請求
- TWSE: 必須設置 `X-Requested-With: XMLHttpRequest` header，檢查 `stat='OK'`
- Wantgoo: 使用 Playwright 並禁用 webdriver 標誌，隨機等待 4 秒以載入 JS

### Output File Structure

每個爬蟲函式返回 `Optional[List[Dict]]`，字典包含：
- `f_code`: 指標代碼 (F01-F25)
- `name`: 指標名稱
- `field`: 欄位說明
- `value`: 查詢的值 (字串) 或特殊值 `"查詢失敗"` / `"保留項目"`
- `unit`: 單位 (可為空字串)

標記為 `"保留項目"` 的指標 (F08-F10) 不執行查詢，直接輸出。
