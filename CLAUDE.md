# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TAIFEX 爬蟲系統 - 自動化爬取台灣期貨交易所及台股相關金融指標。

**核心功能**:
- 自動抓取 25 個金融指標 (F01-F25)
- 每日執行兩次排程：日盤 (F01-F20) + 夜盤 (F21-F25)
- 資料不完整時自動降級查詢前一交易日
- 同日多次執行時版本號自動遞增 (v1, v2, ...)

## Commands

### Running the Scrapers

```bash
# 日盤爬蟲 (F01-F20, 21:00 Taiwan Time)
python daytime_query.py

# 夜盤爬蟲 (F21-F25, 隔日 05:10 Taiwan Time)
python nighttime_query.py
```

### Development & Testing

```bash
# 執行開發診斷工具 (探索/測試單個指標)
python dev/diagnose_daytime.py
python dev/diagnose_nighttime.py
python dev/diagnose_twse.py

# 執行單元測試
pytest dev/tests/
```

### Code Quality

```bash
# 代碼格式化
black .
isort .
```

### Installation

```bash
# 依賴安裝
pip install -r requirements.txt
```

## Architecture

### Core Components

**Entry Points** (`daytime_query.py`, `nighttime_query.py`):
- 調用對應的爬蟲函式，執行資料抓取
- 結果傳遞給 `save_to_markdown()` 存檔
- 輸出檔案格式: `taifex_YYYY.MM.DD_v{version}.md`

**Scrapers** (`scrapers/`):
- `daytime.py`:
  - `query_daytime_data()` - 主入口，協調 F01-F20 的抓取
  - 子函式: `query_taifex_*(...)` 抓取期貨所 (F01-F07)
  - 子函式: `query_twse_*(..., session)` 抓取台股資料 (F11-F17)
  - 降級邏輯: 當日資料缺失時自動補齊前一交易日資料

- `nighttime.py`:
  - `query_nighttime_data()` - 主入口，協調 F21-F25 的抓取
  - 目前僅實作 `query_taifex_night_tx()` (F21-F22)
  - F23-F25 待實作

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

### Data Flow

```
daytime_query.py / nighttime_query.py
    ↓
scrapers/daytime.py (query_daytime_data)
    ├─ query_taifex_foreign_holdings() → F01, F02, F03
    ├─ query_taifex_settlement() → F04
    ├─ query_taifex_options_volume() → F05
    ├─ query_taifex_pc_ratio() → F07
    ├─ query_twse_market_data() → F11, F12
    ├─ query_twse_stock_day(session) → F14, F15, F16
    ├─ query_twse_foreign_buy(session) → F17
    └─ calculate_f13_ma20(session) → F13 (依賴 F11)
    ↓
降級邏輯: expected_codes - actual_codes 不為空
    ├─ 遞迴呼叫 fetch_all(前一交易日)
    └─ 補齊缺失的指標
    ↓
utils/helpers.py (save_to_markdown)
    ↓
output/taifex_YYYY.MM.DD_v{version}.md
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
- `get_current_taiwan_date()` 自動計算台灣時刻
- TWSE API 使用民國年格式 (例: 115/01/15)，轉換邏輯: `year - 1911`

### TWSE vs TAIFEX

- **台灣期貨交易所 (TAIFEX)**: F01-F07 (期貨及選擇權)
- **台灣證券交易所 (TWSE)**: F11-F17 (大盤及個股)
  - API 通常回傳 JSON
  - 需要正確的 Referer/Header 以通過反爬蟲檢查
  - Session 維持及隨機延遲 (0.5-1.0秒) 有助於穩定性

### F13 計算邏輯

20日均線距離 = 當日收盤 - 20日平均價

- 依賴 F11 (當日收盤) 作為目標價格
- 需要撈取本月 + 上個月的收盤價歷史 (最多 ~40 筆)
- 向後搜尋，找到匹配當日收盤的位置，往前取 19 筆 + 自己 = 20 筆
- 容許小數點誤差 (<0.01)

### Error Handling & Fallback

在 `query_daytime_data()` 中：
1. 先嘗試抓取當日資料
2. 若 `expected_codes - actual_codes` 不為空，自動補齊前一交易日
3. 版本號會遞增以避免覆蓋

## File Structure

```
taifex/
├── daytime_query.py              # 日盤主程式
├── nighttime_query.py            # 夜盤主程式
│
├── scrapers/
│   ├── daytime.py                # 日盤爬蟲 (F01-F20)
│   └── nighttime.py              # 夜盤爬蟲 (F21-F25)
│
├── utils/
│   ├── helpers.py                # Markdown 存檔 & 版本遞增
│   └── date_utils.py             # 台灣時區 & 交易日邏輯
│
├── dev/
│   ├── diagnose_*.py             # 開發診斷工具
│   └── tests/                    # 單元測試
│
├── docs/
│   ├── CODE_FRAMEWORK.md         # 代碼框架詳解
│   ├── TAIFEX_PROJECT_SPECIFICATION.md
│   ├── GITHUB_ACTIONS_WORKFLOWS.md
│   └── CONFIG_FIELD_MAPPING.json # F01-F25 對應表
│
├── output/                       # 爬蟲輸出檔案
├── requirements.txt
└── README.md                     # 項目概述
```

## Common Development Tasks

### Adding a New Indicator (New F-Code)

1. 在 `scrapers/daytime.py` (或 `nighttime.py`) 新增查詢函式
2. 遵循命名規則: `query_source_name(..., date_str=None)` 回傳 `None | List[Dict]`
3. 在主函式 `query_daytime_data()` 中呼叫並擴充 `expected_codes`
4. 測試: `python daytime_query.py` 或 `python dev/diagnose_daytime.py`

### Debugging Web Scraping Issues

使用 `dev/diagnose_*.py` 工具：
- 單獨測試每個爬蟲函式
- 檢視原始 HTML/JSON 響應
- 驗證 CSS 選擇器或 JSON 路徑

### Updating Holidays

在 `utils/date_utils.py` 的 `is_trading_day()` 中編輯 `holidays` 列表。

## Dependencies

- `requests` - HTTP 請求
- `beautifulsoup4` - HTML 解析
- `pandas` - 數據處理 (保留，可能未全部使用)
- `pydantic` - 型別驗證 (保留，可能未全部使用)
- `pytz` - 時區處理
- `pytest` - 測試框架

## Notes for Future Development

- F21-F25 在 `nighttime.py` 中僅實作了 F21-F22，F23-F25 (NASDAQ 相關指標) 待實作
- GitHub Actions workflow 檔案 (`.github/workflows/`) 尚未建立，計畫中
- 考慮加入快取機制避免頻繁重複請求
- 國定假日表需定期維護
