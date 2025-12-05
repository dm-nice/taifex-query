# Claude Code 配置檔說明

本文件說明如何配置 Claude Code 的三個關鍵設定檔，讓 AI 助手更好地理解和協助您的專案開發。

---

## 📋 三個配置檔案總覽

| 檔案 | 用途 | 位置 | 優先級 |
|------|------|------|--------|
| `.claude/settings.json` | 專案配置（JSON 格式） | `.claude/settings.json` | 高 |
| `CLAUDE.md` | 專案說明（Markdown） | 根目錄 | 中 |
| `.claudeconfig` | 簡易配置（JSON） | 根目錄 | 低 |

**建議使用**: `.claude/settings.json` + `PROJECT_SPEC.md`

---

## 1️⃣ `.claude/settings.json`（推薦✅）

### 📍 位置
```
C:\Taifex\.claude\settings.json
```

### 🎯 用途
- Claude Code 官方支援的配置檔
- 結構化專案資訊（JSON 格式）
- 可定義專案架構、編碼規範、開發流程等

### ✅ 目前配置狀態
您已經創建了這個檔案，包含：
- ✅ 專案資訊（名稱、版本、架構）
- ✅ Python 編碼規範（PEP 8、命名規則）
- ✅ 系統架構定義
- ✅ 20因子分類
- ✅ 編碼要求（文檔、錯誤處理、測試）
- ✅ 統一文字格式規範（`module_output_format`）

### 🔧 如何使用
Claude Code 會自動讀取此檔案，不需要額外設定。

### ⚠️ 注意事項
- IDE 可能會顯示 schema 警告（可忽略，不影響功能）
- 如果想消除警告，可移除 `module_output_format` 區塊（因為已有 `PROJECT_SPEC.md`）

### 📝 範例配置
```json
{
  "project": {
    "name": "台指期貨20因子預測系統",
    "description": "基於20個市場因子分析台指期貨隔日漲跌趨勢的預測系統",
    "version": "1.0.0"
  },
  "python": {
    "version": "3.9+",
    "style_guide": "PEP 8"
  }
}
```

---

## 2️⃣ `CLAUDE.md`（選用）

### 📍 位置
```
C:\Taifex\CLAUDE.md
```

### 🎯 用途
- Markdown 格式的專案說明
- 給 Claude 看的專案介紹和規範
- 適合寫長篇說明、架構設計、開發流程

### ✅ 何時使用
- 需要詳細解釋專案背景
- 需要說明複雜的業務邏輯
- 想用 Markdown 格式（比 JSON 更易讀）

### 📝 建議內容結構
```markdown
# 專案說明

## 背景
台指期貨20因子預測系統...

## 技術架構
- 模組化設計
- 統一文字格式輸出

## 開發規範
請參考：
- PROJECT_SPEC.md - 統一格式規範
- dev/共同開發規範書_V1.md - 開發規範

## 特殊注意事項
1. 所有模組必須回傳 str 類型
2. 日期格式：YYYY-MM-DD → YYYY.MM.DD
3. 錯誤不可拋出例外
```

### 💡 本專案建議
**不需要創建 `CLAUDE.md`**，因為您已經有：
- ✅ `PROJECT_SPEC.md` - 技術規格總覽
- ✅ `README.md` - 專案介紹
- ✅ `.claude/settings.json` - 結構化配置

---

## 3️⃣ `.claudeconfig`（不推薦❌）

### 📍 位置
```
C:\Taifex\.claudeconfig
```

### 🎯 用途
- 舊版 Claude 配置檔
- 簡易 JSON 配置

### ⚠️ 為何不推薦
- 功能較少
- 已被 `.claude/settings.json` 取代
- 不如 Markdown 檔案易讀

### 💡 本專案建議
**不需要創建 `.claudeconfig`**

---

## 🎯 本專案最佳配置方案

### ✅ 已有的配置（推薦保留）

```
C:\Taifex\
├── .claude/
│   └── settings.json          ✅ 專案配置（結構化資訊）
├── PROJECT_SPEC.md            ✅ 統一格式規範（技術細節）
└── README.md                  ✅ 專案介紹（使用者指南）
```

### 📋 各檔案分工

| 檔案 | 內容 | 讀者 |
|------|------|------|
| `.claude/settings.json` | 專案資訊、編碼規範、架構定義 | Claude Code |
| `PROJECT_SPEC.md` | 統一文字格式規範、實作細節 | 開發者 + Claude |
| `README.md` | 安裝、使用、快速開始 | 使用者 |

### ❌ 不需要的檔案
- ❌ `CLAUDE.md` - 功能已被 `PROJECT_SPEC.md` 涵蓋
- ❌ `.claudeconfig` - 已被 `.claude/settings.json` 取代

---

## 🔧 配置檔案維護指南

### 何時更新 `.claude/settings.json`
- ✅ 專案架構改變
- ✅ 新增開發規範
- ✅ 修改編碼要求
- ⚠️ 統一格式規範（建議改在 `PROJECT_SPEC.md`）

### 何時更新 `PROJECT_SPEC.md`
- ✅ 統一格式規範變更
- ✅ 函式簽章修改
- ✅ 實作範例更新
- ✅ 版本記錄

### 何時更新 `README.md`
- ✅ 新功能上線
- ✅ 安裝步驟變更
- ✅ 使用方式調整

---

## 🎓 最佳實踐

### 1. 保持文件同步
```
程式碼變更 → 更新規格書 → 更新 README
```

### 2. 關注點分離
- **技術細節** → `PROJECT_SPEC.md`
- **專案配置** → `.claude/settings.json`
- **使用說明** → `README.md`

### 3. 定期檢查
- 每次重大變更後，檢查三個文件是否一致
- 確保範例程式碼與實際實作相符

---

## 📞 常見問題

### Q1: `.claude/settings.json` 的 schema 警告能消除嗎？
**A**: 可以，但不建議。警告不影響功能，如果真的想消除，可以移除 `module_output_format` 區塊（因為已有 `PROJECT_SPEC.md`）。

### Q2: 需要同時創建三個配置檔嗎？
**A**: 不需要。推薦只用 `.claude/settings.json` + `PROJECT_SPEC.md` + `README.md`。

### Q3: Claude Code 會讀取哪些檔案？
**A**: Claude Code 會自動讀取：
1. `.claude/settings.json`（優先）
2. `CLAUDE.md`（如果存在）
3. 專案根目錄的 `.md` 檔案（如 `README.md`, `PROJECT_SPEC.md`）

### Q4: 如果有衝突資訊怎麼辦？
**A**: Claude Code 優先讀取 `.claude/settings.json`，但通常會綜合參考所有文件。建議保持資訊一致。

---

## 📚 延伸閱讀

- [PROJECT_SPEC.md](PROJECT_SPEC.md) - 統一格式技術規範
- [README.md](README.md) - 專案使用指南
- [共同開發規範書](dev/共同開發規範書_V1.md) - 模組開發規範

---

**最後更新**: 2025-12-05
**維護者**: Claude Code
