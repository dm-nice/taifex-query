# 台指期貨20因子預測系統

基於20個市場因子分析台指期貨隔日漲跌趨勢的預測系統。

## ✨ 特色

- 🎯 **模組化設計** - 每個因子獨立模組，易於維護和擴充
- 📊 **20因子分析** - 涵蓋機構籌碼、散戶情緒、市場結構等面向
- 🔄 **統一文字格式** - 所有模組採用統一文字格式輸出（v4.0）
- 🐍 **初學者友善** - 清晰的程式碼和豐富的中文註解

## 📦 快速開始

### 1. 環境需求

- Python 3.9+
- 必要套件：`requests`, `pandas`, `beautifulsoup4`, `lxml`

### 2. 安裝依賴

```bash
# 啟用虛擬環境（如果有）
# Windows
venv32\Scripts\activate

# 安裝必要套件
pip install requests pandas beautifulsoup4 lxml
```

### 3. 執行資料抓取

```bash
# 抓取今天的資料
python run.py

# 抓取指定日期的資料
python run.py 2025-12-03

# 驗收模式（開發測試用）
python run.py 2025-12-03 dev

# 只執行特定模組
python run.py 2025-12-03 --module f01_fetcher
```

### 4. 輸出結果

執行後會在 `data/` 目錄產生結果檔案：

```
data/
├── 2025-12-05_f01_fetcher.txt    # F01 資料輸出
├── 2025-12-05_f02_fetcher.txt    # F02 資料輸出
└── 2025-12-05_run.log            # 執行日誌
```

**輸出格式範例**：

成功時：
```
[ 2025.12.03  F01台指期外資淨額 -29,439 口（多方 19,214，空方 48,653）   source: TAIFEX ]
```

錯誤時：
```
[ 2025.11.30  F01 錯誤: 該日無交易資料（可能是假日或休市日）   source: TAIFEX ]
```

## 📂 專案結構

```
C:\Taifex\
├── run.py                      # 主程式 - 執行所有模組
├── README.md                   # 本文件（專案入口）
├── CLAUDE_CONFIG.md            # Claude Code 配置說明
├── CLAUDE_RESPONSE_GUIDE.md    # Claude AI 回應規範文件
├── Claude跨討論組_log.md       # 跨討論組記錄
│
├── .claude/                    # Claude Code 配置目錄
│   └── settings.json           # 專案設定
│
├── modules/                    # 正式模組目錄
│   └── f01_fetcher.py         # F01: 台指期外資未平倉
│
├── dev/                        # 開發文件與驗收模組
│   ├── README.md               # 開發目錄說明
│   ├── 共同開發規範書_V1.md   # 開發規範（含快速參考）⭐
│   ├── _template_spec.md      # 新模組規格書範本
│   ├── _template.py            # 新模組程式碼範本
│   ├── f01_package/            # F01 開發包（範例）
│   └── f14_package/            # F14 開發包（開發中）
│
├── data/                       # 輸出資料目錄（自動生成）
│   ├── YYYY-MM-DD_f01_fetcher.txt
│   └── YYYY-MM-DD_run.log
│
└── venv32/                     # Python 虛擬環境
```

## 🔧 20因子列表

| 編號 | 因子類別 | 說明 |
|------|---------|------|
| **F01-F03** | 機構籌碼與資金流向 | 外資未平倉、投信留倉、自營商部位 |
| **F04-F07** | 散戶情緒與槓桿壓力 | 散戶多空比、融資餘額、借券賣出 |
| **F08-F12** | 市場情緒與外部影響 | VIX指數、美股期貨、亞股表現 |
| **F13-F20** | 價格結構與權值股 | 技術指標、成交量、權值股表現 |

## 📖 文件導覽

### 我想要...

#### 🚀 使用這個專案
- **[README.md](README.md)** - 本文件，安裝和使用指南

#### ⚡ 開發新模組
- **[開發目錄說明](dev/README.md)** - 開發流程、範例、常見錯誤
- **[共同開發規範書](dev/共同開發規範書_V1.md)** ⭐
  - 📋 快速參考章節（10分鐘入門）
  - 📚 完整開發規範（深入學習）
- **[程式碼範本](dev/_template.py)** - 新模組程式碼起點
- **[規格書範本](dev/_template_spec.md)** - 新模組規格書模板

#### 📚 範例參考
- **[F01 程式碼](modules/f01_fetcher.py)** - 最佳實踐範例
- **[F01 規格書](dev/f01_package/f01_fetcher_開發規範書.md)** - 完整規格範例

#### ⚙️ 設定 Claude Code
- **[CLAUDE_CONFIG.md](CLAUDE_CONFIG.md)** - Claude Code 配置說明

### 📋 文件關係圖

```
README.md (專案入口)
    ↓
    ├─ 使用專案 → 安裝、執行、輸出說明（本文件）
    │
    ├─ 開發模組 → dev/README.md (開發目錄總覽) ⭐
    │           → dev/共同開發規範書_V1.md (完整規範)
    │           → dev/_template.py (程式碼範本)
    │           → dev/_template_spec.md (規格書範本)
    │
    ├─ 範例參考 → modules/f01_fetcher.py (程式碼範例)
    │           → dev/f01_package/ (規格書範例)
    │
    ├─ Claude Code → CLAUDE_CONFIG.md (配置說明)
    │              → CLAUDE_RESPONSE_GUIDE.md (AI 回應規範)
    │
    └─ 討論記錄 → Claude跨討論組_log.md (跨對話記錄)
```

## 🔨 開發新模組

### 快速入門（5 步驟）

1. **閱讀開發指南** ⭐
   - [dev/README.md](dev/README.md) - 開發流程總覽
   - [共同開發規範書](dev/共同開發規範書_V1.md) - 快速參考章節（10分鐘）

2. **創建開發包**
   ```bash
   mkdir dev\f02_package
   ```

3. **複製範本**
   ```bash
   copy dev\_template.py dev\f02_package\f02_fetcher_dev.py
   copy dev\_template_spec.md dev\f02_package\f02_fetcher_開發規範書.md
   ```

4. **實作程式碼**
   ```python
   def fetch(date: str) -> str:
       """抓取指定日期的資料"""
       # 實作邏輯...
       return f"[ {date_formatted}  F02{描述}   source: {來源} ]"
   ```

5. **測試驗收**
   ```bash
   python dev\f02_package\f02_fetcher_dev.py 2025-12-03
   python run.py 2025-12-03 dev --module f02_fetcher_dev
   ```

### 四大核心規範

1. ✅ **回傳類型**：必須是 `str`（統一文字格式）
2. ✅ **錯誤處理**：所有錯誤都轉換為文字格式，不拋出例外
3. ✅ **日期格式**：輸入 `YYYY-MM-DD` → 輸出 `YYYY.MM.DD`
4. ✅ **模組代號**：大寫（F01, F02...）

詳細說明請參考：
- [dev/README.md](dev/README.md) - 完整開發流程、常見錯誤
- [共同開發規範書](dev/共同開發規範書_V1.md) - 詳細技術規範

## 🧪 測試

### 測試單一模組
```bash
python modules/f01_fetcher.py 2025-12-03
```

### 執行所有模組（驗收模式）
```bash
python run.py 2025-12-03 dev
```

## ⚙️ 執行流程

```
使用者執行 run.py
    ↓
載入模組 (importlib)
    ↓
呼叫 fetch(date)
    ↓
接收文字格式結果
    ↓
驗證格式 (validate_text_format)
    ↓
寫入 .txt 檔案 + .log 日誌
```

### 關鍵設計

- **模組責任**：實作 `fetch()` 函式，回傳統一格式文字
- **run.py 責任**：載入模組 → 驗證格式 → 寫入檔案
- **向後兼容**：自動轉換舊的 dict 格式為文字格式
- **統一輸出**：所有資料都是 `.txt` 文字檔（UTF-8 編碼）

## 📊 輸出格式詳細說明

### 成功格式
```
[ {日期}  {模組代號}{描述}   source: {來源} ]
```

**範例**：
```
[ 2025.12.03  F01台指期外資淨額 -29,439 口（多方 19,214，空方 48,653）   source: TAIFEX ]
```

### 錯誤格式
```
[ {日期}  {模組代號} 錯誤: {錯誤訊息}   source: {來源} ]
```

**範例**：
```
[ 2025.11.30  F01 錯誤: 該日無交易資料（可能是假日或休市日）   source: TAIFEX ]
```

## 🤝 貢獻與外包開發

### 外包商交付流程

1. **接收規格書** - 閱讀對應模組的開發規範書
2. **開發模組** - 在 `dev/` 目錄下開發
3. **自我測試** - 使用範例日期測試
4. **提交驗收** - 提供程式碼和測試結果

### 驗收標準

✅ 符合統一文字格式
✅ 錯誤處理完整（不拋出例外）
✅ 通過測試案例
✅ 程式碼清晰易懂（中文註解）

## 📞 聯絡與支援

如有問題或建議：
- 提交 GitHub Issue
- 參考文件：[共同開發規範書](dev/共同開發規範書_V1.md)

---

**版本**: 4.0.0
**最後更新**: 2025-12-05
**狀態**: ✅ 開發中
**輸出格式**: 統一文字格式 (.txt)