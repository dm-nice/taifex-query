# 🚀 OpenSpec 開發指南導航

> 快速找到你需要的指南

---

## 📚 按用途分類

### 🎯 「我要快速試驗新想法」

**→ [OpenSpec_開發試驗版.md](OpenSpec_開發試驗版.md)**

- ⏱️ 20 分鐘快速試驗
- 📝 無需文檔、測試、部署
- 🗑️ 試完直接刪掉
- ✅ 適合：陌生資料源、驗證技術方案、時間緊急

---

### 🏗️ 「我要正式開發一個新模組」

**→ [README.md](README.md) 的「OpenSpec 4-Phase 標準」**

- 📋 完整開發流程 (4.5 小時)
- 📄 5 份規範文件 (Phase 1)
- 💻 380+ 行代碼 (Phase 2)
- 🧪 21 個單元測試 (Phase 3)
- 🚀 生產部署驗證 (Phase 4)
- ✅ 適合：正式發布、長期維護、生產環境

---

### 📖 「我要參考完整例子」

**→ [F11 完整範本](f11_package/)**

- 📚 5 份設計文件 (openspec/)
- 🎯 380 行實現代碼 (f11_openspec_dev.py)
- ✅ 21 個通過測試 (test_f11_openspec.py)
- 📊 完整實現報告 (IMPLEMENTATION_REPORT.md)

**複用 F11 到新模組:**

```bash
# 複製 F11 的 openspec 目錄到新模組
cp -r f11_package/openspec f02_package/openspec

# 改成新模組的內容
code f02_package/openspec/project.md
```

---

### 📋 「我要了解開發規範」

**參考主要文件: [共同開發規範書_V1.md](共同開發規範書_V1.md)**

#### 🎯 統一輸出格式規範

所有模組必須遵循：

```
成功: 2025.12.17  FXX: 描述 : 數值 [來源]
失敗: 2025.12.17  FXX 錯誤: 錯誤訊息 [來源]
```

**例子:**

```
✅ 2025.12.17  F11: 加權股價收盤指數 : 18254.50 [TWSE]
❌ 2025.12.17  F11 錯誤: 該日無交易資料 [TWSE]
```

**規則:**

- 回傳類型必須是 `str`（統一文字格式）
- 所有異常都轉換為文字格式，不拋出例外
- 日期格式：輸入 `YYYY-MM-DD` → 輸出 `YYYY.MM.DD`
- 數值使用千分位逗號 (如 `18,254.50`)

#### 🔧 必須實作的函式

```python
def fetch(date: str) -> str:
    """
    抓取指定日期的資料
    
    Args:
        date: 查詢日期，格式 YYYY-MM-DD
        
    Returns:
        統一格式的文字字串（成功或錯誤都是文字）
    """
```

---

### ⚠️ 「我遇到常見陷阱」

#### 1️⃣ HTML 欄位名稱變動（如 F04 陷阱）

**問題**: HTML 欄位名稱可能包含不規則空白 (如 `最後 成交價` 而非 `最後成交價`)

**解決方案**:

```python
# ❌ 錯誤寫法
if col == '最後成交價': ...

# ✅ 正確寫法
keywords = ['最後成交價', '最後 成交價', '成交價']
if any(k in col_name for k in keywords): ...
```

**除錯技巧**:

```python
# 第一步：列印完整欄位名稱
print(df.columns.tolist())
# 第二步：列印第一行資料
print(df.iloc[0])
```

---

#### 2️⃣ API 日期參數限制（如 F01/F02/F03）

**問題**: 某些 API 忽視日期參數，永遠回傳「最近一個交易日」

**解決方案**:

- 在 `design.md` 明確標註「API 限制：無視日期參數」
- 如需歷史數據，改用「期貨每日交易行情下載」CSV 等替代方案
- 程式碼中添加 warning log 提示開發者

---

#### 3️⃣ 資料隱藏於下載按鈕（如 F06 陷阱）

**問題**: 網頁表格更新慢，最新資料在「下載」按鈕的文字檔裡

**解決方案** (雙軌制):

```python
# Step 1: 優先檢查下載連結
if has_download_button:
    data = download_and_parse_text_file()
else:
    # Step 2: 備援表格解析
    data = parse_html_table()
```

**安全解析文字檔**:

- 不要只看最後一行（可能是統計行或空白）
- 從下往上檢查最後 5 行，尋找有效資料
- 使用 `parts[-1]` (最後一欄) 而非固定索引

---

#### 4️⃣ 時間同步問題

**問題**: 跨模組計算時，不同源的資料可能日期不一致

**例子**: F01 (TAIFEX 最新) 與 F04 (TWSE 歷史) 混用

**解決方案**:

- 在 `design.md` 明確記錄「資料來源」與「時間特性」
- 跨模組計算前驗證日期一致性
- 使用備援欄位時要記錄警告 log

---

### 🎓 「我是新手，不知道從何開始」

**建議閱讀順序 (30 分鐘):**

1. **本檔案** (5 分鐘) - 了解有什麼指南
2. **README.md** (10 分鐘) - 了解 OpenSpec 4-Phase
3. **OpenSpec_開發試驗版.md** (10 分鐘) - 如何快速試驗
4. **F11 的 openspec/project.md** (5 分鐘) - 看看真實例子

然後選擇：

- 要試驗？→ 開始快速試驗版 (20 分鐘)
- 要開發？→ 開始完整版 (4.5 小時)

---

## 🗂️ 按檔案位置分類

```
dev/
├── README.md ⭐ 主要指南
│   └─ OpenSpec 4-Phase 標準
│
├── QUICK_GUIDES.md ⭐ 本檔案（導航）
│   └─ 快速找到需要的指南
│
├── OpenSpec_開發試驗版.md ⭐ 試驗版指南
│   └─ 20 分鐘快速驗證
│
├── 共同開發規範書_V1.md
│   └─ 統一開發規範
│
├── f11_package/ ⭐ 完整範本
│   ├─ openspec/
│   │  ├─ project.md (項目概述)
│   │  ├─ changes/.../
│   │  │  ├─ proposal.md (變更提案)
│   │  │  ├─ design.md (技術設計)
│   │  │  ├─ tasks.md (實現清單)
│   │  │  └─ specs/.../spec.md (功能規格)
│   │  └─ ...
│   ├─ f11_openspec_dev.py (380 行實現代碼)
│   └─ test_f11_openspec.py (21 個測試)
│
├── PDCA_自我改善機制設計.md
│   └─ 持續改善流程
│
└── 團隊開發爬蟲的避雷指南.md
    └─ 常見陷阱避免指南
```

---

## 📖 按開發階段分類

### Phase 1: 文檔化 (1.5 小時)

**參考文件:**

- 📖 README.md 的「Phase 1: 文檔化」
- 📋 F11 的 openspec/ 目錄 (5 份範例文件)
- 📄 共同開發規範書_V1.md

**任務:**

- [ ] 編寫 project.md (項目概述)
- [ ] 編寫 proposal.md (變更提案)
- [ ] 編寫 design.md (技術設計)
- [ ] 分析資料源頁面結構
- [ ] 確定輸出格式

---

### Phase 2: 代碼實現 (1.5 小時)

**參考文件:**

- 💻 README.md 的「Phase 2: 代碼實現」
- 💻 F11 的 f11_openspec_dev.py (380 行)
- 🚀 OpenSpec_開發試驗版.md (快速驗證想法)

**任務:**

- [ ] 創建代碼骨架
- [ ] HTTP 請求與 HTML 解析
- [ ] 提取數據
- [ ] 格式化輸出
- [ ] 異常處理 (5+ 類型)
- [ ] 代碼優化

---

### Phase 3: 測試 (1 小時)

**參考文件:**

- 🧪 README.md 的「Phase 3: 完整測試」
- 🧪 F11 的 test_f11_openspec.py (21 個測試)
- 📊 本檔案的「測試最佳實踐」

**任務:**

- [ ] 編寫格式驗證測試 (5 個)
- [ ] 編寫數據提取測試 (4 個)
- [ ] 編寫異常處理測試 (5 個)
- [ ] 編寫邊界情況測試 (3 個)
- [ ] 編寫日誌測試 (2 個)
- [ ] 編寫集成測試 (2 個)
- [ ] 驗證 90%+ 覆蓋率

---

### Phase 4: 部署 (0.5 小時)

**參考文件:**

- 🚀 README.md 的「Phase 4: 部署上線」
- 📋 F11 的 IMPLEMENTATION_REPORT.md

**任務:**

- [ ] 複製到生產目錄 (modules/)
- [ ] 集成到 run.py
- [ ] 生產驗證 (實時資料)

---

## � 更多詳細規範

完整規範文件：[共同開發規範書_V1.md](共同開發規範書_V1.md)（857 行）

包含：

- 完整核心規範詳解
- 代碼風格指南
- 測試規範
- 交付檢查清單
- FAQ

---

## �🔥 最常見的 5 個問題

### 1️⃣ 「我只有 20 分鐘，想快速試試看」

→ 使用 **[OpenSpec_開發試驗版.md](OpenSpec_開發試驗版.md)**

```bash
mkdir prototype_test
# 按指南編寫簡單代碼
python prototype_test/prototype_fetcher.py
# 試完後 rm -r prototype_test
```

---

### 2️⃣ 「我要開發一個新模組，不知道怎麼開始」

→ 複用 **[F11 完整範本](f11_package/)**

```bash
# 步驟 1: 複製 F11 的 openspec 結構
mkdir f02_package
cp -r f11_package/openspec f02_package/openspec

# 步驟 2: 改成 F02 的內容
code f02_package/openspec/project.md

# 步驟 3: 按 README.md 的 4-Phase 完成開發
# Phase 1: 編寫文檔 (1.5h)
# Phase 2: 編寫代碼 (1.5h)
# Phase 3: 編寫測試 (1h)
# Phase 4: 部署驗證 (0.5h)
```

---

### 3️⃣ 「為什麼要做 16 個任務？」

→ 參考 **[README.md](README.md)** 的「OpenSpec 4-Phase 標準」章節

- 5 個任務: 文檔完整
- 6 個任務: 代碼優質
- 4 個任務: 測試充分
- 3 個任務: 部署可靠

總共 16-18 個任務 = 最小充分集合

---

### 4️⃣ 「代碼老是拋出異常怎麼辦？」

→ 參考 **[README.md](README.md)** 的「核心開發規範」章節

關鍵規則：**異常必須捕捉，不能拋出**

```python
try:
    # 代碼
except requests.Timeout:
    return "FXX 錯誤: 連線逾時 [來源]"  # ✅ 轉為文字
except Exception as e:
    return f"FXX 錯誤: {str(e)} [來源]"   # ✅ 不拋出
```

---

### 5️⃣ 「我想看完整的測試例子」

→ 參考 **[F11 的 test_f11_openspec.py](f11_package/test_f11_openspec.py)**

- 21 個測試分為 6 個類別
- 使用 pytest + @patch 模擬
- 達成 90%+ 代碼覆蓋率
- 可直接複製改名到新模組

---

## 🎓 推薦學習路徑

### 路徑 1: 快速探索者 (1 小時)

1. 本檔案 (5 分鐘)
2. [OpenSpec_開發試驗版.md](OpenSpec_開發試驗版.md) (15 分鐘)
3. 快速試驗 (30 分鐘)
4. 決定是否投入完整版

---

### 路徑 2: 正式開發者 (5.5 小時)

1. README.md (10 分鐘)
2. 共同開發規範書_V1.md (15 分鐘)
3. F11 完整範本研究 (30 分鐘)
4. **完整 OpenSpec 4-Phase 開發 (4.5 小時)**
   - Phase 1 文檔: 1.5h
   - Phase 2 代碼: 1.5h
   - Phase 3 測試: 1h
   - Phase 4 部署: 0.5h

---

### 路徑 3: 快速複用者 (2.5 小時)

1. README.md (10 分鐘)
2. 複製 F11 的 openspec (5 分鐘)
3. **改 F11 內容到新模組**
   - Phase 1 文檔: 30 分鐘 (改不是寫)
   - Phase 2 代碼: 1h (改不是從零寫)
   - Phase 3 測試: 30 分鐘 (改不是從零寫)
   - Phase 4 部署: 15 分鐘

---

## 🔗 快速連結

**常用檔案一覽:**

| 檔案 | 說明 | 工時 |
|------|------|------|
| [README.md](README.md) | 主要開發指南 (4-Phase 標準) | 參考用 |
| [QUICK_GUIDES.md](QUICK_GUIDES.md) | 本檔案 (快速導航) | 5 分鐘 |
| [OpenSpec_開發試驗版.md](OpenSpec_開發試驗版.md) | 快速試驗指南 | 20 分鐘 |
| [共同開發規範書_V1.md](共同開發規範書_V1.md) | 統一規範 | 參考用 |
| [f11_package/openspec/](f11_package/openspec/) | F11 規範文件 | 範本 |
| [f11_package/f11_openspec_dev.py](f11_package/f11_openspec_dev.py) | F11 代碼 (380 行) | 範本 |
| [f11_package/test_f11_openspec.py](f11_package/test_f11_openspec.py) | F11 測試 (21 個) | 範本 |

---

## 📌 如何使用本導航

1. **首次開發？** → 從上面「按用途分類」找相關指南
2. **找不到？** → 從「按開發階段分類」找
3. **還是困惑？** → 從「最常見的 5 個問題」找答案
4. **想快速學？** → 選一個「推薦學習路徑」

---

## 🚀 開始你的開發之旅

```bash
# 快速試驗？
# → 按照 OpenSpec_開發試驗版.md
# → 20 分鐘驗證想法

# 正式開發？
# → 複製 F11 完整範本
# → 按照 README.md 的 4-Phase
# → 4.5 小時完成開發

# 不確定？
# → 先做試驗版
# → 試完再決定是否投入完整版
```

---

**版本**: v1.0  
**創建日期**: 2025-12-17  
**用途**: OpenSpec 開發指南導航  
**適用對象**: 所有開發者（新手 → 進階）
