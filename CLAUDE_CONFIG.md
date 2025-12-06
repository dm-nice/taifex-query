# Claude Code 配置說明文件

> **文件用途**: 說明 Taifex 專案的 Claude Code 配置架構與使用方式
> **最後更新**: 2025-12-06
> **版本**: 2.0

---

## 📋 文件系統總覽

本專案使用三層文件架構來配置 Claude Code：

| 檔案 | 用途 | 對象 | 優先級 |
|------|------|------|--------|
| `.claude/settings.json` | 專案配置（JSON） | Claude Code | ⭐⭐⭐ |
| `CLAUDE_RESPONSE_GUIDE.md` | AI 回應規範 | Claude 助理 | ⭐⭐⭐ |
| `Claude跨討論組_log.md` | 跨對話記錄 | 知識傳承 | ⭐⭐ |

---

## 🎯 配置檔案架構

```
C:\Taifex\
├── .claude/
│   ├── settings.json              ✅ 專案配置（環境設定）
│   └── settings.local.json        🔧 本機配置（Git 忽略）
│
├── CLAUDE_CONFIG.md               📖 本文件（配置說明）
├── CLAUDE_RESPONSE_GUIDE.md       📖 AI 回應規範（行為準則）
├── Claude跨討論組_log.md          📖 討論記錄（知識庫）
│
├── README.md                      📖 專案入口（使用者）
├── dev/
│   ├── README.md                  📖 開發指南
│   └── 共同開發規範書_V1.md       📖 技術規範
│
└── data/                          📁 輸出目錄
```

---

## 1️⃣ `.claude/settings.json` - 專案配置

### 📍 位置
```
C:\Taifex\.claude\settings.json
```

### 🎯 用途
Claude Code 官方支援的專案配置檔，包含：
- 專案基本資訊（名稱、版本、描述）
- Python 版本與編碼規範
- 專案架構定義
- 統一文字格式規範（v5.0）

### ✅ 目前配置狀態

**已配置項目**：
- ✅ 專案資訊（台指期貨20因子預測系統）
- ✅ Python 版本要求（3.9+）
- ✅ 編碼規範（PEP 8）
- ✅ 系統架構（run.py + 模組化設計）
- ✅ 統一文字格式 v5.0 規範
- ✅ 20因子分類定義

### 🔧 如何使用

Claude Code 會自動讀取此檔案，不需要額外設定。

### 📝 核心配置範例

```json
{
  "project": {
    "name": "台指期貨20因子預測系統",
    "description": "基於20個市場因子分析台指期貨隔日漲跌趨勢的預測系統",
    "version": "1.0.0",
    "architecture": "模組化設計 + 統一文字格式輸出"
  },
  "python": {
    "version": "3.9+",
    "style_guide": "PEP 8",
    "encoding": "UTF-8"
  },
  "module_output_format": {
    "version": "5.0",
    "success_format": "FXX: {標題} [{標籤}] : {數值} [{來源}]",
    "error_format": "[ YYYY.MM.DD  FXX 錯誤: {訊息}   source: {來源} ]"
  }
}
```

### ⚠️ 注意事項
- IDE 可能顯示 schema 警告（可忽略，不影響功能）
- 本機專屬設定請使用 `.claude/settings.local.json`（已加入 `.gitignore`）

---

## 2️⃣ `CLAUDE_RESPONSE_GUIDE.md` - AI 回應規範

### 📍 位置
```
C:\Taifex\CLAUDE_RESPONSE_GUIDE.md
```

### 🎯 用途
定義 Claude AI 助理的行為規範與回應準則，包含：
- **角色設定** - Python 工程師、財務分析專家、邏輯專家
- **核心任務** - 程式碼審查、客觀回應、專業溝通
- **模型選擇** - Opus/Sonnet/Haiku 使用指引
- **回應格式** - 錯誤訊息、程式碼區塊、結構規範
- **安全限制** - 回應原則、範圍限制、禁止行為
- **專案整合** - Taifex 專案特定規範

### ✅ 何時參考
1. **開發新模組** - 了解輸出格式要求
2. **程式碼審查** - 檢查記憶體、安全性、錯誤處理
3. **問題診斷** - 使用結構化問題分析流程
4. **文件撰寫** - 遵循回應格式規範

### 📝 關鍵規範摘要

**統一文字格式 v5.0**：
```
✅ 成功: FXX: 台指期貨外資 [未平倉] [多空淨額] : -26,823 口 [TAIFEX]
❌ 錯誤: [ 2025.12.06  FXX 錯誤: {訊息}   source: TAIFEX ]
```

**四大核心規範**：
1. ✅ 回傳類型必須是 `str`
2. ✅ 錯誤轉換為文字格式，不拋出例外
3. ✅ 日期格式：`YYYY-MM-DD` → `YYYY.MM.DD`
4. ✅ 模組代號：大寫（F01, F02...）

### 💡 使用建議
在新對話開始時提醒 Claude：
```
請參考 CLAUDE_RESPONSE_GUIDE.md 的規範來協助我開發。
```

---

## 3️⃣ `Claude跨討論組_log.md` - 討論記錄

### 📍 位置
```
C:\Taifex\Claude跨討論組_log.md
```

### 🎯 用途
跨對話的知識傳承與決策記錄，包含：
- **專案核心資訊** - 架構、路徑、指令
- **關鍵概念速查** - 統一文字格式、四大規範
- **專案狀態** - 模組進度、文件完成度
- **重要決策記錄** - 為什麼這樣做
- **經驗分享** - v5.0 優缺點、文件撰寫技巧
- **討論記錄** - 每次重要變更的完整記錄

### ✅ 何時使用

**讀取歷史**：
```
讀取 Claude跨討論組_log.md 的最新討論內容
```

**追加記錄**：
```
把剛才的工作記錄追加到 Claude跨討論組_log.md
```

### 📝 記錄範本

```markdown
### YYYY-MM-DD - [主題名稱]

#### 背景
[簡述情境]

#### 完成事項
1. ✅ [完成項目 1]
2. ✅ [完成項目 2]

#### 決策
- [重要決定 1]
- [重要決定 2]

#### 驗證結果
- ✅ [驗證項目 1]
- ✅ [驗證項目 2]
```

---

## 🎯 文件分工與職責

### 配置層（Claude Code 設定）
```
.claude/settings.json
├─ 專案資訊（名稱、版本、架構）
├─ Python 規範（版本、編碼標準）
└─ 輸出格式（統一文字格式 v5.0）
```

### 規範層（開發規範）
```
CLAUDE_RESPONSE_GUIDE.md
├─ AI 助理角色設定
├─ 回應格式規範
├─ 專案特定規範
└─ 安全與限制

dev/共同開發規範書_V1.md
├─ 統一文字格式詳細說明
├─ 開發流程（6 步驟）
├─ 錯誤處理規範
└─ 測試與驗收標準
```

### 知識層（傳承與記錄）
```
Claude跨討論組_log.md
├─ 專案狀態追蹤
├─ 重要決策記錄
├─ 經驗分享
└─ 討論記錄（按日期）
```

### 入口層（使用者導覽）
```
README.md
├─ 快速開始
├─ 專案結構
├─ 使用方式
└─ 文件導覽

dev/README.md
├─ 開發流程
├─ 程式碼範本
├─ 常見錯誤
└─ 範例參考
```

---

## 🔧 配置維護指南

### 何時更新 `.claude/settings.json`
- ✅ 專案架構改變（新增/移除核心模組）
- ✅ Python 版本升級
- ✅ 統一格式規範變更（版本號更新）
- ⚠️ 詳細技術規範請改在 `dev/共同開發規範書_V1.md`

### 何時更新 `CLAUDE_RESPONSE_GUIDE.md`
- ✅ 新增 AI 回應規範
- ✅ 更新專案特定驗收標準
- ✅ 修改安全與限制政策
- ✅ 整合新的開發流程

### 何時更新 `Claude跨討論組_log.md`
- ✅ 每次重大變更完成後
- ✅ 做出重要技術決策時
- ✅ 發現值得分享的經驗時
- ✅ 模組狀態變更時（開發中→上線）

### 何時更新 `README.md`
- ✅ 新功能上線
- ✅ 安裝步驟變更
- ✅ 使用方式調整
- ✅ 文件結構變化

---

## 📊 專案當前狀態（2025-12-06）

### 模組開發進度
| 模組 | 功能 | 狀態 | 輸出格式 |
|------|------|------|----------|
| F01 | 台指期外資未平倉 | ✅ 正式上線 | v5.0 簡潔格式 |
| F14 | 台指期貨收盤價 | 🔄 開發中 | v4.0 統一文字格式 |
| F02-F13 | 待開發 | ⏸️ 計劃中 | - |

### 文件完成度
| 文件 | 狀態 | 版本 |
|------|------|------|
| `.claude/settings.json` | ✅ 完成 | - |
| `CLAUDE_RESPONSE_GUIDE.md` | ✅ 完成 | 3.0 |
| `Claude跨討論組_log.md` | ✅ 完成 | 2.0 |
| `README.md` | ✅ 完成 | 4.0.0 |
| `dev/README.md` | ✅ 完成 | 4.0 |
| `共同開發規範書_V1.md` | ✅ 完成 | - |

### 技術規範版本
- **統一文字格式**: v5.0（F01 簡潔格式）
- **開發流程**: 6 步驟
- **Python 版本**: 3.9+
- **編碼**: UTF-8（Windows 終端兼容）

---

## 🎓 最佳實踐

### 1. 新對話開始時
```
你好！請先閱讀以下文件：
1. CLAUDE_RESPONSE_GUIDE.md - AI 回應規範
2. Claude跨討論組_log.md - 最新討論記錄
3. dev/共同開發規範書_V1.md - 技術規範
```

### 2. 開發新模組時
```
我要開發 F02 模組，請參考：
1. dev/README.md - 開發流程
2. modules/f01_fetcher.py - 程式碼範例
3. dev/f01_package/f01_fetcher_開發規範書.md - 規格書範例
```

### 3. 完成工作後
```
請把剛才的工作記錄追加到 Claude跨討論組_log.md
```

### 4. 保持文件同步
```
程式碼變更 → 更新規格書 → 更新 README → 記錄討論組
```

---

## 📞 常見問題

### Q1: `.claude/settings.json` 和 `CLAUDE_RESPONSE_GUIDE.md` 有什麼區別？

**A**:
- `.claude/settings.json` = **專案配置**（結構化資訊、技術參數）
- `CLAUDE_RESPONSE_GUIDE.md` = **行為準則**（AI 助理如何回應、溝通規範）

### Q2: 需要同時維護這麼多文件嗎？

**A**: 各有職責，互不重複：
- **配置檔** - Claude Code 自動讀取
- **規範書** - 開發者參考技術細節
- **討論記錄** - 跨對話知識傳承
- **README** - 使用者快速上手

### Q3: Claude Code 會讀取哪些檔案？

**A**: 自動讀取順序：
1. `.claude/settings.json`（專案配置）
2. `.claude/settings.local.json`（本機配置）
3. `CLAUDE_RESPONSE_GUIDE.md`（AI 規範）
4. 根目錄 `.md` 檔案（README、討論記錄等）

### Q4: 如何讓 Claude 記住上次的討論內容？

**A**: 使用跨討論組記錄：
```
# 每次重要工作完成後
請把剛才的工作記錄追加到 Claude跨討論組_log.md

# 下次對話開始時
請讀取 Claude跨討論組_log.md 的最新討論內容
```

### Q5: 統一文字格式 v5.0 和 v4.0 有什麼區別？

**A**:
- **v4.0**: `[ 2025.12.06  F01台指期外資淨額 -26,823 口（多方 21,744，空方 48,567）   source: TAIFEX ]`
- **v5.0**: `F01: 台指期貨外資 [未平倉] [多空淨額] : -26,823 口 [TAIFEX]`（更簡潔）

---

## 📚 相關文件

### 核心文件
- [README.md](README.md) - 專案入口
- [CLAUDE_RESPONSE_GUIDE.md](CLAUDE_RESPONSE_GUIDE.md) - AI 回應規範
- [Claude跨討論組_log.md](Claude跨討論組_log.md) - 討論記錄

### 開發文件
- [dev/README.md](dev/README.md) - 開發指南
- [dev/共同開發規範書_V1.md](dev/共同開發規範書_V1.md) - 技術規範
- [dev/_template.py](dev/_template.py) - 程式碼範本

### 範例參考
- [modules/f01_fetcher.py](modules/f01_fetcher.py) - F01 程式碼
- [dev/f01_package/f01_fetcher_開發規範書.md](dev/f01_package/f01_fetcher_開發規範書.md) - F01 規格書

---

## 🔄 版本記錄

### Version 2.0 (2025-12-06)
- ✅ 更新為三層文件架構
- ✅ 新增 CLAUDE_RESPONSE_GUIDE.md 說明
- ✅ 新增 Claude跨討論組_log.md 說明
- ✅ 移除已刪除的 PROJECT_SPEC.md 引用
- ✅ 更新專案狀態（F01 v5.0 上線）
- ✅ 新增最佳實踐與常見問題

### Version 1.0 (2025-12-05)
- ✅ 初始版本
- ✅ 說明三種配置檔案
- ✅ 建立配置方案建議

---

**最後更新**: 2025-12-06
**維護者**: Claude Code
**版本**: 2.0
