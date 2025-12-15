# F01 Development Version 規格書（簡化版）

**版本**: v6.0 (Dev)
**狀態**: ✅ Production Ready
**最後更新**: 2025-12-15

> 📌 **快速參考**: 本文件為精簡版規格書 (~150 行)
> 📖 **完整版**: 請參閱 [f01_fetcher_dev_spec.md](f01_fetcher_dev_spec.md)

---

## 📋 模塊概況

| 項目 | 內容 |
|------|------|
| **模塊編號** | F01 |
| **功能** | 抓取台指期貨外資未平倉淨口數 |
| **資料來源** | TAIFEX (台灣期貨交易所) |
| **難度** | ⭐⭐☆☆☆ (2/5) |

### ⚠️ 重要限制
```
API 端點無視日期參數，永遠返回最後交易日資料
若需查詢歷史日期，需使用 Selenium 瀏覽器自動化
```

---

## 🔧 技術架構

### 核心函式
```python
def fetch(date: str) -> str
    """主要入口函式，返回統一格式文字"""

def format_f01_output(..., timestamp=None, context=None) -> str
    """格式化輸出（v6.0 增強錯誤日誌）"""

def extract_foreign_data_multiindex(df, date) -> Dict
    """從 MultiIndex 表格提取資料"""

def extract_foreign_data_single(df, date) -> Dict
    """從單層表頭提取資料"""

def convert_to_int(value) -> int
    """安全的字串轉整數（處理千分位）"""
```

### 依賴套件
```
requests>=2.0.0      # HTTP 請求
pandas>=1.0.0        # 表格解析
lxml>=4.0.0          # HTML 解析
```

---

## 📤 輸出格式

### 成功輸出
```
2025.12.04  F01: 台指期貨外資 [未平倉] [多空淨額] : -29,032 口 [TAIFEX]
```

### 錯誤輸出（基本）
```
F01 錯誤: 連線逾時，請檢查網路連線 [TAIFEX]
```

### 錯誤輸出（增強 - v6.0）
```
F01 錯誤: 連線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)
F01 錯誤: HTTP 錯誤 500 [TAIFEX] (2025-12-15 14:32:10, status_code=500)
```

---

## 🌐 API 端點

### URL
```
https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date=YYYY/MM/DD
```

### 參數
| 參數 | 值 | 說明 |
|------|-----|------|
| queryType | 1 | 查詢類型 |
| marketCode | 0 | 市場代碼（期貨） |
| date | YYYY/MM/DD | 查詢日期 ⚠️ 參數無效 |

---

## ⚠️ 錯誤處理

### 異常類型（5 層處理）
```python
# 1. 日期格式錯誤
ValueError → "日期格式錯誤，請使用 YYYY-MM-DD"

# 2. 網路超時
requests.Timeout → "連線逾時，請檢查網路連線" + (timestamp, timeout=30s)

# 3. HTTP 錯誤
requests.HTTPError → "HTTP 錯誤 {code}" + (timestamp, status_code=xxx)

# 4. 請求失敗
requests.RequestException → "網路請求失敗: {error}"

# 5. HTML 解析失敗
ValueError → "HTML 解析失敗: {error}"
```

### 資料異常
```python
# 無交易資料
len(tables) == 0 → "該日無交易資料（可能是假日或休市日）"

# 找不到外資
找不到外資列 → "找不到外資資料，可用身份別: [...]"
```

---

## 💡 使用指南

### 基本用法
```python
from f01_fetcher_dev import fetch

# 抓取資料
result = fetch('2025-12-04')
print(result)

# 輸出: 2025.12.04  F01: 台指期貨外資 [未平倉] [多空淨額] : -29,032 口 [TAIFEX]
```

### 錯誤處理
```python
result = fetch('2025-12-04')

if "錯誤:" in result:
    print(f"失敗: {result}")
else:
    print(f"成功: {result}")
```

### 獨立運行
```bash
python f01_fetcher_dev.py 2025-12-04
```

---

## 🧪 測試驗證

### 單元測試 ✅ 4/4 通過
```bash
python test_error_logging.py
```
- ✅ 向後兼容性測試
- ✅ 時間戳參數測試
- ✅ 上下文參數測試
- ✅ 組合參數測試

### 集成測試 ✅
```bash
python f01_fetcher_dev.py 2025-12-04
# 輸出: 2025.12.04  F01: 台指期貨外資 [未平倉] [多空淨額] : -29,032 口 [TAIFEX]
```

---

## 📊 版本演變

### v5.0 → v6.0 主要改進
| 項目 | v5.0 | v6.0 |
|------|------|------|
| **錯誤時間戳** | ❌ | ✅ |
| **錯誤上下文** | ❌ | ✅ |
| **日誌記錄** | 基本 | 增強 |
| **向後兼容** | N/A | ✅ 完全 |
| **測試覆蓋** | ~70% | ✅ 100% |

---

## 📞 故障排除

### 常見問題

#### 1. 連線超時
```
錯誤: F01 錯誤: 連線逾時，請檢查網路連線 [TAIFEX] (時間戳, timeout=30s)
解決: 檢查網路連線，稍後重試
```

#### 2. HTTP 錯誤
```
錯誤: F01 錯誤: HTTP 錯誤 500 [TAIFEX] (時間戳, status_code=500)
解決: TAIFEX 伺服器問題，稍後重試
```

#### 3. 沒有交易資料
```
錯誤: F01 錯誤: 該日無交易資料（可能是假日或休市日）
解決: 查詢其他交易日
```

#### 4. HTML 解析失敗
```
錯誤: F01 錯誤: HTML 解析失敗: ...
解決: 網頁結構可能改變，需要更新解析邏輯
```

---

## 🔗 相關文檔

### 規格書
- **簡化版**: [f01_fetcher_dev_spec_簡化版.md](f01_fetcher_dev_spec_簡化版.md) ← 當前文件
- **完整版**: [f01_fetcher_dev_spec.md](f01_fetcher_dev_spec.md) - 詳細技術文檔 (420 行)

### 配置文檔
- [openspec/project_dev.md](openspec/project_dev.md) - OpenSpec 配置

### 開發記錄
- [F01_Dev_完成報告.md](F01_Dev_完成報告.md) - 開發完成報告
- [F01_文檔完整性分析報告.md](F01_文檔完整性分析報告.md) - 文檔分析

### 源代碼
- [f01_fetcher_dev.py](f01_fetcher_dev.py) - Dev 版本源代碼 (493 行)
- [test_error_logging.py](test_error_logging.py) - 單元測試

---

**文檔類型**: 快速參考（簡化版）
**適用場景**: 日常開發、快速查閱
**完整資訊**: 請參閱完整版規格書
**維護狀態**: ✅ Active
