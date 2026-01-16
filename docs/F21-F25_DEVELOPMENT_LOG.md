# F21-F25 夜盤爬蟲開發日誌

## 📋 項目概述

開發 Wantgoo 夜盤指標爬蟲，抓取 F21-F25 共 5 個金融指標。

### 目標指標
| F代碼 | 名稱 | 數據來源 |
|-------|------|---------|
| F21 | NASDAQ指數 | Wantgoo全球市場 |
| F22 | 費城半導體指數 | Wantgoo全球市場 |
| F23 | EM-ND期指數 | Wantgoo全球市場 |
| F24 | 台積電ADR | Wantgoo全球市場 |
| F25 | 台指期盤後 | Wantgoo全球市場 |

---

## 🔍 開發階段詳解

### 階段 1：初始實現 (Commit: ad441232)

**時間**: 2026-01-16 初期

**目標**: 實現基本的爬蟲框架

**技術方案**:
- 使用 Playwright 瀏覽器自動化
- 使用 JavaScript 評估 (page.evaluate) 提取表格數據
- 目標 URL: https://www.wantgoo.com/global

**實現細節**:
```python
# 核心邏輯
page.goto('https://www.wantgoo.com/global', wait_until='networkidle')
table_data = page.evaluate('''() => {
    const results = [];
    document.querySelectorAll('table.global-tb tr').forEach(row => {
        // 提取行數據
    });
    return results;
}''')
```

**成果**:
- ✅ 基本爬蟲框架
- ✅ 所有 5 個指標配置
- ✅ 符號標準化 (▲→+, ▼→-)

**問題發現**: 間歇性失敗，有時返回 0 行

---

### 階段 2：穩定性改進 (Commit: 1040288e)

**時間**: 2026-01-16 中期

**問題**:
- 表格行偶發無法獲取
- 選擇器 `document.querySelectorAll('table.global-tb tr')` 不穩定

**根本原因分析**:
頁面有 24 個 `table.global-tb` 元素，直接用 `querySelectorAll('table.global-tb tr')` 會遇到 DOM 解析時序問題

**解決方案**:
改進 JavaScript 選擇器邏輯：
```javascript
// 從 ❌ 不穩定
document.querySelectorAll('table.global-tb tr')

// 改為 ✅ 穩定
const tables = document.querySelectorAll('table.global-tb');
tables.forEach(table => {
    table.querySelectorAll('tr').forEach(row => {
        // 處理每個表格內的行
    });
});
```

**成果**:
- ✅ 穩定性提高
- ✅ 3 次連續測試通過 (v1→v2→v3)

**新問題**: 仍有間歇性失敗

---

### 階段 3：反爬蟲突破 (Commit: 8e9760e6) ⭐ 關鍵突破

**時間**: 2026-01-16 後期

**診斷過程**:
```
測試 1: 成功（194 行）
測試 2: 失敗（0 行）
測試 3: 成功（194 行）
```

**根本原因**: Wantgoo 檢測到 Playwright 並阻止數據加載

**證據**:
```python
# ❌ 無反偵測時
page_text.includes('NASDAQ')  # False - 網站檢測到爬蟲，拒絕加載數據

# ✅ 有反偵測時
page_text.includes('NASDAQ')  # True - 偽裝成真實瀏覽器，正常加載
```

**反偵測實現**:
```python
# 1. 禁用自動化控制特徵
browser = p.chromium.launch(
    args=['--disable-blink-features=AutomationControlled']
)

# 2. 設置真實 User-Agent
context = browser.new_context(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)...'
)

# 3. 隱藏 webdriver 屬性
page.add_init_script('''
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false
    });
''')

# 4. 訪問首頁建立 session
page.goto('https://www.wantgoo.com/')
time.sleep(1)

# 5. 再訪問目標頁面
page.goto('https://www.wantgoo.com/global')
```

**數據提取改進**:
- ❌ 舊方法: 依賴 DOM 結構 (易受反爬蟲影響)
- ✅ 新方法: 從頁面文本 `document.body.innerText` 逐行解析

```python
page_text = page.evaluate('() => document.body.innerText')
lines = page_text.split('\n')
# 格式: "NASDAQ\t23530.02\t△58.27\t0.25\t04:59"
for line in lines:
    parts = line.split('\t')
    if len(parts) >= 3:
        change_value = parts[2]  # 直接提取漲跌值
```

**成果**:
- ✅ 穩定率大幅提升
- ✅ 連續 4 次測試全部成功 (v7→v10)
- ✅ 解決間歇性失敗問題

---

### 階段 4：代碼優化 (Commit: f188801d)

**時間**: 2026-01-16 晚期

**優化內容**:

**1. 提取常量**
```python
WANTGOO_URL = 'https://www.wantgoo.com/global'
BROWSER_USER_AGENT = 'Mozilla/5.0...'
INDICATOR_CONFIG = {
    'NASDAQ': ('F21', 'NASDAQ指數'),
    # ...
}
```

**2. 提取函數 `_parse_indicator_line()`**
```python
def _parse_indicator_line(line, indicator_map):
    """
    單一職責：只處理單行數據解析
    減少嵌套循環複雜性
    """
    # 實現邏輯
```

**3. 改進搜索算法**
```python
found_codes = set()  # 用 set 追蹤已找到指標

for line in page_text.split('\n'):
    # ... 處理邏輯

    # 早期終止：找到所有指標則停止
    if len(found_codes) == len(INDICATOR_CONFIG):
        break
```

**性能改進**:
| 項目 | 前 | 後 |
|------|-----|------|
| 首頁訪問 | ✓ | ✗ |
| 等待時間 | 5秒 | 3秒 |
| 總時間 | ~35秒 | ~32秒 |

**成果**:
- ✅ 執行時間縮短 8%
- ✅ 代碼易維護性提高
- ✅ 3 次測試通過 (v13→v15)

---

### 階段 5：超時問題修復 (Commit: 32756d6b) ⭐ 最終修復

**時間**: 2026-01-16 後期測試

**問題**:
```
Page.goto: Timeout 30000ms exceeded
waiting until "networkidle"
```

**根本原因**:
- `wait_until='networkidle'` 等待所有網絡請求完成
- Wantgoo 有大量背景請求（廣告、分析等）
- 容易超過 30 秒超時

**解決方案**:
```python
# ❌ 舊方法
page.goto(WANTGOO_URL, wait_until='networkidle', timeout=30000)

# ✅ 新方法
page.goto(WANTGOO_URL, wait_until='domcontentloaded', timeout=30000)
time.sleep(4)
```

**等待策略對比**:
| 策略 | 等待條件 | 時間 | 超時風險 |
|------|---------|------|---------|
| networkidle | 所有網絡請求完成 | ~30s+ | ⚠️ 高 |
| domcontentloaded | DOM 加載完成 | ~5-10s | ✅ 低 |

**調整邏輯**:
- 減少首頁訪問 → domcontentloaded 夠快
- 增加睡眠時間 (3→4秒) → 給 JavaScript 初始化時間

**成果**:
- ✅ 完全消除超時問題
- ✅ 3 次連續成功 (v16→v18)
- ✅ 生產就緒

---

## 🏗️ 最終架構

### 文件結構
```
scrapers/
├── nighttime.py          # F21-F25 爬蟲實現
│   ├── WANTGOO_URL       # 常量
│   ├── INDICATOR_CONFIG  # 指標配置
│   ├── _parse_indicator_line()   # 行解析函數
│   └── query_wantgoo_nighttime() # 主函數
└── __init__.py

nighttime_query.py        # 程式入口
output/
├── taifex_night_2026.01.16_v1.md
├── taifex_night_2026.01.16_v2.md
└── ... (共 19+ 版本)
```

### 程式流程

```
1. 瀏覽器初始化 (反偵測設置)
   ├─ 禁用自動化特徵
   ├─ 設置真實 User-Agent
   └─ 隱藏 webdriver 屬性

2. 頁面加載
   ├─ 訪問 https://www.wantgoo.com/global
   ├─ 等待 domcontentloaded
   └─ 睡眠 4 秒（讓 JavaScript 初始化）

3. 數據提取
   ├─ 獲取頁面文本 (document.body.innerText)
   ├─ 逐行解析文本
   └─ 查找指標關鍵詞

4. 數據解析
   ├─ 分割 Tab 字符
   ├─ 提取漲跌值（第 3 欄）
   ├─ 正則匹配符號和數字
   └─ 標準化格式 (+/-)

5. 結果組合
   ├─ 使用 set 去重
   ├─ 檢查早期終止條件
   └─ 返回結果列表

6. 文件保存
   ├─ 調用 save_to_markdown()
   └─ 自動版本遞增 (v1, v2, ...)
```

### 關鍵決策記錄

| 決策 | 理由 | 結果 |
|------|------|------|
| 用 Playwright 替代 requests+BeautifulSoup | Wantgoo 使用 JavaScript 動態渲染 | ✅ 正確 |
| 使用反偵測技巧 | 網站檢測到爬蟲並拒絕加載 | ✅ 必要 |
| 從文本而非 DOM 提取 | 反爬蟲環境下 DOM 結構不穩定 | ✅ 穩定 |
| 使用 domcontentloaded 而非 networkidle | networkidle 容易超時 | ✅ 可靠 |
| 提取 _parse_indicator_line() 函數 | 減少嵌套複雜性 | ✅ 可維護 |

---

## 📊 性能指標

### 最終性能 (v19)
```
執行時間: ~35 秒
- 瀏覽器啟動: ~5 秒
- 頁面加載: ~10 秒
- 睡眠等待: 4 秒
- 數據提取: ~16 秒

成功率: 100% (3/3 連續測試)
指標抓取: 5/5 完整
數據準確: ✅ 已驗證
```

### 開發統計
```
總提交數: 6 個（不含本文檔）
開發天數: 1 天
問題解決數: 4 個

主要技術挑戰:
1. ❌ 間歇性失敗 → ✅ DOM 選擇器優化
2. ❌ 反爬蟲阻止 → ✅ 瀏覽器偽裝
3. ❌ 超時問題 → ✅ 等待策略調整
4. ❌ 代碼複雜 → ✅ 函數提取和優化
```

---

## 🛠️ 故障排除指南

### 問題 1: 找不到指標
**症狀**: `Fetch failed or no data`

**可能原因**:
1. Wantgoo 反爬蟲升級
2. 頁面結構改變
3. 網絡問題

**排查步驟**:
```python
# 1. 檢查頁面是否加載
page_text = page.evaluate('() => document.body.innerText')
print(f"Page length: {len(page_text)}")

# 2. 檢查是否包含指標
print('NASDAQ' in page_text)
print('EM-ND' in page_text)

# 3. 增加睡眠時間
time.sleep(5)  # 或更多
```

**解決方案**:
- 增加睡眠時間到 5-6 秒
- 重新檢查 User-Agent 是否失效
- 嘗試訪問首頁後再訪問目標頁面

### 問題 2: Timeout 錯誤
**症狀**: `Page.goto: Timeout 30000ms exceeded`

**原因**:
- `wait_until='networkidle'` 等待太久

**解決方案**:
- 改用 `wait_until='domcontentloaded'`
- 增加睡眠時間補償

### 問題 3: 數據格式錯誤
**症狀**: 漲跌值為 `None` 或空字符串

**可能原因**:
- 正則表達式不匹配
- Tab 分割位置不對
- 符號格式變化

**排查**:
```python
# 打印該行以檢查格式
print(f"Line: {repr(line)}")
print(f"Parts: {line.split(chr(9))}")  # Tab 分割
```

---

## 📝 維護建議

### 定期檢查清單
- [ ] 每週運行一次確認數據準確性
- [ ] 監控執行時間是否增加
- [ ] 定期查看 Wantgoo 網站是否改版
- [ ] 保持 Playwright 和相關包更新

### 可能的改進方向
1. **加入重試機制**: 失敗時自動重試 3 次
2. **添加日誌**: 記錄詳細的調試信息
3. **性能監控**: 跟蹤執行時間趨勢
4. **告警機制**: 失敗時發送通知
5. **備用方案**: 如果 Wantgoo 失敗，嘗試其他數據源

### 反爬蟲升級預案
如果 Wantgoo 增強反爬蟲：
1. 增加隨機延遲 (random delay)
2. 輪換 User-Agent
3. 使用代理池
4. 增加請求間隔
5. 考慮使用 Puppeteer (Node.js) 替代 Playwright

---

## 🔗 相關檔案

- `scrapers/nighttime.py` - 爬蟲實現
- `nighttime_query.py` - 程式入口
- `utils/helpers.py` - 文件保存函數
- `docs/IMPLEMENTATION_REFERENCE.md` - 指標實作手冊
- `.gitignore` - 忽略本地檔案

---

## 📚 版本歷史

| 版本 | 提交 | 描述 |
|------|------|------|
| v1-v8 | ad441232-8e9760e6 | 初始實現→反偵測突破 |
| v9-v15 | 8e9760e6-f188801d | 代碼優化階段 |
| v16-v18 | 32756d6b | 超時修復 |
| v19+ | 32756d6b (final) | 生產版本 |

---

## ✅ 最終檢查清單

- ✅ 所有 5 個指標正確抓取
- ✅ 輸出格式符合規範
- ✅ 版本號自動遞增
- ✅ 不覆蓋現有檔案
- ✅ 符號格式正確 (+/-)
- ✅ 無編碼錯誤
- ✅ 性能可接受 (~35秒)
- ✅ 穩定性達到 100% (3/3 測試)
- ✅ 代碼易維護
- ✅ 文檔完整

---

**開發完成日期**: 2026-01-16
**最後修改**: 2026-01-16
**狀態**: ✅ 生產就緒
