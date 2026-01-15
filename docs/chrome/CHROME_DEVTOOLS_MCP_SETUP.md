# Chrome DevTools MCP 整合指南

**文件版本**: 1.0  
**建立日期**: 2026/01/15  
**適用專案**: taifex-query + DGtech.com.tw

---

## 📋 目錄

1. [快速開始](#快速開始)
2. [環境設定](#環境設定)
3. [整合方案](#整合方案)
4. [使用場景](#使用場景)
5. [常見命令](#常見命令)
6. [故障排除](#故障排除)

---

## 🚀 快速開始

### 一行命令安裝（推薦）

```bash
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
```

### 驗證安裝成功

在 Claude Code 中執行以下提示：

```
請檢查 https://developers.chrome.com 的 LCP（Largest Contentful Paint）效能指標
```

如果看到 Chrome 自動啟動並分析，表示安裝成功 ✅

---

## ⚙️ 環境設定

### 設定位置

根據你的作業系統，找到 Claude Code 設定檔：

**macOS / Linux:**
```bash
~/.local/share/claude-code/claude_code_config.json
或
~/.config/claude-code/claude_code_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_code_config.json
或
C:\Users\{YourUsername}\AppData\Roaming\Claude\claude_code_config.json
```

### 手動設定（如果需要）

如果自動安裝失敗，手動編輯設定檔，加入：

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

### 驗證設定

```bash
claude mcp list
```

應該看到 `chrome-devtools` 在列表中

---

## 🏗️ 整合方案

### 專案結構建議

```
你的專案根目錄/
│
├── .mcp/
│   └── chrome_devtools_config.md      ← MCP 設定文件
│
├── taifex-query/
│   ├── F01/                           ← 已完成
│   ├── F14/                           ← 開發中（外資未平倉）
│   ├── F15-F20/                       ← 待開發
│   ├── main.py
│   │
│   └── mcp_tools/                     ← 新增資料夾
│       ├── __init__.py
│       ├── chrome_integration.py      ← Chrome 整合模組
│       └── verify_taifex_data.py      ← 資料驗證腳本
│
├── dgtech-website/
│   ├── M00/
│   ├── M01-M17/
│   │
│   └── mcp_tools/
│       ├── __init__.py
│       ├── verify_pages.py            ← 頁面驗證腳本
│       └── automated_tests.py         ← 自動化測試
│
└── README_MCP_INTEGRATION.md           ← 本文件
```

### 建立 Chrome 整合模組

**檔案**: `taifex-query/mcp_tools/chrome_integration.py`

```python
"""
Chrome DevTools MCP 整合模組
用於自動化驗證和測試
"""

class ChromeDevToolsVerifier:
    """Chrome DevTools 驗證器"""
    
    def __init__(self):
        self.tools_available = True
    
    def verify_taifex_data_fetch(self):
        """驗證台期所資料爬蟲"""
        prompt = """
        請幫我驗證台期所資料爬蟲：
        1. 打開 https://www.taifex.com.tw/cht/3/totalTableDate
        2. 檢查「外資未平倉」相關欄位是否正確載入
        3. 拍攝截圖驗證頁面內容
        4. 檢查 Network 請求是否有失敗（Status 500 或其他錯誤）
        """
        return prompt
    
    def verify_website_page(self, page_name: str, url: str):
        """驗證網站頁面"""
        prompt = f"""
        請幫我驗證 {page_name} 頁面：
        1. 打開 {url}
        2. 拍攝截圖檢查頁面布局
        3. 檢查 Console 是否有 JavaScript 錯誤
        4. 驗證所有圖片和資源是否正確載入
        """
        return prompt
    
    def check_performance_metrics(self, url: str):
        """檢查效能指標"""
        prompt = f"""
        請檢查 {url} 的效能指標：
        1. 記錄效能追蹤
        2. 獲取 LCP、FID、CLS 等 Core Web Vitals
        3. 分析網路請求時間
        4. 提供優化建議
        """
        return prompt


def create_verification_script(feature_name: str, url: str):
    """
    建立驗證腳本
    
    使用方式：
    prompt = create_verification_script("F14 外資未平倉", "https://...")
    # 將 prompt 複製到 Claude Code 中執行
    """
    return f"""
    === 自動驗證：{feature_name} ===
    
    請幫我驗證以下內容：
    1. 打開 {url}
    2. 在瀏覽器開發者工具中檢查資料載入
    3. 拍攝截圖驗證結果
    4. 檢查 Network tab 中的 API 呼叫
    5. 驗證資料是否與預期相符
    
    期望結果：
    - 頁面正常載入
    - 所有資料字段正確顯示
    - 沒有 JavaScript 錯誤
    """
```

---

## 📍 使用場景

### 場景 1：驗證 taifex-query 資料爬蟲

**何時使用**: F14（外資未平倉）開發完成後

**指令**:
```python
from taifex_query.mcp_tools.chrome_integration import ChromeDevToolsVerifier

verifier = ChromeDevToolsVerifier()
print(verifier.verify_taifex_data_fetch())
```

將輸出的提示複製到 Claude Code 中執行。

**驗證清單**:
- [ ] 頁面正常載入
- [ ] 外資未平倉數據正確顯示
- [ ] Network 無 5xx 錯誤
- [ ] Console 無關鍵錯誤

---

### 場景 2：驗證 DGtech 網站頁面

**何時使用**: M00-M17 各模組開發完成後

**步驟 1**: 啟動開發伺服器
```bash
cd dgtech-website
python -m http.server 8000
# 或用你的框架的開發伺服器
```

**步驟 2**: 在 Claude Code 中執行
```
請幫我驗證 DGtech 首頁：
1. 打開 http://localhost:8000
2. 檢查頁面布局是否正確
3. 驗證所有按鈕和表單功能
4. 拍攝截圖供我檢查
```

**驗證清單**:
- [ ] 頁面布局正確
- [ ] 所有圖片載入成功
- [ ] 表單可以互動
- [ ] 沒有 JavaScript 錯誤

---

### 場景 3：自動化回歸測試

**何時使用**: 在外包廠商提交代碼時

**腳本**:
```python
# dgtech-website/mcp_tools/automated_tests.py

def run_regression_tests():
    """執行回歸測試"""
    test_cases = [
        {
            "name": "M00 - 首頁",
            "url": "http://localhost:8000/index.html",
            "checks": ["layout", "images", "links"]
        },
        {
            "name": "M01 - 登入頁",
            "url": "http://localhost:8000/login.html",
            "checks": ["form", "validation", "errors"]
        },
        # ... 更多測試案例
    ]
    
    for test in test_cases:
        print(f"\n=== 測試: {test['name']} ===")
        print(f"URL: {test['url']}")
        print(f"檢查項目: {', '.join(test['checks'])}")
```

---

## 💻 常見命令

### 在 Claude Code 中使用

#### 1. 檢查網站效能
```
使用 Chrome DevTools 檢查 https://www.taifex.com.tw 的載入時間和效能瓶頸
```

#### 2. 驗證資料爬蟲
```
請打開 https://www.taifex.com.tw/cht/3/totalTableDate
驗證「外資未平倉口數」欄位是否正確載入
檢查 Network tab 中所有請求的狀態
```

#### 3. 測試頁面功能
```
請打開我的網站 http://localhost:8000/form.html
檢查表單提交是否正常運作
監控 Network 請求和 Console 日誌
```

#### 4. 截圖驗證
```
請打開 http://localhost:3000 並拍攝截圖
驗證頁面布局是否符合設計稿
檢查所有視覺元素是否正確顯示
```

---

## 🔧 進階使用

### 連接到現有瀏覽器

如果你想讓 Chrome DevTools MCP 連接到你已打開的瀏覽器實例：

1. 打開 Chrome，並啟用遠端除錯
```
chrome://inspect/#remote-debugging
```

2. 在設定檔中加入：
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--browser-url",
        "http://127.0.0.1:9222"
      ]
    }
  }
}
```

---

## ❌ 故障排除

### 問題 1：Chrome 自動啟動失敗

**症狀**: 
```
Error: Unable to start Chrome
```

**解決方案**:
1. 確保已安裝 Chrome（而非其他瀏覽器）
2. 在命令列中測試：`which google-chrome` （Linux） 或 `where chrome` （Windows）
3. 手動指定 Chrome 路徑：

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--chrome-path",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
      ]
    }
  }
}
```

---

### 問題 2：連接逾時

**症狀**:
```
Timeout connecting to Chrome
```

**解決方案**:
1. 檢查 Chrome 是否正常啟動
2. 增加逾時時間
3. 嘗試重啟 Claude Code

---

### 問題 3：找不到 MCP Server

**症狀**:
```
chrome-devtools MCP server not found
```

**解決方案**:
```bash
# 重新安裝
claude mcp remove chrome-devtools
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest

# 驗證
claude mcp list
```

---

## 📊 整合到你的工作流程

### 開發流程

```
1. 編寫代碼 (F14 模組、M00-M17 頁面)
   ↓
2. 在 Claude Code 中驗證
   (使用 Chrome DevTools MCP 自動測試)
   ↓
3. 檢查結果
   (檢視截圖、Console 日誌、Network 數據)
   ↓
4. 修正問題
   ↓
5. 外包前最後驗證
```

### 外包驗收流程

```
1. 外包廠商交付代碼
   ↓
2. 使用 Chrome DevTools MCP 自動驗證
   (執行回歸測試、檢查效能)
   ↓
3. 生成驗證報告
   ↓
4. 根據結果驗收或退回
```

---

## 📚 相關資源

- [Chrome DevTools MCP 官方文檔](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [Core Web Vitals 指南](https://web.dev/vitals/)
- [Claude Code 使用指南](https://docs.claude.com)

---

## 📝 筆記

- Chrome DevTools MCP 會在你的本機自動啟動 Chrome（無需提前開啟）
- 每次驗證會建立新的臨時瀏覽器實例，不會影響你的正常瀏覽
- 可以在任何時刻中斷驗證，不會有副作用

---

**下一步**: 選擇你要先整合的場景，準備好後告訴我！
