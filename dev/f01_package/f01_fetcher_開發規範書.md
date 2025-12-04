# f01_fetcher 開發規範書

> 📌 **請先閱讀**: [共同開發規範書](../共同開發規範書_V1.md)  
> 本文件只包含 f01 模組的專屬規範

**模組編號**: f01  
**模組名稱**: f01_fetcher  
**功能**: 抓取台指期貨外資的未平倉淨口數 (Open Interest)  
**資料來源**: 台灣期貨交易所 (TAIFEX)  
**難度**: ⭐⭐☆☆☆ (2/5)

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

## 🎯 目標欄位定義

### 表格中需要尋找的欄位

| 欄位類別 | 欄位路徑 | 說明 | 資料類型 |
|---------|---------|------|---------|
| 篩選條件 | 身份別 | 用於篩選外資行 | string |
| 目標資料 | 未平倉餘額 > 多方 > 口數 | 多方未平倉口數 | integer |
| 目標資料 | 未平倉餘額 > 空方 > 口數 | 空方未平倉口數 | integer |

### 回傳資料結構

```json
{
  "module": "f01",
  "date": "2025-12-01",
  "status": "success",
  "summary": "台指期外資淨額 -29,032 口（多方 18,268，空方 47,300）",
  "data": {
    "long_position": 18268,
    "short_position": 47300,
    "net_position": -29032
  },
  "source": "TAIFEX"
}
```

**data 欄位說明**:
- `long_position` (integer): 外資多方口數
- `short_position` (integer): 外資空方口數
- `net_position` (integer): 淨額 = 多方 - 空方

---

## 🔍 特殊處理邏輯

### 1. MultiIndex 表頭處理

TAIFEX 的表格使用多層表頭，欄位名稱是 tuple 格式：

```python
# 範例：實際的欄位名稱
('Unnamed: 2_level_0', '身份別')
('未平倉餘額', '多方', '口數')
('未平倉餘額', '空方', '口數')
```

**尋找欄位的建議方式**:

```python
def find_column_multiindex(df, keywords):
    """在 MultiIndex 中尋找包含特定關鍵字的欄位"""
    for col in df.columns:
        col_str = ''.join(str(c) for c in col)
        if all(keyword in col_str for keyword in keywords):
            return col
    return None

# 使用範例
trader_col = find_column_multiindex(df, ['身份別'])
long_col = find_column_multiindex(df, ['未平倉', '多方', '口'])
short_col = find_column_multiindex(df, ['未平倉', '空方', '口'])
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

| 測試日期 | 預期狀態 | 預期資料 | 備註 |
|---------|---------|---------|------|
| 2025-12-02 | success | long: 18808<br>short: 48032<br>net: -29224 | 正常交易日 |
| 2025-11-30 | failed | - | 週六，無交易 |
| 2025-11-28 | success | （實際資料） | 可用於開發測試 |

### 測試指令

```bash
# 獨立測試
python f01_fetcher_dev.py 2025-12-02
python f01_fetcher_dev.py 2025-11-30

# 整合測試
python run.py 2025-12-02 dev --module f01_fetcher_dev
```

---

##⚠️ 常見錯誤情況

| 情況 | 處理方式 | 錯誤訊息範例 |
|------|---------|-------------|
| 假日無資料 | status: "failed" | "該日無交易資料（可能是假日或休市日）" |
| 找不到身份別欄位 | status: "failed" | "找不到身份別欄位" |
| 找不到外資 | status: "failed" | "找不到外資資料，可用身份別: [...]" |
| 找不到未平倉欄位 | status: "failed" | "找不到未平倉餘額的多/空口數欄位" |
| 資料提取失敗 | status: "failed" | "資料提取失敗: [詳細錯誤]" |

---

## 💡 實作提示

### 建議的處理流程

```python
def fetch(date: str) -> dict:
    try:
        # 1. 驗證日期格式
        datetime.strptime(date, "%Y-%m-%d")
        
        # 2. 建立 URL 並發送請求
        url_date = date.replace('-', '/')
        url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={url_date}"
        response = requests.get(url, headers={'User-Agent': '...'}, timeout=30)
        response.encoding = "utf-8"
        
        # 3. 解析 HTML 表格
        tables = pd.read_html(response.text)
        if len(tables) == 0:
            return {"status": "failed", "error": "該日無交易資料"}
        
        df = tables[0]  # 通常第一個表格就是目標
        
        # 4. 處理 MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            return extract_foreign_data_multiindex(df, date)
        else:
            return extract_foreign_data_single(df, date)
            
    except requests.Timeout:
        return {"status": "error", "error": "連線逾時"}
    except Exception as e:
        return {"status": "error", "error": f"未預期的錯誤: {str(e)}"}
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

**最後更新**: 2025-12-04  
**版本**: 2.0（精簡版 - 配合共同規範書）