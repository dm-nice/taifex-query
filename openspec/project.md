# Project Context
「這是一個多模組專案，各功能模組位於 dev/fXX_package/ 下」
## Project Overview

**專案名稱**: 台指期貨20因子預測系統  
**專案目標**: 基於20個市場因子分析台指期貨隔日漲跌趨勢的多模組資料抓取系統  
**開發方式**: OpenSpec 4-Phase 標準開發框架 (v2.0)

---

## Purpose

基於市場籌碼、散戶情緒、技術面等多個維度，自動從各資料來源（TAIFEX、TWSE、第三方API）抓取20個預測因子的實時數據，輸出統一格式，供後續預測模型使用。

### 核心目標

- 🎯 自動化資料抓取 - 每日自動執行，零人工介入
- 📊 統一資料格式 - 所有模組採用統一文字格式輸出
- 🔄 模組化架構 - 每個因子（F01-F17+）獨立開發、易於維護
- 📈 完整性驗證 - 21個測試確保每個模組品質

---

## Tech Stack

### 核心技術

- **語言**: Python 3.9+
- **套件管理**: Poetry (pyproject.toml)
- **虛擬環境**: venv32

### 資料抓取

- **HTTP 請求**: requests
- **HTML 解析**: BeautifulSoup4, lxml, pandas.read_html
- **動態頁面**: Selenium WebDriver (需要時)
- **JSON 解析**: 原生 json 模組

### 測試與品質

- **測試框架**: pytest
- **代碼格式**: black, isort
- **測試覆蓋**: 21 個單元測試 / 模組（90%+ 覆蓋率目標）

### 外部資料源

- **TAIFEX** (台灣期貨交易所) - F01~F07: 期貨籌碼
- **TWSE** (台灣證券交易所) - F11~F17: 股票指數與外資淨額
- **台灣銀行** - 匯率 (預留)
- **其他**: 滬深股市、美股指數等 (預留)

---

## Project Structure

### 多模組設計

```
C:\Taifex/
├── .openspec/                    # 專案級別 OpenSpec 配置（所有模組共享）
├── openspec/project.md           # 本文件
│
├── modules/                      # ✅ 正式模組（生產環境）
│   ├── f01_fetcher.py           # F01: 台指期外資未平倉淨額
│   ├── f11_fetcher.py           # F11: 加權股價收盤指數 ⭐ (生產中)
│   └── ... f02-f17_fetcher.py    # 其他模組
│
├── dev/                          # 📚 開發包目錄
│   ├── README.md                 # 開發指南
│   ├── QUICK_GUIDES.md           # 快速導航
│   ├── OpenSpec_開發試驗版.md    # 20 分鐘試驗版指南
│   ├── 共同開發規範書_V1.md     # 統一規範 (857 行)
│   │
│   ├── f11_package/              # ⭐ F11 完整範本 (OpenSpec v2.0)
│   │   ├── f11_openspec_dev.py          # 實現代碼 (380 行)
│   │   ├── test_f11_openspec.py         # 完整測試 (21 測試)
│   │   ├── IMPLEMENTATION_REPORT.md     # 實現報告
│   │   └── openspec/
│   │       ├── project.md
│   │       ├── AGENTS.md
│   │       ├── changes/add-f11-taiex-api/
│   │       │   ├── proposal.md
│   │       │   ├── design.md
│   │       │   ├── tasks.md
│   │       │   └── specs/
│   │       └── specs/
│   │
│   ├── f01_package/              # F01 實現參考
│   ├── f02_package/ ~ f07_package/  # 其他模組開發包
│   └── ...
│
├── data/                         # 📊 輸出目錄（自動生成）
│   ├── 2025-12-17_f11_fetcher.txt
│   └── 2025-12-17_run.log
│
├── run.py                        # 主控程式（執行所有模組）
└── README.md                     # 專案入口
```

---

## Project Conventions

### 模組命名與編號

**模組代號規則**: `FXX` (如 F01, F11, F17)

- **F01~F10**: TAIFEX (期貨籌碼相關)
- **F11~F20**: TWSE/股票相關 (F11: 加權指數, F13: 20日均線, F14-F17: 台積電相關)
- **F21+**: 其他資料源 (預留)

### 輸出格式規範 (v4.0/v5.0 統一格式)

**成功格式**:

```
2025.12.17  FXX: 描述 : 數值 [來源]
```

**失敗格式**:

```
2025.12.17  FXX 錯誤: 錯誤訊息 [來源]
```

**範例**:

```
✅ 2025.12.17  F11: 加權股價收盤指數 : 18254.50 [https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html]
✅ 2025.12.17  F07: 臺指選擇權(TXO)買賣權未平倉量比率% : 107.75% [https://www.taifex.com.tw/cht/3/pcRatio]
❌ 2025.12.17  F11 錯誤: 該日無交易資料 [https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html]
```

### 核心規範

| 規範 | 說明 | 例子 |
|------|------|------|
| **回傳類型** | 必須是 `str` | `return "2025.12.17  F11: ... [https://www.twse.com.tw/...]"` |
| **異常處理** | 異常轉為文字，不拋出 | `except Exception: return "F11 錯誤: ..."` |
| **日期格式** | 輸入 YYYY-MM-DD → 輸出 YYYY.MM.DD | `2025-12-17` → `2025.12.17` |
| **千分位逗號** | 數值使用千分位 | `18,254.50` ✅, `18254.50` ❌ |
| **函式簽名** | `def fetch(date: str) -> str:` | 統一介面 |

### Code Style

- **語言**: 中文註解 + 清晰英文變數名
- **格式工具**: black (自動格式化), isort (排序 import)
- **縮排**: 4 spaces
- **行寬**: 100 字元
- **命名規則**:
  - 函式/變數: `snake_case` (fetch_data, close_price)
  - 常數: `UPPER_CASE` (MAX_RETRIES, TIMEOUT)
  - 類別: `PascalCase` (TaiexFetcher)

### 異常處理規範

**必須捕捉的異常類型**:

1. `requests.Timeout` - 連線超時
2. `requests.HTTPError` - HTTP 錯誤 (404, 500)
3. `requests.ConnectionError` - 網路連線失敗
4. `ValueError` / `KeyError` - 資料解析失敗
5. `IndexError` - 欄位缺失

**規範**: 所有異常都轉為統一文字格式，不拋出

```python
def fetch(date: str) -> str:
    try:
        # 代碼...
        return format_success(data)
    except requests.Timeout:
        return "FXX 錯誤: 伺服器無回應 [來源]"
    except requests.HTTPError as e:
        return f"FXX 錯誤: HTTP {e.response.status_code} [來源]"
    except Exception as e:
        return f"FXX 錯誤: {str(e)} [來源]"
```

### Architecture Patterns

**OpenSpec 4-Phase 標準開發**:

```
Phase 1: 文檔化 (1.5 小時)
  ├── project.md (項目概述)
  ├── proposal.md (變更提案)
  ├── design.md (技術設計)
  ├── tasks.md (實現清單)
  └── specs/*.md (功能規格)
  
Phase 2: 代碼實現 (1.5 小時)
  ├── 主要邏輯: fetch_data(), parse_html()
  ├── 格式化: format_output(), format_error()
  ├── 日誌記錄: logging 統一 [FXX] 前綴
  └── 異常處理: 5+ 異常類型
  
Phase 3: 測試 (1 小時)
  ├── 6 個測試類別
  ├── 21 個單元測試 (最小充分)
  ├── 90%+ 代碼覆蓋率
  └── pytest + @patch 模擬
  
Phase 4: 部署 (0.5 小時)
  ├── 複製到 modules/
  ├── 集成到 run.py
  └── 生產驗證 (實時資料)
```

### Testing Strategy

**測試結構** (以 F11 為標準):

```
6 大測試類別:
├── 1️⃣ 格式驗證 (5 個測試)
│   └── 日期格式、小數位、錯誤格式
├── 2️⃣ 資料提取 (4 個測試)
│   └── 逗號處理、欄位變異、優先級
├── 3️⃣ 異常處理 (5 個測試)
│   └── Timeout、HTTP 錯誤、解析失敗、缺失欄、格式異常
├── 4️⃣ 邊界情況 (3 個測試)
│   └── 空表格、零值、超大值
├── 5️⃣ 日誌測試 (2 個測試)
│   └── 成功/失敗日誌驗證
└── 6️⃣ 集成測試 (2 個測試)
    └── 模組匯入、函式簽名
```

**執行命令**:

```bash
pytest test_f11_openspec.py -v        # 詳細輸出
pytest test_f11_openspec.py --cov    # 覆蓋率報告
```

### Git Workflow

**分支策略**:

```
main/                    # 生產分支（modules/ 中的代碼）
├── dev/f11-feature      # 特性分支（新模組開發）
├── dev/f11-bugfix       # 修復分支（bug 修正）
└── dev/f11-docs         # 文檔分支（規範更新）
```

**提交規範**:

```
[FXX] <動詞> <描述>  # 模組代號 + 動詞 + 說明

例子:
[F11] Add fetch_taiex_index() function
[F11] Fix HTML column name parsing bug
[F11] Update project.md with new requirements
[DEV] Update QUICK_GUIDES.md documentation
```

---

## Domain Context

### 市場基礎知識

**TAIFEX (台灣期貨交易所)** - F01~F07 資料源

- 提供台指期貨籌碼資訊（外資、散戶、法人）
- 未平倉數據：多方口數、空方口數、淨額
- API: `futContractsDate` (無視日期參數), `futDailyMarketReport`
- ⚠️ 陷阱: F01-F03 永遠回傳「最近一個交易日」

**TWSE (台灣證券交易所)** - F11~F17 資料源

- 提供加權股價指數、台積電等股票資訊
- API: `MI_INDEX` (加權指數), `STOCK_DAY` (個股日線), `BFI82U` (外資淨額)
- 民國日期轉西元日期: `year = int(row[0]) + 1911`

### 資料特性

| 模組 | 資料源 | 日期支援 | 更新頻率 | 備註 |
|------|--------|--------|--------|------|
| F01-F03 | TAIFEX futContractsDate | ❌ 無視 | 交易日 | 無法回測歷史 |
| F04 | TAIFEX futDailyMarketReport | ✅ 支援 | 隔日 | ⚠️ 欄位空白變異 |
| F06 | TWSE VIX Download | ✅ 支援 | 實時/隔日 | ⚠️ 下載按鈕時間戳記 |
| F11-F17 | TWSE MI_INDEX/STOCK_DAY | ✅ 支援 | 隔日 | ⚠️ 民國日期需轉換 |

---

## Important Constraints

### 技術限制

1. **API 日期限制** (F01-F03)
   - 某些 API 忽視日期參數，永遠回傳最新交易日
   - 規範: 在 design.md 明確標註限制

2. **HTML 欄位不穩定** (F04, F14-F16)
   - 欄位名稱可能包含不規則空白 (如 `最後 成交價`)
   - 解決: 使用模糊匹配、多個關鍵字

3. **日期格式轉換** (TWSE)
   - 民國日期需轉西元: `year = int(row[0]) + 1911`
   - 必須統一輸出為 `YYYY.MM.DD`

4. **性能要求**
   - 每個模組執行時間 < 5 秒
   - 記憶體使用 < 50 MB
   - 無限期卡死: 設置 Timeout = 10 秒

### 業務限制

1. **開市時間** (9:00-13:30)
   - TAIFEX/TWSE 只在交易日開放 API
   - 假日/公休日應回傳 "該日無交易資料"

2. **資料延遲** (隔日公布)
   - 大多資料需隔日才公布
   - F06 例外: 下載檔案可能當日最新

3. **統一格式要求**
   - 所有模組必須遵循 v4.0/v5.0 文字格式
   - 異常不能拋出，必須轉為文字

---

## External Dependencies

### 網頁資料源

| 來源 | 資料 | URL | 備註 |
|------|------|-----|------|
| **TAIFEX** | 期貨籌碼 | taifex.com.tw | HTML 表格 |
| **TWSE** | 加權指數 | twse.com.tw/...MI_INDEX | JSON API |
| **TWSE** | 個股資訊 | twse.com.tw/...STOCK_DAY | HTML 表格 (民國日期) |
| **TWSE** | 外資淨額 | twse.com.tw/...BFI82U | JSON API |

### Python 套件依賴

```toml
requests = "^2.31.0"           # HTTP 請求
pandas = "^2.1.0"              # HTML 表格解析 (read_html)
beautifulsoup4 = "^4.x"        # HTML 解析
lxml = "^4.9.0"                # HTML/XML 解析引擎
selenium = "^4.x" (可選)       # 動態頁面 (F06)
pydantic = "^2.5.0"            # 資料驗證
pytest = "^7.4.0"              # 測試框架
```

### 外部工具

- **OpenSpec CLI** - 規範版本管理與驗證
- **Git** - 版本控制
- **Poetry** - 套件管理與虛擬環境

---

## 開發團隊指引

### 新模組開發流程 (推薦)

```bash
# 1. 在 C:\Taifex 做一次專案級別初始化（只做一次）
cd C:\Taifex
openspec init

# 2. 開發新模組時，複製 F11 範本
cd dev
cp -r f11_package f02_package  # 複製完整結構

# 3. 進入新模組編輯
cd f02_package/openspec
# (編輯 project.md, proposal.md, design.md 等)

# 4. 不需要重複 init，因為已有專案級別配置
openspec validate add-f02-xxxx --strict
```

### 參考資源

- **QUICK_GUIDES.md** - 快速導航（最常見的 5 個問題）
- **共同開發規範書_V1.md** - 統一規範詳解 (857 行)
- **F11 完整範本** - 標準實現 (380 行代碼 + 21 個測試)
- **OpenSpec_開發試驗版.md** - 20 分鐘快速試驗法

---

**版本**: v2.0 (OpenSpec 標準 v2.0)  
**最後更新**: 2025-12-17  
**適用範圍**: 所有 FXX 模組開發
