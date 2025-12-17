# 開發目錄說明 📚

> **OpenSpec 標準開發框架 v2.0** - F11 完整範本 ⭐

此目錄包含所有開發相關文件、設計規格、測試套件和開發版本模組。

---

## 📂 目錄結構

```
dev/
├── README.md                          # 本文件（開發說明）
├── 共同開發規範書_V1.md               # 通用開發規範 ⭐ 必讀
├── 自我改善機制設計_PDCA.md           # PDCA 持續改善流程
├── 團隊開發爬蟲的避雷指南.md          # 開發陷阱避免指南
│
├── f11_package/                       # F11 OpenSpec 標準範本 ⭐⭐⭐
│   ├── f11_openspec_dev.py           # 完整實現 (380 行，Selenium)
│   ├── test_f11_openspec.py          # 完整測試 (21 個測試，90%+ 覆蓋)
│   ├── openspec/                     # OpenSpec 文檔 (5 份)
│   │   ├── project.md                # 項目概述
│   │   └── changes/.../
│   │       ├── proposal.md           # 變更提案
│   │       ├── design.md             # 技術設計
│   │       ├── tasks.md              # 實現清單
│   │       └── specs/.../spec.md     # 功能規格
│   └── IMPLEMENTATION_REPORT.md       # 完整實現報告
│
├── f01_package/                       # F01 實現參考
├── f06_package/                       # F06 升級案例（Selenium 升級）
├── f02_package/ ... f07_package/      # 其他模組開發包
│
└── __pycache__/                       # Python 快取（自動生成）
```

---

## 🚀 快速開始（OpenSpec 4-Phase）

### 📚 必讀順序

1. **本文件** (5 分鐘) - 了解整體結構
2. **共同開發規範書_V1.md** (10 分鐘) - 核心規範
3. **[F11 完整範本](f11_package/)** ⭐ - 標準實現參考

### 🎯 新模組開發流程

```bash
# 1. 複製 F11 結構創建新模組
mkdir f02_package
# 複製：openspec/ 文件夾結構 + f11_openspec_dev.py 代碼框架

# 2. 編輯 openspec/ 文件（定義項目和規格）
# - openspec/project.md（項目概述）
# - openspec/changes/<change-id>/proposal.md（變更提案）
# - openspec/changes/<change-id>/design.md（技術設計）
# - openspec/changes/<change-id>/tasks.md（實現清單）
# - openspec/changes/<change-id>/specs/<capability>/spec.md（功能規格）

# 3. 驗證規範
openspec validate <change-id> --strict

# 4. 編輯 f02_openspec_dev.py（實現代碼）
# 5. 編輯 test_f02_openspec.py（編寫測試）

# 6. 執行測試
pytest test_f02_openspec.py -v

# 7. 部署至生產
copy f02_openspec_dev.py ..\modules\f02_fetcher.py
```

---

## 🏆 OpenSpec 4-Phase 標準

### Phase 1: 文檔化（1-2 小時）

在 `fXX_package/openspec/` 建立 5 份文檔：

```
openspec/
├── project.md                    # 項目概述
└── changes/<change-id>/
    ├── proposal.md              # 變更提案
    ├── design.md                # 技術設計
    ├── tasks.md                 # 實現清單 (15+ 項)
    └── specs/<capability>/
        └── spec.md              # 功能規格
```

**驗證命令：**

```bash
openspec validate <change-id> --strict  # 必須通過
```

### Phase 2: 代碼實現（1.5-2 小時）

**要求：**

- 380+ 行代碼
- 完整異常處理（5+ 種異常類型）
- 統一日誌記錄 ([FXX] 前綴)
- 標準輸出格式：`YYYY.MM.DD  FXX: [描述] : [數值] [來源]`

**代碼框架：**

```python
def fetch(date: str = None) -> str:
    """抓取指定日期的資料"""
    try:
        # 1. 驗證日期
        # 2. 發送請求/解析頁面
        # 3. 提取數據
        # 4. 返回成功格式
        return f"2025.12.17  FXX: [描述] : [數值] [來源]"
    except requests.Timeout:
        return "FXX 錯誤: 連線逾時 [來源]"
    except Exception as e:
        return f"FXX 錯誤: {str(e)} [來源]"

def main():
    """獨立測試用"""
    import sys
    test_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    print(fetch(test_date))

if __name__ == '__main__':
    main()
```

### Phase 3: 完整測試（1-1.5 小時）

**要求：**

- 15+ 個單元測試
- 90%+ 代碼覆蓋率
- 6 個測試分類（格式、提取、錯誤、邊界、日誌、整合）

**測試運行：**

```bash
pytest test_fXX_openspec.py -v --cov

# 預期結果：15+ passed in X.XXs ✅
```

### Phase 4: 部署上線（0.5 小時）

```bash
# 複製至生產
copy fXX_openspec_dev.py ..\modules\fXX_fetcher.py

# 驗證
python ..\run.py 2025-12-12 --module fXX_fetcher

# 歸檔
openspec archive <change-id> --yes
```

---

## 📊 統一文字格式

### 成功格式

```
YYYY.MM.DD  FXX: [描述] : [數值] [來源]

範例：
2025.12.17  F11: 加權股價收盤指數 : 27536.66 [TWSE]
```

### 失敗格式

```
FXX 錯誤: [訊息] [來源]

範例：
F11 錯誤: 該日無交易資料 [TWSE]
```

---

## 📚 參考實現

### ⭐ F11 (推薦 - 新開發者必讀)

**完整 OpenSpec 4-Phase 實現**

位置：[f11_package/](f11_package/)

**內容：**

- **文檔**：5 份 openspec 規格文件
- **代碼**：f11_openspec_dev.py (380 行，Selenium 動態頁面)
- **測試**：test_f11_openspec.py (21 個測試，90%+ 覆蓋)
- **狀態**：✅ 生產運行，實時驗證 27536.66

**閱讀順序：**

1. `f11_package/openspec/project.md` - 項目概述
2. `f11_package/openspec/changes/.../design.md` - 技術設計
3. `f11_package/f11_openspec_dev.py` - 代碼實現
4. `f11_package/test_f11_openspec.py` - 測試套件
5. `f11_package/IMPLEMENTATION_REPORT.md` - 完整報告

### F06 (升級案例 - Selenium 升級參考)

位置：[f06_package/](f06_package/)

- **升級**：v1.0 (靜態, NaN) → v1.1 (Selenium, 21.46) ✅
- **改進**：設計文件 + 升級日誌 + 部署報告
- **代碼**：f06_v11_openspec_dev.py (500 行)
- **測試**：test_f06_v11_openspec.py (19 個 Mock 測試)

### F01 (舊實現 - 參考用)

位置：[f01_package/](f01_package/)

- **版本**：v7.0 (生產)
- **測試**：41 個單元測試
- **狀態**：穩定運行

---

## 🔧 核心開發規範（4 點）

### 1️⃣ 回傳類型必須是 str

```python
def fetch(date: str) -> str:
    return "2025.12.17  F11: ... [TWSE]"  # ✅ 正確
```

### 2️⃣ 異常必須捕捉，不能拋出

```python
try:
    response = requests.get(url, timeout=30)
except requests.Timeout:
    return "FXX 錯誤: 連線逾時 [來源]"  # ✅ 轉為文字
```

### 3️⃣ 日期格式必須轉換

```python
# 輸入：2025-12-17 (YYYY-MM-DD)
# 輸出：2025.12.17 (YYYY.MM.DD)

date_formatted = date.replace("-", ".")
```

### 4️⃣ 日誌使用 [FXX] 前綴

```python
logger.info(f"[F11] {date} 開始抓取資料")
logger.error(f"[F11] {date} 異常: {error}")
```

---

## 💡 常見陷阱

| 陷阱 | 錯誤做法 | 正確做法 |
|------|---------|---------|
| 日期格式 | `2025-12-17` 輸出 | `2025.12.17` 輸出 |
| 異常處理 | 拋出異常 | 捕捉為文字 |
| 回傳類型 | 返回 dict/list | 返回 str |
| 日誌前綴 | `[F11]` 缺失 | `[F11]` 包含 |

---

## 📞 文件導覽

| 文件 | 說明 | 優先級 |
|------|------|--------|
| 共同開發規範書_V1.md | 統一規範 | ⭐⭐⭐ |
| f11_package/ | F11 完整範本 | ⭐⭐⭐ |
| 自我改善機制設計_PDCA.md | 持續改善流程 | ⭐⭐ |
| 團隊開發爬蟲的避雷指南.md | 開發陷阱指南 | ⭐⭐ |

---

**版本**: v2.0 (F11 標準)  
**狀態**: ✅ 生產就緒  
**最後更新**: 2025-12-17
