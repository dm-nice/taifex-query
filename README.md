# TAIFEX 爬蟲系統 - 台灣期貨交易所資料聚合

自動化爬取台灣期貨交易所及台股相關的 **25 個金融指標 (F01-F25)**，每日執行兩次自動排程。

## 🎯 項目目標

```
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

## 📊 核心指標 (F01-F25)

### 一般交易時段 (F01-F20, 21:00)

| F值 | 名稱 | 來源 | 主鍵字 |
|-----|------|------|--------|
| F01-F03 | 台指期貨外資 | 台期所 | 多空淨額/多方/空方 |
| F04 | 台指期貨收盤 | 台期所 | 最後成交價 |
| F05-F07 | 台指選擇權 | 台期所 | 成交量/波動率/P/C比 |
| F11-F12 | 大盤指數 | 台股 | 指數收盤/成交金額 |
| F13 | 均線距離 | wantgoo | 20日均線距離 |
| F14-F16 | 台積電 | 台股 | 收盤/漲跌/成交張 |
| F17 | 外資陸資 | 台股 | 買賣差額 |

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

## 📁 項目結構

```
taifex/
├── daytime_query.py              ← 運行: python daytime_query.py
├── nighttime_query.py            ← 運行: python nighttime_query.py
├── requirements.txt              ← 依賴: pip install -r requirements.txt
│
├── scrapers/                     # 爬蟲邏輯
│   ├── daytime.py               # F01-F20 爬蟲
│   └── nighttime.py             # F21-F25 爬蟲
│
├── utils/                        # 工具函式
│   ├── helpers.py               # save_to_markdown(), get_next_version()
│   ├── date_utils.py            # 日期邏輯
│   └── validators.py            # 資料驗證
│
├── config/                       # 配置
│   ├── settings.py              # 全域設定
│   └── field_mapping.py         # F01-F25 對應表
│
├── output/                       # 輸出檔案
│   └── taifex_*.md
│
├── tests/                        # 單元測試
├── .github/workflows/            # GitHub Actions
│   ├── daytime-schedule.yml
│   └── nighttime-schedule.yml
│
└── docs/                         # 文檔
    ├── TAIFEX_PROJECT_SPECIFICATION.md
    ├── CODE_FRAMEWORK.md
    ├── GITHUB_ACTIONS_WORKFLOWS.md
    ├── DEVELOPMENT_CHECKLIST.md
    └── QUICK_REFERENCE.md
```

---

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 本地測試

```bash
# 測試一般時段爬蟲
python daytime_query.py

# 測試盤後時段爬蟲
python nighttime_query.py

# 查看輸出
cat output/taifex_*.md
```

### 3. GitHub Actions 配置

將 `.github/workflows/` 目錄下的工作流文件提交到 GitHub：

```bash
git add .
git commit -m "feat: initial TAIFEX scraper setup"
git push origin main
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

## 📦 依賴套件

```
requests>=2.31.0           # HTTP 請求
beautifulsoup4>=4.12.0     # HTML 解析
pandas>=2.1.0              # 數據處理
pydantic>=2.5.0            # 型別驗證
pytz>=2023.3               # 時區處理
selenium>=4.14.0           # 動態內容爬蟲 (可選)
pytest>=7.4.0              # 測試框架
```

---

## 📚 文檔指南

快速了解項目的不同方式：

| 文檔 | 說明 | 讀者 | 時間 |
|------|------|------|------|
| [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) | 快速參考 & 速查表 | 所有人 | 5分鐘 |
| [TAIFEX_PROJECT_SPECIFICATION.md](docs/TAIFEX_PROJECT_SPECIFICATION.md) | 完整規劃 | PM、架構師 | 20分鐘 |
| [CODE_FRAMEWORK.md](docs/CODE_FRAMEWORK.md) | 代碼框架 | 開發者 | 15分鐘 |
| [DEVELOPMENT_CHECKLIST.md](docs/DEVELOPMENT_CHECKLIST.md) | 開發進度 | 項目經理 | 10分鐘 |
| [GITHUB_ACTIONS_WORKFLOWS.md](docs/GITHUB_ACTIONS_WORKFLOWS.md) | 工作流配置 | DevOps | 10分鐘 |

---

## 🧪 開發命令

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

## 🐛 常見問題

### Q: 爬蟲找不到資料怎麼辦？
**A**: 自動降級邏輯會查詢前一交易日。若持續失敗，資料標記為 `[ 查詢失敗 ]`

### Q: F21-F25 格式錯誤？
**A**: 務必包含 `+` 或 `-` 符號，不需要 `%` 號
- ✅ `+301.26`, `-45.89`
- ❌ `301.26%`, `45.89`

### Q: 同日多次執行會覆蓋檔案？
**A**: 不會。版本號自動遞增 (`_v1`, `_v2`, `_v3`)

### Q: 如何手動執行排程？
**A**: GitHub → Actions → 選工作流 → Run workflow

### Q: 如何檢查執行日誌？
**A**: GitHub → Actions → 選執行 → 查看詳細輸出

---

## 🔗 外部資源

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

## 📋 部署檢查清單

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

## 📞 需要幫助？

1. **快速了解**: 查看 `docs/QUICK_REFERENCE.md` (5分鐘)
2. **詳細規劃**: 查看 `docs/TAIFEX_PROJECT_SPECIFICATION.md` (20分鐘)
3. **代碼框架**: 查看 `docs/CODE_FRAMEWORK.md` (15分鐘)
4. **開發進度**: 查看 `docs/DEVELOPMENT_CHECKLIST.md` (10分鐘)

---

**最後更新**: 2026-01-16
**版本**: 1.0.0
**狀態**: 架構規劃完成，待開發實現
