# OpenSpec 工作流程解釋 & 合作指南

> 這份文件說明 OpenSpec 如何運作，以及我們應該如何合作開發新模組

---

## 🎯 OpenSpec 工作流程解釋

### 📊 三階段工作流

```
Stage 1: 創建變更提案         Stage 2: 實現代碼            Stage 3: 歸檔已完成
────────────────────       ─────────────────          ──────────────────
proposal.md ────────────→  完整實現代碼   ────────→  archive/
tasks.md                  通過所有測試
design.md (可選)           更新 specs/
specs/ deltas
```

**關鍵原則**: **先規範後代碼** - 不著手編寫代碼，除非提案已獲批准！

---

## 👥 我們應該如何合作

### 1️⃣ **你提出想法 → 我創建提案** (Stage 1: Creating Changes)

**你的觸發詞**:

```
- "幫我規劃開發 F02"
- "我想開發新的資料來源模組"
- "幫我創建變更提案"
- "我要做 XXX 功能" (涉及新增/破壞性改變/架構改變)
```

**我的工作流**:

```
1. 讀取 openspec/project.md (專案規範)
2. 執行 openspec list (查看現有變更)
3. 執行 openspec list --specs (查看已有規範)
4. 建立 proposal.md (為什麼、做什麼、影響)
5. 建立 tasks.md (實現清單)
6. 建立 specs/ deltas (新/修改/移除需求)
7. 執行 openspec validate <change-id> --strict (驗證)
8. **請求你的批准** ← 停在這裡，等待回饋
```

**我建立的結構**:

```
openspec/changes/
└── add-f02-xxxx/           # change-id (動詞開頭，kebab-case)
    ├── proposal.md         # 為什麼做、做什麼、影響誰
    ├── tasks.md            # 實現清單 (16-18 個任務)
    ├── design.md           (可選)
    └── specs/
        └── [capability]/
            └── spec.md     # ADDED/MODIFIED/REMOVED 需求
```

---

### 2️⃣ **你批准提案 → 我逐項實現** (Stage 2: Implementing Changes)

**你說**:

```
"同意，開始實現"
"提案看起來不錯，開始編碼"
```

**我的流程** (必須按順序):

```bash
1. 讀取 proposal.md       ← 了解做什麼
2. 讀取 design.md         ← 了解技術決策 (如果存在)
3. 讀取 tasks.md          ← 拿到實現清單
4. 完成 Phase 1: 文檔
   - [ ] 1.1 XXX
   - [ ] 1.2 YYY
5. 完成 Phase 2: 代碼
6. 完成 Phase 3: 測試
7. 完成 Phase 4: 部署
8. 更新 tasks.md          ← 所有項目改為 [x]
9. 確認完成
```

**關鍵規則**:

- ✅ 逐個完成任務
- ✅ 每完成一個就標記 `[x]`
- ❌ 不能跳過任務
- ❌ 實現前**必須等批准**

---

### 3️⃣ **部署成功 → 歸檔變更** (Stage 3: Archiving Changes)

**你說**:

```
"F02 已上線，開始歸檔"
```

**我執行**:

```bash
openspec archive add-f02-xxxx --yes

結果:
changes/add-f02-xxxx/  →  changes/archive/2025-12-17-add-f02-xxxx/
specs/                 ← 自動更新為新規範
```

---

## 🎬 實例：開發 F02 模組

### Stage 1: 你要求新功能

```
你說: "幫我規劃開發 F02 (外資-未平倉-多方)"
```

### 我會做

```markdown
# Change: add-f02-foreign-long

## Why
補充 F01 的籌碼分析，提供外資多方口數

## What Changes
- 新增 F02 模組 (fetch 函式 + 21 個測試)
- 新增 design.md (技術設計)
- 新增 tasks.md (16 個實現任務)

## Impact
- 新增規範: specs/f02-foreign-long/spec.md
- 新增代碼: dev/f02_package/
- 部署到: modules/f02_fetcher.py
```

完整的 proposal.md、tasks.md、spec.md 會被建立

### 你審閱並說

```
"看起來合理，開始編碼"
```

### Stage 2: 我開始實現

```
讀取 proposal.md ✓
讀取 design.md (如果需要) ✓
讀取 tasks.md ✓
開始 Phase 1: 文檔化
  - [x] 1.1 編寫 proposal.md
  - [x] 1.2 編寫 design.md
  - [x] 1.3 編寫 tasks.md
  - [x] 1.4 編寫 specs/f02/spec.md
  - [x] 1.5 驗證規範
開始 Phase 2: 代碼實現
  - [x] 2.1 複製 F11 範本
  - [x] 2.2 改寫 fetch() 函式
  - [ ] 2.3 ... (繼續)
```

### 完成後: 你說

```
"F02 已測試驗收，準備上線"
```

### Stage 3: 歸檔

```bash
openspec archive add-f02-xxxx --yes
結果: changes/archive/2025-12-17-add-f02-xxxx/
```

---

## 🔄 日常合作模式

| 情景 | 你做 | 我做 |
|------|------|------|
| **開發新模組** | "幫我規劃 F03" | 建立完整提案，等批准 |
| **修復 bug** | 直接說要修 | 不建提案，直接修復 |
| **優化性能** | "F11 太慢" | 建提案 (改變行為) |
| **更新規範** | "改下文檔" | 不建提案，直接改 |
| **重構代碼** | "整理 F04" | 建提案 (架構變更) |

---

## ✅ 你應該檢查的清單

### 在要求任何功能前

- [ ] 我已讀 `openspec/project.md` (專案規範)
- [ ] 我已執行 `openspec list` (看現有變更)
- [ ] 我已執行 `openspec list --specs` (看已有規範)
- [ ] 我確認要求「新增功能」還是「修復 bug」

### 批准提案前

- [ ] proposal.md 清楚說明「為什麼做」
- [ ] 影響範圍合理 (哪些文件、哪些模組)
- [ ] tasks.md 有完整的實現清單
- [ ] spec.md 有清楚的需求和場景

---

## 🛠️ 常用 CLI 命令

```bash
# 查看現狀
openspec list                # 有哪些變更進行中?
openspec list --specs        # 現有規範?
openspec show f02-foreign-long  # 檢視特定變更詳情

# 驗證
openspec validate add-f02-xxxx --strict  # 嚴格驗證

# 歸檔
openspec archive add-f02-xxxx --yes  # 部署後歸檔
```

---

## 🎯 我們的工作節奏

```
你提出需求
    ↓
我建立提案 (proposal.md + tasks.md + specs/)
    ↓
你閱讀並批准
    ↓
我按 tasks.md 逐項實現
    ↓
我完成所有任務，標記 [x]
    ↓
你測試驗證
    ↓
我歸檔變更
    ↓
準備下一個模組 (循環)
```

---

## ⚡ 關鍵要點

1. **規範優先** - 代碼前必須有批准的提案
2. **逐項完成** - 不能跳過 tasks.md 中的任何項目
3. **停在批准處** - 提案完成後我會停下來，等你說「開始」
4. **一次一個** - 完成當前模組才開始下一個
5. **保持同步** - specs/ 是真相，changes/ 是提案

---

## 📚 提案文件結構詳解

### proposal.md (為什麼做)

```markdown
# Change: add-f02-foreign-long

## Why
[1-2 句說明問題或機會]
補充 F01 的籌碼分析，提供外資多方口數，完整籌碼視圖

## What Changes
[清單列出改變]
- 新增 F02 模組 (fetch 函式 + 21 個測試)
- 新增技術設計文件 (design.md)
- 新增實現清單 (tasks.md)
- **BREAKING**: 輸出格式統一為 v5.0

## Impact
[影響範圍]
- 受影響規範: specs/f02-foreign-long/spec.md (新)
- 受影響代碼: dev/f02_package/, modules/f02_fetcher.py
```

### tasks.md (做什麼)

```markdown
## 1. Phase 1: 文檔化 (1.5 小時)
- [ ] 1.1 編寫 project.md (項目概述)
- [ ] 1.2 編寫 proposal.md (變更提案) ← 你正在這
- [ ] 1.3 編寫 design.md (技術設計)
- [ ] 1.4 編寫 spec.md (功能規格 + 場景)
- [ ] 1.5 驗證規範: openspec validate add-f02-xxxx --strict

## 2. Phase 2: 代碼實現 (1.5 小時)
- [ ] 2.1 複製 F11 為 F02 的骨架
- [ ] 2.2 改寫 fetch_f02() 函式 (30 行)
- [ ] 2.3 改寫 format_output() 函式 (10 行)
- [ ] 2.4 改寫 format_error() 函式 (5 行)
- [ ] 2.5 代碼測試通過 (local run)
- [ ] 2.6 代碼優化 (移除重複、改進日誌)

## 3. Phase 3: 完整測試 (1 小時)
- [ ] 3.1 編寫 21 個測試 (6 類別)
- [ ] 3.2 所有測試通過 (pytest -v)
- [ ] 3.3 驗證 90%+ 覆蓋率
- [ ] 3.4 集成測試通過

## 4. Phase 4: 部署上線 (0.5 小時)
- [ ] 4.1 複製到 modules/f02_fetcher.py
- [ ] 4.2 集成到 run.py
- [ ] 4.3 生產驗證 (實時資料)
```

### spec.md (需求和場景)

```markdown
## ADDED Requirements

### Requirement: F02 資料抓取
系統應該能夠從 TAIFEX 抓取外資未平倉-多方數據

#### Scenario: 成功抓取
- **WHEN** 查詢有效交易日期
- **THEN** 回傳 "2025.12.17  F02: 外資-未平倉-多方 : 125,432 口 [TAIFEX]"

#### Scenario: 無交易資料
- **WHEN** 查詢假日
- **THEN** 回傳 "2025.12.14  F02 錯誤: 該日無交易資料 [TAIFEX]"

### Requirement: 異常處理
所有異常必須轉為文字格式，不拋出例外

#### Scenario: 網路逾時
- **WHEN** 伺服器無響應超過 10 秒
- **THEN** 回傳 "F02 錯誤: 伺服器無回應 [TAIFEX]"
```

---

## 🚀 現在開始

你可以直接告訴我：

### 開始新模組開發

```
"幫我規劃開發 F02 (外資-未平倉-多方)"
```

### 修復現有 bug

```
"F11 有個 bug，輸出格式不對"
```

### 優化性能

```
"F04 抓取太慢，能否優化?"
```

### 查看現狀

```
"有哪些變更進行中?"
"現有規範有哪些?"
```

**準備好了嗎？告訴我你想做什麼！** 🎯

---

## 📖 更多資訊

詳細資訊參考:

- [openspec/AGENTS.md](../openspec/AGENTS.md) - 完整 OpenSpec 規範
- [openspec/project.md](../openspec/project.md) - 專案規範和慣例
- [dev/QUICK_GUIDES.md](./QUICK_GUIDES.md) - 快速導航
- [dev/README.md](./README.md) - 開發指南

---

**版本**: 1.0  
**最後更新**: 2025-12-17  
**用途**: 說明 OpenSpec 工作流程和合作方式
