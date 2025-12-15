# f01_fetcher 開發規範書

> 📌 **請先閱讀**: [共同開發規範書](../共同開發規範書_V1.md)
> 本文件只包含 f01 模組的專屬規範

**模組編號**: f01
**模組名稱**: f01_fetcher
**功能**: 抓取台指期貨外資的未平倉淨口數 (Open Interest)
**資料來源**: 台灣期貨交易所 (TAIFEX)
**難度**: ⭐⭐☆☆☆ (2/5)
**最近更新**: v5.1 (2025-12-15) - 增強錯誤日誌功能

**⚠️ 重要限制**: 本模組使用的 API 端點無視日期參數，永遠回傳最後交易日資料

---

## 📊 資料來源

### API 端點
```
https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date=YYYY/MM/DD
```

### 資料特徵
- **格式**: HTML 表格
- **表頭結構**: MultiIndex（多層）
- **更新頻率**: 每個交易日
- **目標對象**: 「外資及陸資」或「外資」

---

## 🔧 資料來源技術說明

### 目前實作方式

**✅ 目前使用：網頁 HTML 解析（非官方 API）**

#### 技術細節

| 項目 | 說明 |
|------|------|
| **資料來源** | 期交所網頁查詢介面 |
| **URL** | `https://www.taifex.com.tw/cht/3/futContractsDate` |
| **方法** | HTTP GET 請求（使用 `requests` 套件） |
| **資料格式** | HTML 網頁（包含表格） |
| **解析工具** | `pandas.read_html()` + `BeautifulSoup`/`lxml` |
| **回傳內容** | 完整 HTML 網頁（約 474KB） |

#### 實作流程

```python
# 1. 發送 HTTP 請求
url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={url_date}"
response = requests.get(url, headers=headers, timeout=30)

# 2. 解析 HTML 表格
tables = pd.read_html(response.text)

# 3. 提取第一個表格
df = tables[0]

# 4. 根據表頭類型處理
if isinstance(df.columns, pd.MultiIndex):
    # MultiIndex 模式處理
else:
    # 單層表頭模式處理
```

### ⚠️ 已知限制：API 無視日期參數

**重要發現**：期交所的 `futContractsDate` 端點**無視日期參數**

#### 測試驗證結果

```bash
# 測試不同日期，回傳內容完全相同
測試日期: 2025-12-04 → 內容長度: 474,832 字元
測試日期: 2025-11-28 → 內容長度: 474,832 字元 (完全相同!)
測試日期: 2024-12-04 → 內容長度: 474,832 字元 (完全相同!)
```

**結論**：
- ❌ 無論傳入什麼日期參數，伺服器都回傳**最後交易日**的資料
- ✅ 這不是程式 bug，而是**資料來源的限制**
- ✅ 目前的實作已在程式碼第 11-18 行清楚記錄此限制

#### 為什麼會這樣？

期交所網頁實際上需要透過 **JavaScript 互動**才能查詢不同日期：

1. **網頁有日期選擇器**（jQuery datepicker）
2. **需要點擊查詢按鈕**（觸發 `gosubmit()` 函式）
3. **表單提交前會執行 JavaScript 驗證**
4. **單純的 HTTP GET 請求無法觸發這些互動**

結果：
- 使用 `requests` 抓取 → 只能拿到預設的最新資料
- URL 參數被伺服器忽略

---

## 🔄 兩種技術方案對比

### 方案 1: 目前方式（requests + HTML 解析）

#### 優點
- ⚡ **快速**：1-2 秒即可完成
- 💚 **資源消耗低**：不需啟動瀏覽器
- 📝 **程式碼簡單**：易於維護和除錯
- ✅ **穩定性高**：相依套件少（requests, pandas）

#### 缺點
- ❌ **無法查詢歷史日期**：永遠回傳最後交易日資料
- ⚠️ **依賴網頁結構**：網頁改版可能導致程式失效

#### 適用情境
✅ **只需要「最新交易日」資料的應用**
- 每日定時執行，抓取當天或前一交易日資料
- 即時監控外資動向
- 簡單的資料收集需求

---

### 方案 2: Selenium 版本（瀏覽器自動化）

#### 技術說明

**Selenium** = 瀏覽器自動化工具

```python
# Selenium 實作示意（偽代碼）
from selenium import webdriver
from selenium.webdriver.common.by import By

# 1. 啟動真實瀏覽器
driver = webdriver.Chrome()
driver.get('https://www.taifex.com.tw/cht/3/futContractsDate')

# 2. 找到日期輸入框並輸入
date_input = driver.find_element(By.ID, 'date_picker')
date_input.clear()
date_input.send_keys('2024/12/04')  # 可輸入任意歷史日期

# 3. 點擊查詢按鈕（觸發 JavaScript）
submit_btn = driver.find_element(By.ID, 'submit_btn')
submit_btn.click()

# 4. 等待頁面更新
driver.implicitly_wait(3)

# 5. 抓取結果（真正的歷史資料）
html = driver.page_source
tables = pd.read_html(html)
```

#### 優點
- ✅ **可查詢任意歷史日期**：真正解決日期參數問題
- ✅ **完整模擬瀏覽器**：可操作所有 JavaScript 功能
- ✅ **支援動態網頁**：等待資料載入

#### 缺點
- 🐢 **速度慢**：5-10 秒（需啟動瀏覽器）
- 🔴 **資源消耗高**：需要完整的瀏覽器執行環境
- 🛠️ **安裝複雜**：需要瀏覽器驅動（ChromeDriver, GeckoDriver）
- 🟡 **穩定性問題**：瀏覽器版本更新可能導致驅動不相容
- ⚠️ **依賴 UI 結構**：網頁 UI 改版可能導致元素定位失效

#### 適用情境
✅ **需要查詢「歷史特定日期」資料的應用**
- 回測分析（需要某個特定日期的資料）
- 歷史資料補齊
- 資料驗證和比對

---

### 📊 方案選擇建議

| 需求情境 | 建議方案 | 理由 |
|---------|---------|------|
| 每日定時抓取最新資料 | ✅ 方案 1 (requests) | 快速、穩定、資源消耗低 |
| 只需監控當前外資動向 | ✅ 方案 1 (requests) | 簡單易維護 |
| 需要回測特定日期資料 | ✅ 方案 2 (Selenium) | 能真正查詢歷史日期 |
| 需要補齊歷史資料庫 | ✅ 方案 2 (Selenium) | 可批次查詢多個歷史日期 |
| 資料驗證與比對 | ✅ 方案 2 (Selenium) | 需要精確的日期資料 |

---

### 💡 實務建議

**目前專案狀態**：
- ✅ 使用方案 1 (requests)
- ✅ 已在程式碼中清楚標註 API 限制
- ✅ 適合目前的使用情境（抓取最新資料）

**何時考慮升級到 Selenium**：
1. 明確需要查詢歷史特定日期資料
2. 需要建立完整的歷史資料庫
3. 需要驗證或比對過去某天的資料

**建議做法**：
- 📋 先評估實際業務需求
- 📋 如果只需最新資料 → 保持現狀
- 📋 如果確實需要歷史查詢 → 再投入資源升級

---

## 🎯 目標欄位定義

### 表格中需要尋找的欄位

| 欄位類別 | 欄位路徑 | 說明 | 資料類型 |
|---------|---------|------|---------|
| 篩選條件 | 身份別 | 用於篩選外資行 | string |
| 目標資料 | 未平倉餘額 > 多方 > 口數 | 多方未平倉口數 | integer |
| 目標資料 | 未平倉餘額 > 空方 > 口數 | 空方未平倉口數 | integer |

### 回傳資料格式（統一文字格式 v5.0）

**✅ 成功時**:
```
F01: 台指期貨外資 [未平倉] [多空淨額] : -29,439 口 [TAIFEX]
```

**❌ 失敗/錯誤時**:
```
F01 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]
F01 錯誤: 連線逾時，請檢查網路連線 [TAIFEX]
F01 錯誤: 日期格式錯誤，請使用 YYYY-MM-DD [TAIFEX]
```

**格式說明**:
- **成功格式**: `F01: 台指期貨外資 [未平倉] [多空淨額] : {net:,} 口 [TAIFEX]`
  - 模組代號: `F01` (大寫)
  - 標題: `台指期貨外資`
  - 標籤: `[未平倉] [多空淨額]`
  - 數值: 淨額口數，使用千分位逗號 (如 `-29,439`)
  - 來源: `[TAIFEX]`
- **錯誤格式**: `F01 錯誤: {錯誤訊息} [TAIFEX]`
  - 模組代號: `F01` (大寫)
  - 錯誤標記: `錯誤:`
  - 錯誤訊息: 中文說明
  - 來源: `[TAIFEX]`

**重要**:
- ✅ 回傳類型必須是 `str`
- ❌ 不再使用 `dict` 格式
- ✅ 錯誤時也必須回傳統一格式的文字
- ✅ 模組內部仍可使用 dict 處理邏輯，最後轉為文字即可

---

## 🔍 特殊處理邏輯

### 1. 雙模式表頭處理（MultiIndex 與單層）

**重要更新**: TAIFEX 的表格可能是 MultiIndex（多層）或單層表頭，必須兼容兩種格式！

#### MultiIndex 模式

表格使用多層表頭，欄位名稱是 tuple 格式：

```python
# 範例：實際的欄位名稱
('Unnamed: 2_level_0', '身份別')
('未平倉餘額', '多方', '口數')
('未平倉餘額', '空方', '口數')
```

**尋找欄位的方式**:

```python
def find_column_multiindex(df: pd.DataFrame, keywords: list) -> Optional[tuple]:
    """在 MultiIndex 中尋找包含特定關鍵字的欄位"""
    for col in df.columns:
        col_str = ''.join(str(c) for c in col)
        if all(keyword in col_str for keyword in keywords):
            return col
    return None

# 使用範例
trader_col = None
for col in df.columns:
    if any('身份別' in str(c) or '身份' in str(c) for c in col):
        trader_col = col
        break

long_col = find_column_multiindex(df, ['未平倉', '多方', '口'])
short_col = find_column_multiindex(df, ['未平倉', '空方', '口'])
```

#### 單層表頭模式

表格使用單層表頭，欄位名稱是字串：

```python
# 範例：可能的欄位名稱
'身份別'
'未平倉餘額-多方-口數'
'未平倉餘額-空方-口數'
```

**尋找欄位的方式**:

```python
def find_column_single(df: pd.DataFrame, possible_names: list) -> Optional[str]:
    """在單層欄位中尋找可能的欄位名稱"""
    for name in possible_names:
        if name in df.columns:
            return name
    return None

# 使用範例
trader_col = find_column_single(
    df,
    ['身份別', '身份', '交易人', '交易人名稱', '身分別']
)

long_col = find_column_single(
    df,
    ['未平倉餘額-多方-口數', '多方-口數', '多方口數', '多方', '多單口數']
)

short_col = find_column_single(
    df,
    ['未平倉餘額-空方-口數', '空方-口數', '空方口數', '空方', '空單口數']
)
```

#### 自動判斷模式

```python
# 根據表格類型處理
if isinstance(df.columns, pd.MultiIndex):
    logger.debug("偵測到 MultiIndex 表頭")
    return extract_foreign_data_multiindex(df, date)
else:
    logger.debug("偵測到單層表頭")
    return extract_foreign_data_single(df, date)
```

### 2. 身份別名稱

台指期的身份別通常顯示為 **「外資及陸資」**，而不是「外資」。

**建議處理方式**:

```python
# 優先找「外資及陸資」，找不到再試「外資」
foreign_rows = df[df[trader_col].isin(['外資及陸資', '外資'])]

if len(foreign_rows) == 0:
    # 找不到時，列出可用的身份別幫助除錯
    available = df[trader_col].unique().tolist()
    return {
        "module": "f01",
        "date": date,
        "status": "failed",
        "error": f"找不到外資資料，可用身份別: {available}"
    }
```

### 3. 數值格式轉換

從網頁抓取的數值可能包含千分位逗號，需要處理：

```python
def convert_to_int(value) -> int:
    """處理千分位逗號和空值"""
    if pd.isna(value):
        return 0
    try:
        return int(str(value).replace(',', '').strip())
    except (ValueError, AttributeError):
        return 0

# 使用範例
long_pos = convert_to_int(foreign_rows[long_col].values[0])
short_pos = convert_to_int(foreign_rows[short_col].values[0])
```

---

## 🧪 測試案例

### 必測日期

| 測試日期 | 預期狀態 | 預期輸出（v5.0 統一格式） | 備註 |
|---------|---------|---------|------|
| 2025-12-05 | success | `F01: 台指期貨外資 [未平倉] [多空淨額] : -26,823 口 [TAIFEX]` | 正常交易日 |
| 2025-11-30 | failed | `F01 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]` | 週六，無交易 |
| 2025-12-04 | success | `F01: 台指期貨外資 [未平倉] [多空淨額] : -26,823 口 [TAIFEX]` | 可用於開發測試 |
| 2025-13-01 | error | `F01 錯誤: 日期格式錯誤，請使用 YYYY-MM-DD [TAIFEX]` | 錯誤日期格式 |

### 測試指令

```bash
# 獨立測試
python f01_fetcher_dev.py 2025-12-02
python f01_fetcher_dev.py 2025-11-30

# 整合測試
python run.py 2025-12-02 dev --module f01_fetcher_dev
```

---

## ⚠️ 錯誤處理規範

### 必須處理的錯誤情況

| 情況 | 狀態碼 | 錯誤訊息範例 |
|------|--------|-------------|
| **網路錯誤** | error | |
| 連線逾時 | error | "連線逾時，請檢查網路連線" |
| HTTP 錯誤 | error | "HTTP 錯誤 404" |
| 網路請求失敗 | error | "網路請求失敗: [詳細錯誤]" |
| **資料格式錯誤** | failed | |
| 假日無資料 | failed | "該日無交易資料（可能是假日或休市日）" |
| 找不到身份別欄位 | failed | "找不到身份別欄位" |
| 找不到外資 | failed | "找不到外資資料，可用身份別: [...]" |
| 找不到未平倉欄位 | failed | "找不到未平倉餘額的多/空口數欄位" |
| 資料提取失敗 | failed | "資料提取失敗: [詳細錯誤]" |
| **參數錯誤** | error | |
| 日期格式錯誤 | error | "日期格式錯誤，請使用 YYYY-MM-DD" |
| HTML 解析失敗 | error | "HTML 解析失敗: [詳細錯誤]" |
| **未預期錯誤** | error | |
| 其他例外 | error | "未預期的錯誤: [詳細錯誤]" |

### 錯誤處理範例程式碼

```python
def fetch(date: str) -> dict:
    try:
        # 1. 驗證日期格式
        datetime.strptime(date, "%Y-%m-%d")

        # 2. 發送 HTTP 請求
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = "utf-8"

        # 3. 解析 HTML
        tables = pd.read_html(response.text)
        if len(tables) == 0:
            return {
                "module": MODULE_ID,
                "date": date,
                "status": "failed",
                "error": "該日無交易資料（可能是假日或休市日）"
            }

        # 4. 根據表頭類型處理
        df = tables[0]
        if isinstance(df.columns, pd.MultiIndex):
            return extract_foreign_data_multiindex(df, date)
        else:
            return extract_foreign_data_single(df, date)

    except ValueError:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": "日期格式錯誤，請使用 YYYY-MM-DD"
        }
    except requests.Timeout:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": "連線逾時，請檢查網路連線"
        }
    except requests.HTTPError as e:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": f"HTTP 錯誤 {e.response.status_code}"
        }
    except Exception as e:
        logger.exception("未預期的錯誤")
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": f"未預期的錯誤: {str(e)}"
        }
```

---

## 💡 實作提示

### 完整實作範例（文字格式）

```python
from typing import Dict, Optional

def format_f01_output(date: str, status: str, data: Optional[Dict] = None, error: Optional[str] = None) -> str:
    """格式化 F01 輸出為統一文字格式 v5.0"""
    if status == "success" and data:
        net = data.get("net_position", 0)
        source = data.get("source", "TAIFEX")
        # v5.0 成功格式：移除日期，保持簡潔
        return f"F01: 台指期貨外資 [未平倉] [多空淨額] : {net:,} 口 [{source}]"
    else:
        error_msg = error or "未知錯誤"
        # v5.0 錯誤格式：移除日期和中括號，統一簡潔風格
        return f"F01 錯誤: {error_msg} [TAIFEX]"


def fetch(date: str) -> str:
    """
    抓取指定日期的台指期貨外資未平倉資料

    Args:
        date: 日期字串 (YYYY-MM-DD)

    Returns:
        統一格式的文字字串
    """
    # 1. 驗證日期格式
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return format_f01_output(date, "error", error="日期格式錯誤，請使用 YYYY-MM-DD")

    # 2. 建立 URL 並發送請求
    url_date = date.replace('-', '/')
    url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={url_date}"

    try:
        logger.info(f"正在抓取 {date} 的資料...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = "utf-8"

        # 3. 解析 HTML
        tables = pd.read_html(response.text)
        if len(tables) == 0:
            return format_f01_output(date, "failed", error="該日無交易資料（可能是假日或休市日）")

        # 4. 根據表頭類型處理 (內部使用 dict)
        df = tables[0]
        if isinstance(df.columns, pd.MultiIndex):
            result_dict = extract_foreign_data_multiindex(df, date)
        else:
            result_dict = extract_foreign_data_single(df, date)

        # 5. 轉換為文字格式
        if result_dict.get("status") == "success":
            return format_f01_output(date, "success", data=result_dict.get("data"))
        else:
            return format_f01_output(date, "failed", error=result_dict.get("error", "未知錯誤"))

    except requests.Timeout:
        return format_f01_output(date, "error", error="連線逾時，請檢查網路連線")

    except requests.HTTPError as e:
        return format_f01_output(date, "error", error=f"HTTP 錯誤 {e.response.status_code}")

    except Exception as e:
        logger.exception("未預期的錯誤")
        return format_f01_output(date, "error", error=f"未預期的錯誤: {str(e)}")
```

**重點說明**:
- ✅ fetch() 回傳 `str` 而非 `dict`
- ✅ 新增 format_f01_output() 格式化函式
- ✅ 模組內部仍可用 dict 處理邏輯（extract_foreign_data_*）
- ✅ 最後統一轉換為文字格式
- ✅ 所有錯誤都回傳統一文字格式

### 建議的處理流程（舊版，保留參考）

```python
def fetch(date: str) -> dict:  # 舊版回傳 dict
    """
    抓取指定日期的台指期貨外資未平倉資料

    Args:
        date: 日期字串 (YYYY-MM-DD)

    Returns:
        結果字典，包含 module, date, status, summary/error, data 等欄位
    """
    # 1. 驗證日期格式
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": "日期格式錯誤，請使用 YYYY-MM-DD"
        }

    # 2. 建立 URL 並發送請求
    url_date = date.replace('-', '/')
    url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={url_date}"

    try:
        logger.info(f"正在抓取 {date} 的資料...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = "utf-8"

        # 3. 解析 HTML 表格
        tables = pd.read_html(response.text)
        if len(tables) == 0:
            return {
                "module": MODULE_ID,
                "date": date,
                "status": "failed",
                "error": "該日無交易資料（可能是假日或休市日）"
            }

        # 4. 取得第一個表格並根據表頭類型處理
        df = tables[0]

        if isinstance(df.columns, pd.MultiIndex):
            logger.debug("偵測到 MultiIndex 表頭")
            return extract_foreign_data_multiindex(df, date)
        else:
            logger.debug("偵測到單層表頭")
            return extract_foreign_data_single(df, date)

    except requests.Timeout:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": "連線逾時，請檢查網路連線"
        }

    except requests.HTTPError as e:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": f"HTTP 錯誤 {e.response.status_code}"
        }

    except requests.RequestException as e:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": f"網路請求失敗: {str(e)}"
        }

    except ValueError as e:
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": f"HTML 解析失敗: {str(e)}"
        }

    except Exception as e:
        logger.exception("未預期的錯誤")
        return {
            "module": MODULE_ID,
            "date": date,
            "status": "error",
            "error": f"未預期的錯誤: {str(e)}"
        }
```

### 除錯技巧

1. **印出欄位名稱**:
   ```python
   print("可用欄位:", df.columns.tolist())
   ```

2. **印出身份別列表**:
   ```python
   print("身份別:", df[trader_col].unique())
   ```

3. **檢查資料型別**:
   ```python
   print("表頭類型:", type(df.columns))
   ```

---

## 📝 完整範例

完整的參考實作請見: `modules/f01_fetcher.py`

---

## 📞 支援

遇到問題時：
1. 先檢查 [共同開發規範書](../共同開發規範書_V1.md)
2. 參考 `modules/f01_fetcher.py` 的實作
3. 使用瀏覽器 F12 檢查網頁實際結構

---

## 📝 版本更新記錄

### Version 5.2 (2025-12-07)
- ✅ 統一錯誤格式為 v5.0（移除日期欄位）
- ✅ 更新錯誤格式：`F01 錯誤: {訊息} [TAIFEX]`
- ✅ 更新所有範例程式碼與測試案例
- ✅ 同步 modules/f01_fetcher.py 實作
- ✅ 與開發專員工作記錄同步

### Version 5.1 (2025-12-07)
- ✅ 新增「資料來源技術說明」完整章節
- ✅ 新增「兩種技術方案對比」詳細說明
- ✅ 說明目前使用網頁 HTML 解析（非官方 API）
- ✅ 記錄 API 無視日期參數的測試驗證結果
- ✅ 說明 Selenium 版本的技術細節與適用情境
- ✅ 提供方案選擇建議與實務建議
- ✅ 與程式測試專員的測試報告同步

### Version 5.0 (2025-12-06)
- ✅ 更新為新的簡潔格式：`F01: 台指期貨外資 [未平倉] [多空淨額] : {net} 口 [TAIFEX]`
- ✅ 移除輸出中的日期和多空細節（簡化輸出）
- ✅ 保持錯誤格式不變（向後兼容）
- ✅ 更新 format_f01_output() 函式
- ✅ 與 modules/f01_fetcher.py 實作同步

### Version 4.0 (2025-12-05)
- ✅ 改為統一文字格式輸出
- ✅ fetch() 回傳 `str` 而非 `dict`
- ✅ 新增 format_f01_output() 格式化函式
- ✅ 更新所有範例程式碼
- ✅ 與實際實作完全同步

### Version 3.0 (2025-12-05)
- ✅ 更新為混合模式（英文 key + 中文訊息）
- ✅ 新增單層表頭支援（兼容 MultiIndex 和單層兩種格式）
- ✅ 完整的錯誤處理規範（error vs failed 區分）
- ✅ 新增完整的程式碼範例和錯誤處理流程
- ✅ 與實際 `modules/f01_fetcher.py` 實作完全同步

### Version 2.0 (2025-12-04)
- 精簡版 - 配合共同規範書

### Version 1.0
- 初始版本

---

## 🔄 變更記錄

### v5.1 (2025-12-15) - 增強錯誤日誌功能 ✨

**新增功能**：
- ✅ `format_f01_output()` 函式新增 `timestamp` 參數 - 捕獲錯誤發生時間
- ✅ `format_f01_output()` 函式新增 `context` 參數 - 傳遞錯誤上下文信息
- ✅ 錯誤訊息增強 - 顯示時間戳和上下文（如 timeout 值、HTTP 狀態碼）
- ✅ 日誌記錄升級 - 使用 `logger.error()` 和 `logger.warning()` 記錄詳細信息

**修改的異常處理**：
```python
# 之前 (v5.0)
F01 錯誤: 連線逾時，請檢查網路連線 [TAIFEX]

# 之後 (v5.1)
F01 錯誤: 連線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)
```

**測試覆蓋**：
- ✅ 向後兼容性測試（無新參數時仍可正常運作）
- ✅ 時間戳參數測試
- ✅ 上下文字典測試
- ✅ 組合參數測試
- 📝 文件位置：`dev/f01_package/test_error_logging.py`

**技術細節**：
- 使用 `datetime.now().strftime()` 捕獲當前時間戳
- Context 字典中的 `timeout` 自動格式化為 `timeout=30s`
- 其他 context 項目格式化為 `key=value`
- 完全向後兼容 - 新參數為可選

---

**最後更新**: 2025-12-15
**版本**: 5.1（增強錯誤日誌版本）
**狀態**: ✅ 實現完成、單元測試通過、集成測試驗證
