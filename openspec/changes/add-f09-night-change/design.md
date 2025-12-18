# Technical Design: F09 台指期貨夜盤漲跌點數

## Context

### 背景

TAIFEX 盤後交易時段表格包含「漲跌點數」欄位，顯示夜盤相對於日盤收盤價的變化。

- F08 已實現夜盤收盤價抓取
- F09 將抓取同一表格的「漲跌點數」欄位

### 資料源分析

**TAIFEX 期貨每日交易行情（盤後交易時段）**
- URL: https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryType=2
- 相關欄位：
  - 「最後成交價」（F08 使用）
  - 「漲跌點數」或「漲跌」（F09 使用）
  - 「結算價」（備用）

---

## Goals / Non-Goals

### Goals

- ✅ 抓取 TX 近月合約夜盤漲跌點數
- ✅ 正負號顯示（+108 或 -52）
- ✅ 支援歷史日期查詢
- ✅ 與 F08 共用代碼結構

### Non-Goals

- ❌ 不計算價差（TAIFEX 已提供漲跌欄位）
- ❌ 不抓取日盤資料
- ❌ 不抓取其他期貨商品

---

## Decisions

### Decision 1: 直接使用 TAIFEX 提供的漲跌欄位

**選擇**: 讀取表格中的「漲跌點數」或「漲跌」欄位

**理由**:
- TAIFEX 已計算好漲跌值，無需自行計算
- 避免 F04 與 F08 數據不同步的問題
- 簡化代碼邏輯

**替代方案**:
- ❌ 計算差值 (F08 - F04): 需要同時抓取兩個模組，增加複雜度

---

### Decision 2: 正負號顯示

**選擇**: 保留原始正負號，統一格式為 `+108` 或 `-52`

**格式規範**:
```python
# 正數：明確顯示 +
if change > 0:
    change_str = f"+{change:,.0f}"
# 負數：保留 - 號
elif change < 0:
    change_str = f"{change:,.0f}"  # 自動包含負號
# 零：顯示 0
else:
    change_str = "0"
```

---

### Decision 3: 複製 F08 代碼結構

**選擇**: 複製 F08 的完整框架，僅修改欄位名稱和輸出文字

**模組化設計**:

```python
# F09 特有部分
MODULE_ID = "f09"
MODULE_NAME = "f09_fetcher"

def extract_change_points(df: pd.DataFrame, date: str) -> Dict:
    # 查找「漲跌點數」或「漲跌」欄位
    change_col = find_column(df, ['漲跌點數', '漲跌', 'Change'])

    # 提取數值
    change_value = convert_to_number(target_row[change_col])

    # 格式化正負號
    if change_value > 0:
        change_str = f"+{change_value:,.0f}"
    elif change_value < 0:
        change_str = f"{change_value:,.0f}"
    else:
        change_str = "0"
```

---

## Data Flow

### 完整流程

```
1. 使用者呼叫 fetch("2025-12-18")
   ↓
2. 驗證日期格式 (YYYY-MM-DD)
   ↓
3. 轉換為 TAIFEX 格式 (2025/12/18)
   ↓
4. 構建 URL (加入 queryType=2)
   ↓
5. 發送 HTTP GET 請求 (timeout=30)
   ↓
6. pandas.read_html 解析 HTML 表格
   ↓
7. 篩選 TX 合約行（近月）
   ↓
8. 提取「漲跌點數」欄位
   ↓
9. 格式化正負號 (+108 / -52)
   ↓
10. 返回文字結果
```

---

## API Specification

### 函式簽名

```python
def fetch(date: str) -> str:
    """
    抓取指定日期的台指期貨夜盤漲跌點數

    Args:
        date: 日期字串 (YYYY-MM-DD)

    Returns:
        成功: "2025.12.18  F09: 台指期貨夜盤漲跌點數 : +108 點  [https://...]"
        失敗: "2025.12.18  F09 錯誤: 錯誤訊息 [https://...]"
    """
```

### 輸出格式規範

**成功格式** (正數):
```
2025.12.18  F09: 台指期貨夜盤漲跌點數 : +108 點  [https://www.taifex.com.tw/cht/3/futDailyMarketReport]
```

**成功格式** (負數):
```
2025.12.18  F09: 台指期貨夜盤漲跌點數 : -52 點  [https://www.taifex.com.tw/cht/3/futDailyMarketReport]
```

**成功格式** (零):
```
2025.12.18  F09: 台指期貨夜盤漲跌點數 : 0 點  [https://www.taifex.com.tw/cht/3/futDailyMarketReport]
```

**失敗格式**:
```
2025.12.18  F09 錯誤: 連線逾時 [https://www.taifex.com.tw/cht/3/futDailyMarketReport]
```

---

## Testing Strategy

### 測試覆蓋（簡化版）

由於 F09 與 F08 高度相似，測試套件簡化為：

1. **格式驗證** (3 個)
   - 正數格式 (+108)
   - 負數格式 (-52)
   - 零值格式 (0)

2. **資料提取** (2 個)
   - 正常漲跌提取
   - 欄位名變異處理

3. **異常處理** (3 個)
   - Timeout
   - 空表格
   - 找不到 TX

4. **集成測試** (2 個)
   - 模組匯入
   - 函式簽名

**總計**: 10 個測試（相比 F08 的 21 個簡化）

---

## Risks / Trade-offs

### Risk 1: 欄位名稱不確定

**風險**: TAIFEX 可能使用「漲跌」、「漲跌點數」或其他名稱

**緩解**:
```python
find_column(df, ['漲跌點數', '漲跌', 'Change', '漲跌 (點)'])
```

---

### Risk 2: 零值處理

**風險**: 夜盤與日盤價格相同時，漲跌為 0

**處理**: 顯示 "0 點"（不加正負號）

---

## Implementation Notes

### 與 F08 的差異

| 項目 | F08 (夜盤收盤價) | F09 (夜盤漲跌) |
|------|----------------|---------------|
| 欄位名稱 | 「最後成交價」 | 「漲跌點數」 |
| 數值格式 | `27,483.0` | `+108` / `-52` |
| 正負號 | 無 | 必須顯示 |
| 單位 | 無 | `點` |

### 代碼重用

```python
# 與 F08 共用
- convert_to_number()
- find_column()
- HTTP 請求邏輯
- 異常處理

# F09 特有
- extract_change_points()  # 提取漲跌邏輯
- format_change_str()      # 正負號格式化
```

---

## Migration Plan

### 部署步驟

```bash
# Phase 1: 開發 (1 小時)
1. 複製 F08 代碼為基礎
2. 修改欄位名稱為「漲跌點數」
3. 添加正負號格式化邏輯
4. 本地驗證

# Phase 2: 測試 (0.5 小時)
5. 編寫 10 個測試
6. 執行 pytest

# Phase 3: 部署 (0.5 小時)
7. 複製到 modules/f09_fetcher.py
8. 執行 run.py 驗證
9. 檢查輸出檔案
```

---

## Validation Example

### 預期數據 (2025-12-17)

根據已知數據：
- F04 (日盤收盤): 27,591.0
- F08 (夜盤收盤): 27,483.0
- **F09 (夜盤漲跌): -108 點**

**驗證公式**:
```
F09 = F08 - F04
-108 = 27,483.0 - 27,591.0 ✅
```

---

## References

- F08 實現: `dev/f08_package/f08_openspec_dev.py`
- F04 實現: `modules/f04_fetcher.py`
- TAIFEX 資料源: https://www.taifex.com.tw/cht/3/futDailyMarketReport?queryType=2

---

**版本**: v1.0
**作者**: AI Assistant
**日期**: 2025-12-18
**狀態**: Proposed
