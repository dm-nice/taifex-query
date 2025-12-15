# F01 規格書欄位到 OpenSpec 的映射表

**目的**：說明 F01 規格書中的各個欄位如何對應到 OpenSpec 的專案上下文和變更管理系統

---

## 📋 規格書核心欄位對應

### 1️⃣ 基本資訊欄位

| 規格書欄位 | 內容 | OpenSpec 對應位置 | 用途 |
|-----------|------|-------------------|------|
| **模組編號** | `f01` | `openspec/project.md` > Purpose | 識別模組 |
| **模組名稱** | `f01_fetcher` | `openspec/project.md` > Purpose | 命名規範 |
| **功能說明** | 抓取台指期貨外資的未平倉淨口數 | `openspec/project.md` > Purpose | 開發目標 |
| **資料來源** | TAIFEX | `openspec/project.md` > External Dependencies | 資料源管理 |
| **難度評級** | ⭐⭐☆☆☆ (2/5) | `openspec/project.md` > Domain Context | 技術複雜度 |
| **重要限制** | API 無視日期參數 | `openspec/project.md` > Important Constraints | 核心限制 |

### 2️⃣ 技術棧欄位

| 規格書欄位 | 內容 | OpenSpec 對應位置 | 用途 |
|-----------|------|-------------------|------|
| **實作語言** | Python 3.9+ | `openspec/project.md` > Tech Stack | 環境要求 |
| **核心套件** | requests, pandas, lxml | `openspec/project.md` > Tech Stack | 依賴管理 |
| **資料格式** | HTML 表格（MultiIndex） | `openspec/project.md` > Tech Stack | 資料處理方式 |
| **輸出格式** | 文字格式 v5.0 | `openspec/project.md` > Tech Stack | 結果格式規範 |

### 3️⃣ 開發規範欄位

| 規格書欄位 | 內容 | OpenSpec 對應位置 | 用途 |
|-----------|------|-------------------|------|
| **命名規則** | `fXX`（小寫）、snake_case | `openspec/project.md` > Project Conventions > Code Style | 程式碼風格 |
| **註解規範** | 中文註解 | `openspec/project.md` > Project Conventions > Code Style | 程式碼可維護性 |
| **統一介面** | `fetch(date: str) -> str` | `openspec/project.md` > Project Conventions > Architecture Patterns | 介面契約 |
| **錯誤處理** | error vs failed 區分 | `openspec/project.md` > Project Conventions > Architecture Patterns | 錯誤管理 |
| **資料轉換** | 字串轉整數、千分位處理 | `openspec/project.md` > Project Conventions > Architecture Patterns | 資料處理 |

### 4️⃣ 測試規範欄位

| 規格書欄位 | 內容 | OpenSpec 對應位置 | 用途 |
|-----------|------|-------------------|------|
| **測試工具** | pytest | `openspec/project.md` > Project Conventions > Testing Strategy | 測試框架 |
| **測試案例** | 4 個必測日期 | `openspec/project.md` > Project Conventions > Testing Strategy | 測試清單 |
| **驗收標準** | 統一文字格式輸出 | `openspec/project.md` > Project Conventions > Testing Strategy | 驗收條件 |

### 5️⃣ 資料源技術欄位

| 規格書欄位 | 內容 | OpenSpec 對應位置 | 用途 |
|-----------|------|-------------------|------|
| **API 端點** | `https://www.taifex.com.tw/cht/3/futContractsDate` | `openspec/project.md` > Domain Context | 資料源位置 |
| **表格結構** | MultiIndex（多層） | `openspec/project.md` > Domain Context | 資料結構規範 |
| **目標欄位** | 身份別、多方、空方 | `openspec/project.md` > Domain Context | 資料提取清單 |
| **更新頻率** | 每個交易日 | `openspec/project.md` > External Dependencies | 資料更新週期 |

---

## 🔄 規格變更流程對應

### 如果需要修改規格書的欄位

當您需要修改規格書中的任何內容時，建議：

**情景 1：修改基本資訊（如難度評級）**
1. 更新 `f01_fetcher_spec.md` 中的欄位
2. 同步更新 `openspec/project.md` 中的對應內容
3. 若影響接口，使用 `openspec create` 建立變更提案

**情景 2：新增技術限制或約束**
1. 更新 `f01_fetcher_spec.md` 中的「重要限制」或「特殊處理邏輯」
2. 更新 `openspec/project.md` 中的「Important Constraints」
3. 若涉及設計變更，建立變更提案

**情景 3：修改資料源（如換新 API）**
1. 更新 `f01_fetcher_spec.md` 中的「資料來源」章節
2. 更新 `openspec/project.md` 中的「External Dependencies」
3. 更新「Domain Context」中的 API 端點和表格結構
4. **必須**建立變更提案（新實作需求）

---

## 🎯 OpenSpec 配置總結

### 已填寫的 OpenSpec 部分

✅ **openspec/project.md** - 完整填寫

| 區段 | 內容 | 來源 |
|------|------|------|
| **Purpose** | F01 模組目標、用途、資料來源 | 規格書基本資訊 |
| **Tech Stack** | Python、requests、pandas、HTML 解析 | 規格書技術細節 |
| **Code Style** | UTF-8、命名規則、註解規範 | 規格書開發規範 |
| **Architecture** | fetch() 介面、錯誤處理、資料轉換 | 規格書實作邏輯 |
| **Testing** | pytest、4 個測試案例、驗收模式 | 規格書測試章節 |
| **Git Workflow** | dev/ 開發、modules/ 穩定版 | 規格書版本管理 |
| **Domain Context** | TAIFEX 資料特徵、表格結構、輸出格式 | 規格書資料源技術 |
| **Constraints** | ⚠️ API 無視日期參數的限制和解決方案 | 規格書已知限制 |
| **Dependencies** | 期交所、Python 套件、相關文件 | 規格書外部依賴 |

### 未填寫的 OpenSpec 部分

❌ **openspec/AGENTS.md** - 系統自動生成，無需修改

❌ **openspec/changes/** - 暫無變更提案

❌ **openspec/specs/** - 暫無額外規格定義

---

## 💡 使用建議

### 如何使用這份映射表

1. **新開發模組時**：
   - 先建立規格書 (spec.md)
   - 參考此映射表填寫 `openspec/project.md`
   - 確保規格書和 OpenSpec 保持同步

2. **修改現有規格時**：
   - 修改 `f01_fetcher_spec.md`
   - 同步更新 `openspec/project.md`
   - 必要時建立變更提案

3. **引導 AI 助手時**：
   - AI 優先閱讀 `openspec/project.md`
   - 再參考 `f01_fetcher_spec.md` 的詳細內容
   - 確保 AI 理解完整的專案背景

### 擴展到其他模組

當為 F02-F20 建立 OpenSpec 時：
1. 複製本映射表作為範本
2. 根據各模組的規格書調整欄位
3. 建立 `F0X/openspec/SPEC_TO_OPENSPEC_MAPPING.md`
4. 維持命名和結構的一致性

---

## 📚 相關檔案清單

| 檔案 | 位置 | 用途 |
|------|------|------|
| **F01 規格書** | `f01_fetcher_spec.md` | 完整的開發規範 |
| **OpenSpec 專案配置** | `openspec/project.md` | AI 助手的專案背景 |
| **OpenSpec 工作指南** | `openspec/AGENTS.md` | AI 助手的工作流程 |
| **本映射表** | `openspec/SPEC_TO_OPENSPEC_MAPPING.md` | 規格到 OpenSpec 的對應 |
| **實現代碼** | `../../modules/f01_fetcher.py` | 實際的 Python 實作 |
| **開發版本** | `f01_fetcher_dev.py` | 開發和測試用 |
| **測試檔案** | `test_f01_auto.py` | 自動化測試 |

---

**建立日期**: 2025-12-14  
**目的**: 為 OpenSpec 整合 F01 規格書  
**維護者**: 架構專員
