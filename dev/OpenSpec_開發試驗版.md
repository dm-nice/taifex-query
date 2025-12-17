# OpenSpec 開發試驗版指南

> **快速試驗版** - 驗證想法、測試資料源、決定方案
>
> 試驗版用時短 (20 分鐘)、門檻低、試完就刪，適合探索新模組

---

## 📋 試驗版 vs 完整版

```
┌─────────────────────────────────┬──────────────────────┬──────────────┐
│ 環節                              │ 完整版 (正式發布)     │ 試驗版 (玩玩看) │
├─────────────────────────────────┼──────────────────────┼──────────────┤
│ Phase 1: 文檔                     │ 5 份 (1.5 小時)     │ 0 份 (無)     │
│ Phase 2: 代碼                     │ 380+ 行 (1.5 小時)   │ 150 行 (20 分) │
│ Phase 3: 測試                     │ 21 個 (1 小時)       │ 0 個 (無)     │
│ Phase 4: 部署                     │ 3 步驟 (0.5 小時)    │ 0 個 (試驗用) │
├─────────────────────────────────┼──────────────────────┼──────────────┤
│ 總工時                            │ 4.5 小時            │ 20 分鐘       │
│ 代碼質量                          │ 生產級 (90%+ 覆蓋)   │ 原型級 (無測試)│
│ 保留期限                          │ 永久                │ 試用完刪掉    │
└─────────────────────────────────┴──────────────────────┴──────────────┘
```

---

## 🚀 快速試驗版開發流程 (20 分鐘)

### 步驟 1: 建立試驗目錄 (1 分鐘)

```bash
# 建立臨時試驗目錄（不用跟 dev/f11_package 一樣的複雜結構）
mkdir dev/prototype_test
cd dev/prototype_test

# 只需一個檔案
touch prototype_fetcher.py
```

---

### 步驟 2: 寫最簡單的程式碼 (10 分鐘)

```python
"""
快速試驗版 - 試完後就刪掉
用來驗證想法是否可行、確認資料源、測試技術方案
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_test():
    """
    簡單版本，不需要完整的異常處理
    目的：快速驗證邏輯可行
    """
    try:
        # 1. 定義目標 URL
        url = "https://..."  # 填入目標網址
        
        # 2. 發送請求（簡單版本）
        response = requests.get(url, timeout=5)
        
        # 3. 解析 HTML（簡單版本）
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        
        # 4. 提取數據（快速提取，不管邊界情況）
        value = table.find('td').text.strip()
        
        # 5. 簡單格式化
        date = datetime.now().strftime("%Y.%m.%d")
        return f"{date}  FXX: {value}"
    except Exception as e:
        return f"錯誤: {e}"

if __name__ == '__main__':
    result = fetch_test()
    print(result)
    
    # 保存結果用於檢查
    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write(result)
```

---

### 步驟 3: 測試並調整 (5 分鐘)

```bash
# 直接運行，看看對不對
python prototype_fetcher.py

# 查看輸出結果
type output.txt

# 如果結果正確 → 進入完整版開發
# 如果結果錯誤 → 繼續調整這個檔案
```

**調試技巧:**

```python
# 加入調試輸出看看抓到什麼
print(f"Response Status: {response.status_code}")
print(f"HTML Length: {len(response.text)}")
print(f"Table Found: {table is not None}")

# 打印出表格內容看結構
print(soup.prettify())
```

---

### 步驟 4: 確認可行性 (決策點)

```
試驗結果？

✅ 成功 → 進入完整版開發
        ├─ 複製試驗版的邏輯
        ├─ 補充文檔、異常處理
        └─ 編寫 21 個測試

❌ 失敗 → 調整試驗版
        ├─ 確認 URL 是否正確
        ├─ 檢查頁面是動態還是靜態
        ├─ 嘗試不同的選擇器
        └─ 考慮使用 Selenium 代替 requests
```

---

### 步驟 5: 升級到完整版

```bash
# 試驗版確認可行後，正式開發
mkdir dev/f02_package

# 複製 F11 範本（省時間）
cp dev/f11_package/openspec dev/f02_package/openspec

# 編輯 openspec/ 文件（改成新模組的內容）
# 編寫 f02_openspec_dev.py（改進試驗版的代碼）
# 編寫 test_f02_openspec.py（21 個測試）
# ... 完整開發流程
```

---

### 步驟 6: 清理試驗版

```bash
# 試驗完直接刪掉（不需要保留）
rm -r dev/prototype_test

# 確認已刪
ls dev/prototype_test  # 應該不存在
```

---

## 🎯 何時使用試驗版？

### ✅ 應該使用試驗版的情況

| 情況 | 說明 |
|------|------|
| **完全陌生的資料源** | 不確定頁面結構、需要先調查 |
| **不確定技術方案** | requests vs Selenium？靜態 vs 動態？ |
| **頁面結構複雜** | 20+ 欄位，不確定抓哪個 |
| **時間緊急** | 先試再決定投入 4.5 小時 |
| **想驗證想法** | POC (Proof of Concept) |

### ❌ 可以直接做完整版的情況

| 情況 | 說明 |
|------|------|
| **已做過類似模組** | 複用經驗，直接做完整版 |
| **資料源結構已確認** | 已知道抓哪個欄位 |
| **技術方案已決定** | 已決定用 HTTP 還是 Selenium |
| **時間充足** | 有 4.5 小時投入 |

---

## 📊 試驗版特點

### 試驗版特點（快速、簡單）

```python
# ❌ 不寫文檔
#    (無 project.md、proposal.md、design.md)

# ❌ 不寫完整異常處理
#    (try-except 一筆帶過)

# ❌ 不寫測試
#    (無單元測試、無覆蓋率驗證)

# ❌ 不部署
#    (不複製到 modules、不集成 run.py)

# ✅ 快速驗證邏輯
#    (20 分鐘快速試驗)

# ✅ 試驗新技術
#    (試試 Selenium、試試新的 HTML 選擇器)

# ✅ 確認資料源
#    (確認能抓到資料)

# ✅ 試完刪掉
#    (丟棄式代碼，無技術債)
```

### 完整版特點（正式、穩定）

```python
# ✅ 5 份詳細文檔
#    (project.md、proposal.md、design.md、tasks.md、spec.md)

# ✅ 5+ 異常類型處理
#    (timeout、HTTP error、parsing error、malformed value...)

# ✅ 21 個單元測試
#    (6 個測試類、90%+ 代碼覆蓋率)

# ✅ 正式部署
#    (複製到 modules、集成 run.py、生產驗證)

# ❌ 耗時更長
#    (4.5 小時 vs 20 分鐘)

# ❌ 但質量最好
#    (生產級代碼、完全可維護)

# ❌ 生產就靠它
#    (永久保留、定期更新)
```

---

## 🔄 試驗版 → 完整版升級流程

### 完整升級步驟

```
1️⃣  試驗版驗證成功
    └─ prototype_test/prototype_fetcher.py ✅
       output.txt ✅

2️⃣  複製試驗版邏輯
    └─ 複製核心提取代碼到 f02_openspec_dev.py

3️⃣  補充完整版要素
    ├─ Phase 1: 編寫 5 份文檔 (1.5h)
    ├─ Phase 2: 完善異常處理、代碼優化 (1h)
    ├─ Phase 3: 編寫 21 個測試 (1h)
    └─ Phase 4: 部署驗證 (0.5h)

4️⃣  刪掉試驗版
    └─ rm -r dev/prototype_test
```

### 代碼遷移範例

```python
# ❌ 試驗版 (簡單版)
def fetch_test():
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        value = soup.find('table').find('td').text
        return f"{date}  FXX: {value}"
    except Exception as e:
        return f"錯誤: {e}"

        ⬇️ 升級

# ✅ 完整版 (生產版)
def fetch(date: str = None) -> str:
    """完整版本，有完善異常處理"""
    try:
        # 驗證日期格式
        datetime.strptime(date, "%Y-%m-%d")
        
        # 發送請求
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        if not table:
            return "F02 錯誤: 找不到表格 [來源]"
        
        # 提取數據（支援多欄名變體）
        value = extract_from_table(table)
        
        # 格式化輸出
        return format_output(date, value)
        
    except requests.Timeout:
        return "F02 錯誤: 連線逾時 [來源]"
    except Exception as e:
        return f"F02 錯誤: {str(e)} [來源]"
```

---

## 💡 試驗版開發技巧

### 快速調試技巧

```python
# 1️⃣  保存原始 HTML 檢查
with open('debug.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

# 2️⃣  打印漂亮格式的 HTML
from bs4 import BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')
print(soup.prettify()[:2000])  # 只打前 2000 字元

# 3️⃣  檢查所有表格
tables = soup.find_all('table')
print(f"找到 {len(tables)} 個表格")
for i, table in enumerate(tables):
    print(f"表格 {i}: {len(table.find_all('tr'))} 行")

# 4️⃣  檢查所有欄位名稱
headers = soup.find_all('th')
print([h.text for h in headers])

# 5️⃣  嘗試不同的選擇器
# 試試看哪個能抓到數據
print(soup.find('table'))                    # 第一個表格
print(soup.select('table[id="xyz"]'))       # 指定 ID 的表格
print(soup.find_all('td')[10])              # 第 11 個 td
```

### 判斷靜態 vs 動態

```python
# 試試 requests（靜態頁面）
import requests
response = requests.get(url)

# 檢查是否有數據
if "指數" in response.text:
    print("✅ 靜態頁面，requests 可用")
else:
    print("❌ 動態頁面，需要 Selenium")
    
    # 改用 Selenium
    from selenium import webdriver
    driver = webdriver.Chrome()
    driver.get(url)
    # ... Selenium 代碼
```

---

## 📁 試驗版範本快速複製

### 一鍵建立試驗環境

```bash
# 進入 dev 目錄
cd c:\Taifex\dev

# 建立目錄
mkdir prototype_test

# 建立檔案
notepad prototype_test\prototype_fetcher.py
```

### 最小化試驗代碼 (Minimal Template)

```python
"""快速試驗版"""
import requests
from bs4 import BeautifulSoup

def test():
    # 改這裡！填入你的 URL
    url = "https://your-data-source.com/data"
    
    try:
        r = requests.get(url, timeout=5)
        s = BeautifulSoup(r.text, 'html.parser')
        
        # 改這裡！改成你的提取邏輯
        value = s.find('table').find('td').text
        
        print(f"結果: {value}")
        return value
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == '__main__':
    test()
```

---

## 📝 檢查清單

### 試驗版檢查清單

- [ ] 建立 `dev/prototype_test/` 目錄
- [ ] 建立 `prototype_fetcher.py` 檔案
- [ ] 填入目標 URL
- [ ] 填入提取邏輯
- [ ] 運行並查看 output.txt
- [ ] 確認結果正確

### 升級決策

- [ ] 結果正確？→ 進入完整版開發
- [ ] 結果錯誤？→ 調試試驗版
- [ ] 需要 Selenium？→ 改試驗代碼
- [ ] 確認可行？→ 開始完整版

### 清理檢查清單

- [ ] 完整版開發完成
- [ ] 完整版測試通過 (21/21)
- [ ] 完整版部署成功
- [ ] 刪除 `dev/prototype_test/` 目錄
- [ ] 確認試驗版已完全刪除

---

## 🎓 常見問題

### Q1: 試驗版代碼能不能直接複製到完整版？

**A:** 可以，但要改進：

```python
# ❌ 試驗版的代碼
value = soup.find('table').find('td').text

# ✅ 改進為完整版
def extract_from_table(table):
    # 支援多欄名變體
    for name in ['現在指數', '加權指數', '指數']:
        header = table.find('th', string=name)
        if header:
            # ... 完整邏輯
```

---

### Q2: 試驗版用 Selenium 慢，有沒有辦法加速？

**A:** 有幾個技巧：

```python
# 1️⃣  用 headless 模式（無瀏覽器 GUI）
from selenium import webdriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# 2️⃣  調整等待時間
from selenium.webdriver.support.ui import WebDriverWait
wait = WebDriverWait(driver, 3)  # 改短一點

# 3️⃣  如果不需要 JavaScript，用 requests（更快）
import requests
response = requests.get(url)
```

---

### Q3: 試驗版完成後，是否要保留日誌？

**A:** 建議保留調查記錄，但刪除代碼：

```bash
# 保留調查結果（文字記錄）
# dev/prototype_test_report.txt
# 記錄：URL、結構、欄位、技術方案決定

# 刪除試驗代碼
rm -r dev/prototype_test
```

---

### Q4: 能不能在試驗版直接測試？

**A:** 可以，但簡單就好：

```python
# 簡單的內嵌測試
def test():
    result = fetch_test()
    assert "F11:" in result
    assert "2025.12" in result
    print("✅ 基本測試通過")

if __name__ == '__main__':
    test()
```

但完整的 21 個測試還是等升級到完整版再做。

---

## 📌 總結

| 項目 | 試驗版 | 完整版 |
|------|--------|--------|
| **用途** | 驗證想法、POC | 正式發布 |
| **工時** | 20 分鐘 | 4.5 小時 |
| **文檔** | 無 | 5 份 |
| **代碼行數** | 150 行 | 380+ 行 |
| **測試** | 無 | 21 個 |
| **質量** | 原型級 | 生產級 |
| **保留期限** | 試完刪 | 永久 |
| **何時用** | 探索階段 | 確認可行後 |

---

## 🚀 快速開始

### 1 分鐘建立試驗版

```bash
# 進入開發目錄
cd c:\Taifex\dev

# 建立試驗版目錄和檔案
mkdir prototype_test
echo. > prototype_test\prototype_fetcher.py

# 編輯檔案（填入你的 URL 和邏輯）
code prototype_test\prototype_fetcher.py

# 運行測試
python prototype_test\prototype_fetcher.py
```

### 成功後升級

```bash
# 如果試驗成功
mkdir f02_package
# 複製 F11 範本，開始完整開發

# 完整版完成後
rm -r prototype_test  # 刪掉試驗版
```

---

**版本**: v1.0  
**創建日期**: 2025-12-17  
**適用**: 所有新模組開發  
**推薦場景**: 探索陌生資料源、驗證技術方案
