# TAIFEX 項目快速參考

**快速查詢指南** - 所有關鍵信息一覽

---

## 🎯 項目概述 (30秒速讀)

```
目標: 每日自動爬取台灣期貨交易所 25 個金融指標 (F01-F25)

執行時間:
  📍 21:00 - 查詢 F01-F20 (一般交易時段)
  📍 隔日 05:10 - 查詢 F21-F25 (盤後時段)

輸出格式:
  📄 output/taifex_YYYY.MM.DD_v{version}.md

特殊功能:
  ✅ 無資料自動查前一交易日
  ✅ 同日多次查詢序號遞增
  ✅ GitHub Actions 自動排程
```

---

## 📊 F01-F25 指標速查表

### 一般交易時段 (F01-F20, 21:00)

| F值 | 名稱 | 來源 | 主鍵字 |
|-----|------|------|--------|
| F01-F03 | 台指期貨外資 | 台期所 | 多空淨額/多方/空方 |
| F04 | 台指期貨收盤 | 台期所 | 最後成交價 |
| F05-F07 | 台指選擇權 | 台期所 | 成交量/波動率/P/C比 |
| F08-F10 | **[保留]** | - | - |
| F11-F12 | 大盤指數 | 台股 | 指數收盤/成交金額 |
| F13 | 均線距離 | wantgoo | 20日均線距離 |
| F14-F16 | 台積電 | 台股 | 收盤/漲跌/成交張 |
| F17 | 外資陸資 | 台股 | 買賣差額 |
| F18-F20 | **[保留]** | - | - |

### 盤後交易時段 (F21-F25, 隔日 05:10)

| F值 | 名稱 | 來源 | 格式 |
|-----|------|------|------|
| F21 | NASDAQ | wantgoo | +/-數值 |
| F22 | 費城半導體 | wantgoo | +/-數值 |
| F23 | EM-ND期指 | wantgoo | +/-數值 |
| F24 | 台積電ADR | wantgoo | +/-數值 |
| F25 | 台指期盤後 | wantgoo | +/-數值 |

⚠️ **F21-F25 特別注意**: 必須包含符號 (+/-), 不需要百分比符號

---

## 📁 目錄結構一覽

```
taifex_scraper/
├── 📄 daytime_query.py         ← 運行: python daytime_query.py
├── 📄 nighttime_query.py       ← 運行: python nighttime_query.py
├── 📄 requirements.txt          ← 安裝: pip install -r requirements.txt
│
├── 📂 scrapers/                # 爬蟲邏輯
│   ├── daytime.py              # F01-F20 爬蟲
│   └── nighttime.py            # F21-F25 爬蟲
│
├── 📂 utils/                   # 工具函式
│   ├── helpers.py              # save_to_markdown(), get_next_version()
│   ├── date_utils.py           # 日期邏輯
│   └── validators.py           # 資料驗證
│
├── 📂 config/                  # 配置
│   ├── settings.py             # 全域設定
│   └── field_mapping.py        # F01-F25 對應表
│
├── 📂 output/                  # 輸出檔案
│   └── taifex_*.md
│
├── 📂 tests/                   # 單元測試
├── 📂 docs/                    # 文檔
├── 📂 .github/workflows/       # GitHub Actions
│   ├── daytime-schedule.yml
│   └── nighttime-schedule.yml
└── 📂 dev/                     # 開發測試 (臨時)
```

---

## 🔧 核心功能快速查詢

### Entry Points

#### daytime_query.py (21:00)
```bash
python daytime_query.py

# 執行:
# 1. 查詢 F01-F20 資料
# 2. 無資料自動查前一交易日
# 3. 決定版本號 (v1, v2, ...)
# 4. 保存到 output/taifex_YYYY.MM.DD_v{N}.md
```

#### nighttime_query.py (05:10)
```bash
python nighttime_query.py

# 執行:
# 1. 查詢 F21-F25 資料
# 2. 驗證符號格式 (+/-)
# 3. 決定版本號 (v1, v2, ...)
# 4. 保存到 output/taifex_YYYY.MM.DD_v{N}.md
```

### 核心函式

#### scrapers/daytime.py
```python
query_daytime_data(date=None, auto_fallback=True) → List[DaytimeData]
```

#### scrapers/nighttime.py
```python
query_nighttime_data(date=None, auto_fallback=True) → List[NighttimeData]
```

#### utils/helpers.py
```python
save_to_markdown(data, date, version, market_type) → str  # 返回檔案路徑
get_next_version(market_type='daytime', date=None) → int  # 返回版本號
```

#### utils/date_utils.py
```python
get_current_taiwan_date(format='%Y.%m.%d') → str
is_trading_day(date=None) → bool
get_previous_trading_day(date=None) → str
```

---

## 📝 輸出格式示例

### 一般交易時段 (daytime)
```markdown
2026.01.15 F01 台指期貨-外資 [ 未平倉 多空淨額: -181389口 ]
2026.01.15 F02 台指期貨-外資 [ 未平倉 多方: 185467口 ]
2026.01.15 F03 台指期貨-外資 [ 未平倉 空方: 366856口 ]
2026.01.15 F04 台指期貨-當日收盤 [ 最後成交價: 23,307.62 ]
2026.01.15 F08 [保留項目]
2026.01.15 F13 加權股價 20日均線 [ 查詢失敗 ]
```

### 盤後交易時段 (nighttime)
```markdown
2026.01.16 F21 NASDAQ指數 [ 漲跌幅: +301.26 ]
2026.01.16 F22 費城半導體指數 [ 漲跌幅: -45.89 ]
2026.01.16 F25 台指期盤後 [ 漲跌幅: +1.50 ]
```

---

## 🕐 GitHub Actions Cron 表達式

### daytime-schedule.yml
```
0 13 * * 1-5
→ 每週一至週五 13:00 UTC (= 台灣 21:00)
```

### nighttime-schedule.yml
```
10 21 * * 1-5
→ 每週一至週五 21:10 UTC (= 台灣隔日 05:10)
```

**重要**: GitHub Actions 使用 UTC 時間，台灣 UTC+8

---

## 🐛 常見問題速解

### Q: 爬蟲找不到資料怎麼辦？
**A**: 自動降級邏輯會查詢前一交易日。若持續失敗，資料標記為 `[ 查詢失敗 ]`

### Q: F21-F25 格式錯誤？
**A**: 務必包含 `+` 或 `-` 符號，不需要 `%` 號
- ✅ `+301.26`, `-45.89`
- ❌ `301.26%`, `45.89`

### Q: 同日多次執行會覆蓋檔案？
**A**: 不會。版本號自動遞增 (`_v1`, `_v2`, `_v3`)

### Q: 保留項目 (F08-F10, F18-F20) 怎麼處理？
**A**: 顯示為 `[ 保留項目 ]`，無實際資料

### Q: 如何手動執行排程？
**A**: GitHub → Actions → 選工作流 → Run workflow

### Q: 如何檢查執行日誌？
**A**: GitHub → Actions → 選執行 → 查看詳細輸出

---

## 🔐 配置速查

### config/settings.py
```python
OUTPUT_DIR = "output"              # 輸出目錄
FILENAME_FORMAT = "taifex_{date}_v{version}.md"
TIMEZONE = "Asia/Taipei"           # 台灣時區
MAX_RETRIES = 3                    # 重試次數
TIMEOUT = 10                       # 超時秒數
```

### config/field_mapping.py
```python
FIELD_MAPPING = {
    'F01': {
        'url': '...',
        'name': '台指期貨-外資',
        'field': '未平倉 多空淨額',
        'unit': '口'
    },
    # ... 其他 F01-F25
}
```

---

## 📦 依賴套件清單

```bash
pip install -r requirements.txt

# 核心依賴:
requests>=2.31.0           # HTTP 請求
beautifulsoup4>=4.12.0     # HTML 解析
pandas>=2.1.0              # 數據處理
pydantic>=2.5.0            # 型別驗證
pytz>=2023.3               # 時區處理

# 可選:
selenium>=4.14.0           # 動態內容爬蟲

# 開發工具:
pytest>=7.4.0              # 測試框架
black>=23.9.0              # 代碼格式化
isort>=5.12.0              # Import 排序
```

---

## 🧪 開發命令速查

```bash
# 安裝依賴
pip install -r requirements.txt

# 執行爬蟲
python daytime_query.py       # F01-F20
python nighttime_query.py     # F21-F25

# 執行測試
pytest tests/

# 代碼格式化
black .
isort .

# Git 操作
git add .
git commit -m "feat: 描述"
git push origin main
```

---

## 🚀 部署檢查清單 (5分鐘版)

部署前確認:

- [ ] `daytime_query.py` 可正常運行
- [ ] `nighttime_query.py` 可正常運行
- [ ] `output/` 目錄已創建
- [ ] `requirements.txt` 完整
- [ ] `.github/workflows/` 目錄存在
- [ ] 兩個 workflow 檔案已創建
- [ ] Git 配置正確
- [ ] GitHub Actions 已啟用

---

## 📊 數據驗證規則

### F01-F20 (一般交易時段)
```
格式: 日期 F碼 名稱 [ 欄位: 數值單位 ]
例: 2026.01.15 F01 台指期貨-外資 [ 未平倉 多空淨額: -181389口 ]

特殊:
- 保留項目: [ 保留項目 ]
- 查詢失敗: [ 查詢失敗 ]
```

### F21-F25 (盤後時段)
```
格式: 日期 F碼 名稱 [ 欄位: ±數值 ]
例: 2026.01.16 F21 NASDAQ指數 [ 漲跌幅: +301.26 ]

規則:
✅ 必須有 +/- 符號
✅ 數值後無 % 號
❌ 不能只有數值
❌ 不能有 % 號
```

---

## 🔗 外部資源連結

### 數據來源

- **台灣期貨交易所**: https://www.taifex.com.tw
- **台灣證券交易所**: https://www.twse.com.tw
- **Wantgoo**: https://www.wantgoo.com

### 開發參考

- **Requests**: https://requests.readthedocs.io
- **BeautifulSoup**: https://www.crummy.com/software/BeautifulSoup
- **Pydantic**: https://docs.pydantic.dev
- **GitHub Actions**: https://docs.github.com/actions

---

## 📞 快速聯絡

**需要幫助？**

1. 查看完整文檔: `TAIFEX_PROJECT_SPECIFICATION.md`
2. 查看代碼框架: `CODE_FRAMEWORK.md`
3. 查看工作流配置: `GITHUB_ACTIONS_WORKFLOWS.md`
4. 查看開發進度: `DEVELOPMENT_CHECKLIST.md`

---

## ⚡ 快速啟動 (新手指南)

### Step 1: 項目初始化
```bash
cd /your/project/path
bash init-python.sh
```

### Step 2: 安裝依賴
```bash
pip install -r requirements.txt
```

### Step 3: 本地測試
```bash
# 測試一般時段爬蟲
python daytime_query.py

# 測試盤後時段爬蟲
python nighttime_query.py

# 查看輸出
cat output/taifex_*.md
```

### Step 4: 部署到 GitHub
```bash
git add .
git commit -m "feat: initial TAIFEX scraper setup"
git push origin main
```

### Step 5: 驗證 GitHub Actions
```
GitHub → Actions → 檢查兩個工作流是否正常
```

完成！🎉

---

**最後更新**: 2026-01-16
**版本**: 1.0

