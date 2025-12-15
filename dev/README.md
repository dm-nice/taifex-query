# 開發目錄說明 📚

> **OpenSpec 實現框架 v7.0** - F01 模組完整升級，包含完善文檔、TypedDict 類型定義、統一日誌系統

此目錄包含所有開發相關的文件、規格書、測試套件和開發版本模組。

---

## 📂 目錄結構

```
dev/
├── README.md                          # 本文件（開發說明）
├── 共同開發規範書_V1.md               # 所有模組的通用開發規範 ⭐ 必讀
├── 自我改善機制設計_PDCA.md           # PDCA 持續改善流程
├── 團隊開發爬蟲的避雷指南.md          # 開發陷阱避免指南
├── _template.py                       # 新模組程式碼範本
├── _template_spec.md                  # 新模組規格書範本
│
├── f01_package/                       # F01 模組開發包（最佳實踐範例）
│   ├── f01_openspec_dev.py           # F01 OpenSpec 版本（v7.0 - 生產就緒）
│   ├── f01_fetcher_dev.py            # F01 開發版本
│   ├── design.md                      # F01 設計文檔
│   ├── tasks.md                       # F01 OpenSpec 任務清單
│   ├── test_f01_openspec.py           # F01 測試套件 (41 個測試)
│   └── README.md                      # F01 模組說明
│
├── f02_package/                       # F02 模組開發包
│   ├── f02_fetcher_dev.py
│   └── README.md
│
├── f03_package/ ... f07_package/      # F03 ~ F07 模組開發包
│
├── f06_package/                       # F06 模組開發包（波動率指數）⭐ 升級完成
│   ├── f06_v11_openspec_dev.py       # F06 v1.1 版本（Selenium - 開發版）
│   ├── test_f06_v11_openspec.py      # F06 v1.1 測試套件（19 個 Mock 測試）
│   ├── design.md                      # F06 設計文檔
│   ├── UPGRADE_LOG.md                 # v1.0 → v1.1 升級日誌
│   ├── DEPLOYMENT_REPORT_V11.md       # v1.1 部署報告
│   ├── explore_mis_structure.py       # MIS 頁面結構調查
│   ├── debug_pandas_columns.py        # pandas 欄位除錯
│   └── README.md                      # F06 模組說明
│
├── f11_package/                       # F11 模組開發包
│
├── f13_package/ ... f17_package/      # F13 ~ F17 模組開發包
│
└── __pycache__/                       # Python 快取目錄（自動生成）
```

---

## 🎯 快速開始指南

### 1️⃣ 對於新開發者（10分鐘快速入門）

**必讀文件順序：**

1. 📖 **本文件** (5 分鐘) - 了解整體結構
2. 📖 **共同開發規範書_V1.md** (5 分鐘) - 核心規範與「快速參考」章節
3. 💻 **參考 F01 範例** - 最完整的實作參考
   - 代碼：`f01_package/f01_openspec_dev.py`
   - 規格：`f01_package/design.md`

### 2️⃣ 對於新功能開發者

**工作流程：**

```bash
# 1. 複製範本建立新模組
cp _template.py       fXX_package/fxx_fetcher_dev.py
cp _template_spec.md  fXX_package/design.md

# 2. 編輯設計文檔（填寫需求）
code fXX_package/design.md

# 3. 實作代碼
code fXX_package/fxx_fetcher_dev.py

# 4. 測試（獨立測試）
python fXX_package/fxx_fetcher_dev.py 2025-12-12

# 5. 整合測試（通過 run.py）
python ../run.py 2025-12-12 dev --module fxx_fetcher_dev

# 6. 驗收通過後移至生產
copy fXX_package/fxx_fetcher_dev.py ../modules/fxx_fetcher.py
```

### 3️⃣ 對於 F01 模組維護者

**最新版本（v7.0）位置：**

- 生產版本：`../modules/f01_fetcher.py` ✅ 已部署
- 開發版本：`f01_package/f01_openspec_dev.py` (用於參考和測試)
- 完整測試：`f01_package/test_f01_openspec.py` (41 個測試)

**升級歷史：**

- v6.0 → v7.0: 添加完整文檔、TypedDict 定義、統一日誌系統

---

## 🏆 OpenSpec 實現框架（F01 範例）

F01 模組是使用 **OpenSpec 4 相位框架** 實現的完整範例：

### Phase 1: 文檔化 ✅

- **模組級文檔**：7 個部分（功能、入口、限制、依賴、版本、錯誤表、日誌）
- **函數文檔**：4,500+ 字的詳細 docstring
- **inline 註解**：4 個關鍵邏輯點的業務說明

**相關文件：**

- `f01_package/design.md` - 設計理由和架構
- `f01_package/tasks.md` - 16 個任務的完整清單

### Phase 2: 代碼改進 ✅

- **TypedDict 定義**：3 個類型 (ForeignDataDict, ErrorContextDict, FetchResultDict)
- **統一日誌**：[F01] 前綴 + 日期 + 時間戳上下文
- **異常處理**：5 種異常類型統一處理
- **PEP 8 遵循**：100% 合規

**改進項目：**

```python
# 類型定義 (phase 2)
class ForeignDataDict(TypedDict):
    net_position: int
    long_position: int
    short_position: int
    source: str

# 統一日誌 (phase 2)
logger.info(f"[F01] {date} 開始抓取資料")
```

### Phase 3: 測試 ✅

- **41 個測試全部通過** (100% 成功率)
  - 18 個單元測試 (convert_to_int, find_column, format_output)
  - 8 個異常測試 (timeout, HTTP error, network etc.)
  - 7 個邊界情況測試
  - 1 個 Dev vs Prod 一致性測試
  - 6 個部署驗證測試

**測試運行：**

```bash
cd f01_package
python -m pytest test_f01_openspec.py -v
```

### Phase 4: 部署 ✅

- **生產部署完成** (2025-12-15 13:45:09)
- **備份保留** (v6.0 保留以便回滾)
- **向後相容** (100% 驗證)
- **驗證測試** (6/6 通過)

**部署狀態：**

```
Location: ../modules/f01_fetcher.py
Version: v7.0
Status: ACTIVE (正式環境)
Backup: ../modules/f01_fetcher.py.backup.v6.0
```

---

## 🎯 OpenSpec 實現框架（F06 範例 - 升級完成）

F06 模組完成了 **OpenSpec 4 相位框架** 的首次升級：

**模組名稱：** 臺指選擇權波動率指數 (Taiwan Index Options Volatility Index)  
**版本歷程：** v1.0 (靜態, NaN) → **v1.1 (Selenium, 21.46)** ✅  
**當前數據源：** MIS VolatilityQuotes (<https://mis.taifex.com.tw/futures/VolatilityQuotes/>)  
**輸出格式：** `2025.12.15  F06: 臺指選擇權波動率指數 : 21.46 [TAIFEX]`

### 升級成果 (2025-12-15 22:20)

| 指標 | v1.0 | v1.1 | 改進 |
|------|------|------|------|
| **資料品質** | NaN (無數據) | 21.46 (實時) | ✅ 解決 |
| **抓取方式** | HTTP + 靜態 | Selenium + 動態 | ✅ 增強 |
| **測試覆蓋** | 34 個測試 | 19 個 Mock 測試 | ✅ 重構 |
| **部署狀態** | 有數據問題 | ✅ 生產運作 | ✅ 上線 |
| **性能** | <2 秒 | ~20 秒 | ⚠️ 但換取正確性 |

### Phase 1: 文檔化 ✅

- **設計規格**：design.md (241 行) + UPGRADE_LOG.md
  - 完整的模組目標、兩個數據源對比、輸出格式規範
  - 異常處理策略（5 種異常類型）
  - 升級路線圖 (v1.1 新增)

### Phase 2: 代碼實現 ✅

- **f06_v11_openspec_dev.py**：500 行生產就緒代碼
  - **Selenium 自動化**：Chrome WebDriver 管理
  - **免責聲明自動點擊**：解決 TAIFEX MIS 訪問限制
  - **動態 HTML 解析**：支援 JavaScript 渲染內容
  - **表格多欄位支援**：7 種欄位名稱變異
  - **完整異常處理**：5+ 種異常類型

**代碼亮點：**

```python
# 免責聲明自動處理
disclaimer_button = WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '接受')]"))
)
disclaimer_button.click()

# 多欄位支援
possible_names = [
    '目前指數',  # MIS 主欄位 ⭐
    '臺指選擇權波動率指數',
    '波動率指數',
    'VIX指數', 'VIX', '波動率', 'Volatility Index', 'VIX Close'
]

# pandas 表格解析
tables = pd.read_html(page_html)
for df in tables:
    for name in possible_names:
        if name in df.columns:
            value = float(df[name].iloc[0])
            return {"status": "success", "data": {"vix_value": value}}
```

### Phase 3: 測試 ✅

**v1.1 測試套件** (test_f06_v11_openspec.py)

- **19 個 Mock 測試全部通過** (100% 成功率)
  - TestFormatOutput: 5 個測試
  - TestExtractVIXValue: 4 個測試  
  - TestSeleniumIntegration: 3 個 Mock Selenium 測試
  - TestEdgeCases: 3 個邊界情況測試
  - TestOutputFormat: 2 個格式驗證測試
  - TestDateValidation: 2 個日期驗證測試

**測試運行：**

```bash
cd f06_package
python -m pytest test_f06_v11_openspec.py -v
# 結果: 19 passed in 94.86s ✅
```

### Phase 4: 部署 ✅

**部署時間線：**

```
22:15 | 問題識別 (v1.0 返回 NaN)
22:16 | 升級決策 (選擇 Selenium 方案)
22:18 | v1.1 代碼完成 + 測試完成
22:19 | 核心問題解決 (欄位名稱調整)
22:20 | 生產部署 (複製至 modules/f06_fetcher.py)
22:22 | 生產驗證通過 (實時 VIX: 21.46)
```

**部署狀態：**

```
Location: ../modules/f06_fetcher.py
Version: v1.1 (Selenium)
Status: ✅ ACTIVE (生產環境運行中)
Backup: ../modules/f06_fetcher.py.backup.v1.0
Tests: 19/19 通過 (100%)
```

**升級詳情參考：**

- 🔄 升級日誌: `f06_package/UPGRADE_LOG.md`
- 📊 部署報告: `f06_package/DEPLOYMENT_REPORT_V11.md`
- 🧪 測試套件: `f06_package/test_f06_v11_openspec.py`
  - **HTML 表格解析**：支援 MultiIndex 和單層表頭
  - **統一日誌**：[F06] 前綴 + 日期 + 時間戳

**關鍵特性：**

```python
# 提取 VIX 數據
def extract_vix_value(df, date) -> dict:
    # 嘗試 7 種可能的欄位名稱
    # 支援 MultiIndex 複雜表頭
    # 返回 VIXDataDict 或 error dict

# 統一輸出格式
def format_f06_output(date, status, data) -> str:
    # 成功: "2025.12.15  F06: 臺指選擇權波動率指數 : 18.50 [TAIFEX]"
    # 失敗: "F06 錯誤: ..."
    # 異常: "F06 錯誤: ... (YYYY-MM-DD HH:MM:SS, context)"
```

### Phase 3: 測試 ✅

- **34 個測試全部通過** (100% 成功率)
  - 7 個單元測試 (格式化輸出)
  - 5 個單元測試 (數據提取)
  - 7 個異常測試 (date format, timeout, HTTP 4xx/5xx, network error)
  - 8 個邊界情況測試 (empty string, spaces, invalid dates)
  - 5 個集成測試 (complete fetch workflow)
  - 3 個輸出格式驗證
  - 4 個日期驗證測試

**測試運行：**

```bash
cd f06_package
python -m pytest test_f06_openspec.py -v
# 或
python test_f06_openspec.py
```

**測試覆蓋：**

- ✅ 日期格式驗證和轉換
- ✅ HTML 表格解析（單層和 MultiIndex）
- ✅ VIX 數據提取（7 種欄位名稱變體）
- ✅ 輸出格式化（成功、失敗、異常）
- ✅ 精度控制（2 位小數）
- ✅ 所有異常情況

### Phase 4: 部署 ✅

- **生產部署完成** (2025-12-15 21:47:42)
- **驗證測試** (模組導入成功、fetch 返回有效格式、main() 正常運作)
- **無備份** (首次部署)

**部署狀態：**

```
Location: ../modules/f06_fetcher.py
Version: v1.0
Status: ACTIVE (正式環境)
Deployment Time: 2025-12-15 21:47:42
Source: f06_package/f06_openspec_dev.py
```

---

## 📊 統一文字格式標準 v7.0

所有模組必須遵循的輸出格式規範：

### 成功情況

**格式：** `YYYY.MM.DD  FXX: [描述] [內容] : [數據] [單位] [TAIFEX]`

**F01 範例：**

```
2025.12.15  F01: 台指期貨外資 [未平倉] [多空淨額] : -29,032 口 [TAIFEX]
```

### 失敗情況

**格式：** `F01 錯誤: [錯誤訊息] [TAIFEX]`

**範例：**

```
F01 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]
```

### 異常情況（附帶時間戳和上下文）

**格式：** `F01 錯誤: [訊息] [TAIFEX] (YYYY-MM-DD HH:MM:SS, [上下文])`

**範例：**

```
F01 錯誤: 連線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)
F01 錯誤: HTTP 錯誤 404 [TAIFEX] (2025-12-15 14:30:45, status_code=404)
```

---

## 🔧 開發規範（核心 4 點）

### 1️⃣ 回傳類型

```python
def fetch(date: str) -> str:  # ✅ 必須是 str，不能是 dict
    return "2025.12.15  F01: ..."  # ✅ 統一文字格式
```

### 2️⃣ 異常處理

```python
def fetch(date: str) -> str:
    try:
        # ... 實現邏輯
    except requests.Timeout:
        return "F01 錯誤: 連線逾時 [TAIFEX]"  # ✅ 轉為文字，不拋出
    except Exception as e:
        return f"F01 錯誤: {str(e)} [TAIFEX]"  # ✅ 捕捉所有異常
```

### 3️⃣ 日期格式轉換

```python
# 輸入：YYYY-MM-DD (例: 2025-12-15)
# 輸出：YYYY.MM.DD (例: 2025.12.15)

date_formatted = date.replace("-", ".")  # ✅ 正確方式
return f"{date_formatted}  F01: ..."
```

### 4️⃣ 日誌記錄

```python
import logging
logger = logging.getLogger(__name__)

# ✅ 使用 [FXX] 前綴便於日誌過濾
logger.info(f"[F01] {date} 開始抓取資料")
logger.error(f"[F01] {date} 異常: {error}")
```

---

## 📋 開發工作流完整步驟

### 第一步：初始化新模組

```bash
# 建立模組目錄
mkdir dev\fXX_package
cd dev\fXX_package

# 複製並重命名範本
copy ..\\_template.py fxx_fetcher_dev.py
copy ..\\_template_spec.md design.md
```

### 第二步：撰寫設計文檔

編輯 `design.md`，包含：

- **目標**：模組要解決什麼問題
- **資料來源**：URL、API 端點
- **字段定義**：需抓取的字段及說明
- **測試案例**：3 種情況測試日期

```markdown
# FXX 模組設計

## 目標
抓取 [數據源] 的 [特定數據]

## 資料來源
URL: https://...

## 字段定義
| 字段 | 說明 | 來源 |
|------|------|------|
| ... | ... | ... |

## 測試案例
1. 正常日期 (2025-12-12)
2. 假日 (2025-12-14)
3. 邊界情況 (...)
```

### 第三步：實作代碼

編輯 `fxx_fetcher_dev.py`：

```python
"""
FXX 模組：[簡單說明]

【功能】抓取 [數據描述]
【入口】fetch(date: str) -> str
【限制】[任何限制說明]
"""

from datetime import datetime
import requests
import logging

logger = logging.getLogger(__name__)
SOURCE = "[資料來源名稱]"

def fetch(date: str) -> str:
    """
    抓取指定日期的資料
    
    Args:
        date (str): YYYY-MM-DD 格式的日期
        
    Returns:
        str: 統一格式文字字串
    """
    # 1. 驗證日期格式
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return f"FXX 錯誤: 日期格式錯誤，請使用 YYYY-MM-DD [{SOURCE}]"
    
    # 2. 轉換日期格式
    date_formatted = date.replace("-", ".")
    
    try:
        # 3. 發送請求
        logger.info(f"[FXX] {date} 開始抓取資料")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 4. 解析和處理
        data = parse_response(response)
        
        # 5. 返回成功結果
        logger.info(f"[FXX] {date} 抓取成功")
        return f"{date_formatted}  FXX: [描述] {data} [{SOURCE}]"
        
    except requests.Timeout:
        return f"FXX 錯誤: 連線逾時，請檢查網路連線 [{SOURCE}]"
    except Exception as e:
        logger.error(f"[FXX] {date} 異常: {str(e)}")
        return f"FXX 錯誤: {str(e)} [{SOURCE}]"

def main():
    """獨立測試用"""
    import sys
    test_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    result = fetch(test_date)
    print(result)

if __name__ == '__main__':
    main()
```

### 第四步：測試

```bash
# 測試 1: 不提供參數（使用當前日期）
python fxx_fetcher_dev.py

# 測試 2: 指定正常交易日
python fxx_fetcher_dev.py 2025-12-12

# 測試 3: 指定假日
python fxx_fetcher_dev.py 2025-12-13

# 測試 4: 指定錯誤格式
python fxx_fetcher_dev.py 2025-12/13

# 測試 5: 通過 run.py 整合測試
cd ..
python ../run.py 2025-12-12 dev --module fxx_fetcher_dev
```

### 第五步：驗收和部署

```bash
# 驗收通過後，將開發版本移至生產目錄
copy fxx_package\fxx_fetcher_dev.py ..\modules\fxx_fetcher.py

# 驗證部署成功
python ..\modules\fxx_fetcher.py 2025-12-12
```

---

## 🧪 F01 模組測試套件

### 運行測試

```bash
cd f01_package

# 運行全部測試
python -m pytest test_f01_openspec.py -v

# 運行特定測試類
python -m pytest test_f01_openspec.py::TestConvertToInt -v

# 運行特定測試用例
python -m pytest test_f01_openspec.py::TestConvertToInt::test_convert_with_comma -v
```

### 測試覆蓋

| 類別 | 測試數 | 說明 |
|------|--------|------|
| TestConvertToInt | 6 | 字串轉整數，處理千分位逗號 |
| TestFindColumn | 4 | 表頭搜尋 (MultiIndex + 單層) |
| TestFormatOutput | 4 | 輸出格式化 (成功/失敗/異常) |
| TestExceptionHandling | 8 | 異常處理 (5 種異常類型) |
| TestEdgeCases | 7 | 邊界情況 (空值、無效日期等) |
| test_compare_with_prod | 1 | Dev vs Prod 一致性 |
| (Post-deployment) | 6 | 部署驗證測試 |
| **合計** | **41** | **100% 通過** |

---

## 📚 相關檔案導覽

### 設計和規範文檔

| 文件 | 說明 | 優先級 |
|------|------|--------|
| 共同開發規範書_V1.md | 所有模組的統一規範 | ⭐⭐⭐ 必讀 |
| 自我改善機制設計_PDCA.md | PDCA 持續改善流程 | ⭐⭐ 參考 |
| 團隊開發爬蟲的避雷指南.md | 常見陷阱和解決方案 | ⭐⭐ 推薦 |

### F01 模組文檔

| 文件 | 說明 | 大小 |
|------|------|------|
| f01_package/design.md | F01 設計與架構 | ~350 行 |
| f01_package/tasks.md | F01 OpenSpec 16 項任務 | ~1165 行 |
| f01_package/test_f01_openspec.py | F01 完整測試套件 | ~500 行 |
| f01_package/f01_openspec_dev.py | F01 生產就緒版本 | ~954 行 |

### 專案根目錄

| 文件 | 說明 |
|------|------|
| ../README.md | 專案概覽 |
| ../run.py | 模組執行框架 |
| ../modules/f01_fetcher.py | F01 生產版本 (v7.0) |

---

## ⚠️ 常見陷阱與解決方案

### ❌ 陷阱 1: 回傳 dict 而不是 str

```python
# 錯誤 ❌
def fetch(date: str) -> dict:
    return {"status": "success", "data": {...}}

# 正確 ✅
def fetch(date: str) -> str:
    return "2025.12.15  F01: 台指期貨外資... [TAIFEX]"
```

### ❌ 陷阱 2: 日期格式不轉換

```python
# 錯誤 ❌
return f"[ 2025-12-15  F01... ]"  # 輸入格式，用 "-"

# 正確 ✅
date_formatted = date.replace("-", ".")
return f"2025.12.15  F01: ...  [TAIFEX]"  # 輸出格式，用 "."
```

### ❌ 陷阱 3: 未捕捉所有異常

```python
# 錯誤 ❌
def fetch(date: str) -> str:
    response = requests.get(url)  # 可能拋出異常
    return "..."

# 正確 ✅
def fetch(date: str) -> str:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return "..."
    except requests.Timeout:
        return "F01 錯誤: 連線逾時 [TAIFEX]"
    except Exception as e:
        return f"F01 錯誤: {str(e)} [TAIFEX]"
```

### ❌ 陷阱 4: 日期預設值使用硬編碼

```python
# 錯誤 ❌ (2025-12-15 時顯示舊日期)
def main():
    test_date = '2025-11-28'  # 硬編碼，容易過時
    fetch(test_date)

# 正確 ✅
def main():
    test_date = datetime.now().strftime("%Y-%m-%d")  # 動態日期
    fetch(test_date)
```

---

## 🔄 更新日誌

### v7.0 (2025-12-15) ✅ 最新

- ✨ 完全 OpenSpec 實現
- 📚 4,500+ 字詳細文檔
- 🔑 TypedDict 類型定義
- 📊 41 個測試 (100% 通過)
- 🚀 已部署至生產環境

### v6.0 (2025-12-12)

- 基礎實現
- 備份保留 (f01_fetcher.py.backup.v6.0)

### v5.0 及更早版本

- 舊版架構（不推薦參考）

---

## 💡 快速參考

### 常用命令

```bash
# 測試單個模組（開發版本）
python dev/fxx_package/fxx_fetcher_dev.py 2025-12-12

# 通過 run.py 測試（驗收模式）
python run.py 2025-12-12 dev --module fxx_fetcher_dev

# 運行生產版本
python modules/fxx_fetcher.py 2025-12-12

# 查看輸出
type data/2025-12-12_HHMM_fxx_fetcher.txt
```

### 重要路徑

```
c:\Taifex\
├── dev\               # 開發目錄（本文件位置）
│  └── f01_package\
│     └── f01_openspec_dev.py   # F01 v7.0 參考版本
├── modules\           # 生產目錄
│  └── f01_fetcher.py           # F01 v7.0 生產版本
├── data\              # 輸出目錄
└── run.py             # 執行框架
```

---

## 🎓 學習路徑

### 初學者（第一週）

1. 讀本文件 (30 分鐘)
2. 讀共同開發規範書 (30 分鐘)
3. 研究 F01 代碼 (2 小時)
4. 試寫簡單模組 (4 小時)

### 進階開發者（持續）

1. 參考 F01 OpenSpec 實現 (2 小時)
2. 學習 TypedDict 應用 (1 小時)
3. 應用到自己的模組 (4 小時)

### 專家級（回顧和優化）

1. 複習 OpenSpec 4 相位 (1 小時)
2. 優化既有模組 (按需)
3. 指導新開發者 (持續)

---

## 📞 協助與支持

- **文檔查詢**：參考相應的 `.md` 文件
- **代碼範例**：查看 `f01_package/f01_openspec_dev.py`
- **測試參考**：查看 `f01_package/test_f01_openspec.py`
- **常見問題**：見「常見陷阱與解決方案」章節

---

**版本**: v7.0 OpenSpec  
**最後更新**: 2025-12-15  
**狀態**: ✅ 生產就緒  
**測試覆蓋**: 41/41 (100%)  
**部署狀態**: F01 已上線，其他模組開發中
