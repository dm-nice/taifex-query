# TAIFEX 爬蟲系統 - 完整規劃文檔

**項目名稱**: 台灣期貨交易所資料聚合系統
**創建日期**: 2026-01-16
**狀態**: 架構規劃完成，待開發實現

---

## 1. 項目概述

### 1.1 目標
自動化日收集台灣期貨交易所 (TAIFEX) 及台股相關的 **25 個金融指標 (F01-F25)**，每日執行兩次，分別在：
- **21:00** - 查詢一般交易時段資料 (F01-F20)
- **隔日 05:10** - 查詢盤後交易時段資料 (F21-F25)

### 1.2 核心特性
- ✅ 自動降級：當日無資料自動查詢前一交易日
- ✅ 版本管理：同日多次查詢使用序號版本 (`_v1`, `_v2`)
- ✅ 時間分段：分開執行兩個程式，分別輸出到不同檔案
- ✅ GitHub Actions：Cron 排程自動執行
- ✅ 配置化：F01-F25 統一配置，易於擴展

---

## 2. 數據規格 (F01-F25)

### 2.1 一般交易時段 (F01-F20, 21:00 執行)

| F值 | 資料名稱 | 資料來源 | 抓取欄位 | 單位 | 狀態 |
|-----|---------|---------|---------|------|------|
| F01 | 台指期貨-外資 | https://www.taifex.com.tw/cht/3/totalTableDate | 未平倉 多空淨額 | 口 | ✅ |
| F02 | 台指期貨-外資 | https://www.taifex.com.tw/cht/3/totalTableDate | 未平倉 多方 | 口 | ✅ |
| F03 | 台指期貨-外資 | https://www.taifex.com.tw/cht/3/totalTableDate | 未平倉 空方 | 口 | ✅ |
| F04 | 台指期貨-當日收盤 | https://www.taifex.com.tw/cht/3/futDailyMarketReport | 最後成交價 | - | ✅ |
| F05 | 台指選擇權-當日 | https://www.taifex.com.tw/cht/3/optDailyMarketReport | 選擇權總成交量 | - | ✅ |
| F06 | 臺指選擇權波動率 | https://mis.taifex.com.tw/futures/VolatilityQuotes | 波動率指數 | - | ✅ |
| F07 | 臺指選擇權Put/Call | https://www.taifex.com.tw/cht/3/pcRatio | 買賣權未平倉量比率% | - | ✅ |
| F08 | [保留項目] | - | - | - | ⏸️ Reserved |
| F09 | [保留項目] | - | - | - | ⏸️ Reserved |
| F10 | [保留項目] | - | - | - | ⏸️ Reserved |
| F11 | 加權股價指數 | https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html | 指數收盤 | - | ✅ |
| F12 | 大盤統計資訊 | https://www.twse.com.tw/zh/trading/historical/mi-index.html | 總計成交金額 | - | ✅ |
| F13 | 加權股價 20日均線 | https://www.wantgoo.com/index/0000 | 均線距離 | - | ✅ |
| F14 | 2330台積電-當日 | https://www.twse.com.tw/zh/trading/historical/stock-day.html | 收盤價 | - | ✅ |
| F15 | 2330台積電-當日 | https://www.twse.com.tw/zh/trading/historical/stock-day.html | 漲跌價差 | - | ✅ |
| F16 | 2330台積電-當日 | https://www.twse.com.tw/zh/trading/historical/stock-day.html | 成交張數 | - | ✅ |
| F17 | 台灣股票外資及陸資 | https://www.twse.com.tw/fund/BFI82U | 買賣差額 | - | ✅ |
| F18 | [保留項目] | - | - | - | ⏸️ Reserved |
| F19 | [保留項目] | - | - | - | ⏸️ Reserved |
| F20 | [保留項目] | - | - | - | ⏸️ Reserved |

### 2.2 盤後交易時段 (F21-F25, 隔日 05:10 執行)

| F值 | 資料名稱 | 資料來源 | 抓取欄位 | 備註 |
|-----|---------|---------|---------|------|
| F21 | NASDAQ指數 | https://www.wantgoo.com/global | 漲跌幅 | 含符號 (+/-) |
| F22 | 費城半導體指數 | https://www.wantgoo.com/global | 漲跌幅 | 含符號 (+/-) |
| F23 | EM-ND期指數 | https://www.wantgoo.com/global | 漲跌幅 | 含符號 (+/-) |
| F24 | 台積電ADR | https://www.wantgoo.com/global | 漲跌幅 | 含符號 (+/-) |
| F25 | 台指期盤後 | https://www.wantgoo.com/global | 漲跌幅 | 含符號 (+/-) |

**特殊說明**:
- F21-F25 需包含符號 (例：`+301.26`, `-301.26`)
- F21-F25 **不需要百分比符號** (只要數值+符號)
- 保留項目 (F08-F10, F18-F20) 顯示為 `[ 保留項目 ]`

---

## 3. 輸出格式

### 3.1 檔案命名
```
taifex_YYYY.MM.DD_v{version}.md
```

**範例**:
- `taifex_2026.01.15_v1.md` - 一般時段首次查詢
- `taifex_2026.01.15_v2.md` - 一般時段第二次查詢
- `taifex_2026.01.16_v1.md` - 盤後時段首次查詢

### 3.2 數據格式 (每行一條)
```markdown
2026.01.15 F01 台指期貨-外資 [ 未平倉 多空淨額: -181389口 ]
2026.01.15 F02 台指期貨-外資 [ 未平倉 多方: 185467口 ]
2026.01.15 F03 台指期貨-外資 [ 未平倉 空方: 366856口 ]
2026.01.15 F04 台指期貨-當日收盤 [ 最後成交價: 23,307.62 ]
2026.01.15 F05 台指選擇權-當日 [ 選擇權總成交量: 987654 ]
...
2026.01.15 F08 [保留項目]
...
2026.01.16 F21 NASDAQ指數 [ 漲跌幅: +301.26 ]
2026.01.16 F22 費城半導體指數 [ 漲跌幅: -45.89 ]
```

### 3.3 數據可用性標記
當無法取得資料時：
```markdown
2026.01.15 F13 加權股價 20日均線 [ 查詢失敗 ]
```

---

## 4. 程式架構

### 4.1 項目目錄結構
```
taifex_scraper/
├── daytime_query.py              # 一般交易時段入口 (21:00 執行)
├── nighttime_query.py            # 盤後交易時段入口 (隔日 05:10 執行)
├── requirements.txt              # 相依套件
├── pyproject.toml                # Poetry 配置
├── CLAUDE.md                      # Claude 開發指引
├── README.md                      # 專案說明
├── .gitignore                     # Git 忽略設定
├── .clauderules                   # 開發規範
│
├── scrapers/                      # 爬蟲模組
│   ├── __init__.py
│   ├── daytime.py                # F01-F20 爬蟲邏輯
│   └── nighttime.py              # F21-F25 爬蟲邏輯
│
├── utils/                         # 工具函式
│   ├── __init__.py
│   ├── helpers.py                # save_to_markdown(), get_next_version()
│   ├── validators.py             # 資料驗證
│   └── date_utils.py             # 交易日邏輯
│
├── config/                        # 配置文件
│   ├── __init__.py
│   ├── settings.py               # 全域設定
│   └── field_mapping.py          # F01-F25 對應表
│
├── tests/                         # 單元測試
│   └── test_scrapers.py
│
├── output/                        # 輸出資料目錄
│   └── taifex_*.md
│
├── docs/                          # 文件
│   ├── API_GUIDE.md
│   └── architecture.md
│
├── dev/                           # 開發測試 (臨時)
│
└── .github/workflows/             # GitHub Actions
    ├── daytime-schedule.yml       # F01-F20 定時排程
    └── nighttime-schedule.yml     # F21-F25 定時排程
```

### 4.2 Entry Point 邏輯

#### daytime_query.py (21:00 執行)
```python
from scrapers.daytime import query_daytime_data
from utils.helpers import save_to_markdown, get_next_version

def main():
    print("🕘 一般交易時段資料查詢 (21:00)")
    data = query_daytime_data()  # 查詢 F01-F20
    if data:
        version = get_next_version()
        save_to_markdown(data, version=version, market_type='daytime')
        print(f"✅ 資料已保存")
    else:
        print("❌ 無法獲取資料")
```

#### nighttime_query.py (隔日 05:10 執行)
```python
from scrapers.nighttime import query_nighttime_data
from utils.helpers import save_to_markdown, get_next_version

def main():
    print("🌙 盤後交易時段資料查詢 (05:10)")
    data = query_nighttime_data()  # 查詢 F21-F25
    if data:
        version = get_next_version()
        save_to_markdown(data, version=version, market_type='nighttime')
        print(f"✅ 資料已保存")
    else:
        print("❌ 無法獲取資料")
```

### 4.3 核心模組職責

#### scrapers/daytime.py
- 查詢 F01-F03 (台指期貨外資，台期所)
- 查詢 F04 (台指期貨收盤，台期所)
- 查詢 F05-F07 (選擇權相關，台期所)
- 查詢 F11-F17 (股票資訊，台股+wantgoo)
- 自動降級邏輯：當日無資料 → 前一交易日

#### scrapers/nighttime.py
- 查詢 F21-F25 (美股及期盤後，wantgoo)
- 自動降級邏輯：隔日無資料 → 前一交易日

#### utils/helpers.py
- `save_to_markdown()` - 儲存資料到 .md 檔案
  - 支援覆蓋模式
  - 自動版本序號遞增
- `get_next_version()` - 取得下次版本號
  - 檢查當日現有檔案
  - 返回 v1, v2, v3...

#### utils/date_utils.py
- `is_trading_day()` - 判斷是否交易日
- `get_previous_trading_day()` - 取前一交易日
- `get_current_taiwan_date()` - 取台灣當前日期

#### config/settings.py
```python
OUTPUT_DIR = "output"
FILENAME_FORMAT = "taifex_{date}_v{version}.md"
TIMEZONE = "Asia/Taipei"
MAX_RETRIES = 3
TIMEOUT = 10
```

#### config/field_mapping.py
完整的 F01-F25 對應表，包含：
- URL 位址
- 資料名稱
- 抓取欄位
- 單位 (如適用)

---

## 5. 執行排程 (GitHub Actions)

### 5.1 daytime-schedule.yml (F01-F20)
```yaml
name: TAIFEX Daytime Query (F01-F20)

on:
  schedule:
    - cron: '0 21 * * 1-5'  # 週一至週五 21:00 (UTC+8)

jobs:
  query:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run daytime query
        run: python daytime_query.py
      - name: Commit and push
        run: |
          git add output/
          git commit -m "feat: TAIFEX daytime data $(date +%Y.%m.%d)"
          git push
```

### 5.2 nighttime-schedule.yml (F21-F25)
```yaml
name: TAIFEX Nighttime Query (F21-F25)

on:
  schedule:
    - cron: '10 5 * * 2-6'  # 週二至週六 05:10 (UTC+8)

jobs:
  query:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run nighttime query
        run: python nighttime_query.py
      - name: Commit and push
        run: |
          git add output/
          git commit -m "feat: TAIFEX nighttime data $(date +%Y.%m.%d)"
          git push
```

---

## 6. 開發流程

### 6.1 優先級順序
1. **Phase 1** - 基礎爬蟲 (F01-F07, F21-F25)
2. **Phase 2** - 股票資訊 (F11-F17)
3. **Phase 3** - 錯誤處理與降級邏輯
4. **Phase 4** - GitHub Actions 整合
5. **Phase 5** - 測試與驗證

### 6.2 開發規範 (.clauderules)
```
- 優先使用 Type Hints 和 Pydantic 進行型別檢查
- 每次完成功能後，**必須主動更新** CLAUDE.md
- 修改代碼後執行 `black .` 和 `isort .`
- 始終參考 docs/ 目錄以維持架構一致性
```

### 6.3 關鍵依賴
```
requests>=2.31.0          # HTTP 請求
pandas>=2.1.0             # 數據處理
lxml>=4.9.0               # XML 解析
beautifulsoup4>=4.12.0    # HTML 解析
pydantic>=2.5.0           # 型別驗證
selenium>=4.14.0          # 動態內容 (如需)
pytz>=2023.3              # 時區處理
schedule>=1.2.0           # 排程管理
pytest>=7.4.0             # 測試框架
black>=23.9.0             # 代碼格式化
isort>=5.12.0             # Import 排序
```

---

## 7. 特殊考量

### 7.1 交易日邏輯
- 自動偵測台灣股市及期貨市場休市日期
- 若當日無資料，自動查詢前一交易日
- 記錄查詢日期 (非執行日期)

### 7.2 時區處理
- 統一使用 `Asia/Taipei` 時區
- F21-F25 使用隔日日期 (美股收盤後才有資料)
- GitHub Actions UTC 時間需轉換

### 7.3 數據驗證
- F21-F25 必須包含 `+` 或 `-` 符號
- 數值類資料需驗證格式
- 缺失資料標記為 `[ 查詢失敗 ]`

### 7.4 版本管理
- 同日多次執行自動遞增版本號
- 版本號格式：`_v1`, `_v2`, `_v3`...
- 檔案內容追加 (append) 到同一檔案

---

## 8. 當前進度

- [x] PRD (Product Requirements Document) 規劃完成
- [x] 初始化腳本 (init-python.sh) 修改完成
- [x] 目錄結構設計
- [x] Entry Point 框架
- [x] 配置文件架構
- [ ] 爬蟲邏輯實現 (待開發)
- [ ] GitHub Actions 配置 (待開發)
- [ ] 單元測試 (待開發)
- [ ] 本地驗證 (待開發)
- [ ] 線上部署 (待開發)

---

## 9. 聯絡資訊

**項目所有者**: [用戶]
**最後更新**: 2026-01-16
**備份版本**: 1.0

