# GitHub Actions 設定指南

## 📋 步驟 1：啟用 GitHub Actions 寫入權限

### 為什麼需要這個設定？
GitHub Actions 需要權限才能自動 commit 和 push 更新的資料到你的 repository。

### 設定步驟

1. **打開你的 GitHub Repository**
   - 前往：`https://github.com/你的用戶名/taifex-query`

2. **進入設定頁面**
   - 點擊 `Settings` (齒輪圖示)

3. **找到 Actions 設定**
   - 左側選單找到 `Actions` → `General`

4. **設定 Workflow 權限**
   - 往下滾動找到 `Workflow permissions` 區塊
   - 選擇：✅ **Read and write permissions**
   - ✅ 勾選 **Allow GitHub Actions to create and approve pull requests** (可選)

5. **儲存設定**
   - 點擊頁面最下方的 `Save` 按鈕

### 📸 設定位置示意

```
Settings → Actions → General
└── Workflow permissions
    ├── ○ Read repository contents and packages permissions (預設)
    └── ● Read and write permissions  ← 選這個！
```

---

## 📋 步驟 2：Push Workflows 到 GitHub

### 檢查檔案

確認以下檔案已創建：
```
c:\Taifex\
├── .github/
│   └── workflows/
│       ├── daily-morning.yml  ✅
│       └── daily-night.yml    ✅
├── requirements.txt           ✅
└── GITHUB_SETUP.md           ✅ (本檔案)
```

### Push 指令

```bash
cd c:\Taifex

# 查看狀態
git status

# 添加所有新檔案
git add .github/workflows/
git add requirements.txt
git add GITHUB_SETUP.md

# Commit
git commit -m "feat: Add GitHub Actions workflows for automated data collection

- Add daily-morning.yml: 每日 21:00 抓取早盤數據 (F01-F17)
- Add daily-night.yml: 每日 05:30 抓取夜盤數據 (F21-F25)
- Add requirements.txt: Python dependencies
- Add GITHUB_SETUP.md: Setup instructions"

# Push
git push origin main
```

---

## 📋 步驟 3：測試 Workflow

### 方法 1：手動觸發測試

1. 前往 GitHub Repository
2. 點擊 `Actions` 標籤
3. 左側選擇 `Daily Morning Data Collection` 或 `Daily Night Data Collection`
4. 點擊右側 `Run workflow` 按鈕
5. 選擇 `Branch: main`
6. 點擊綠色的 `Run workflow` 按鈕

### 方法 2：等待定時執行

- **早盤**: 每天 21:00 (台灣時間) 自動執行
- **夜盤**: 每天 05:30 (台灣時間) 自動執行

### 檢查執行結果

1. 點擊 `Actions` 標籤
2. 查看最新的 workflow run
3. 點擊進去看詳細 log
4. 確認：
   - ✅ Python 環境安裝成功
   - ✅ 資料抓取成功
   - ✅ Commit 和 Push 成功

---

## 🔧 Workflow 功能說明

### daily-morning.yml (早盤)

**執行時間**: 每天 21:00 台灣時間
**抓取因子**: F01-F07, F11-F17 (早盤資料)
**執行流程**:
1. 設定 Python 環境
2. 安裝 Chrome 瀏覽器 (給 Selenium 用)
3. 執行 `run.py` 抓取資料
4. 生成預測儀表板 (步驟2才會啟用)
5. Commit + Push 到 GitHub

**Commit 訊息格式**: `🌅 Morning data update: YYYY-MM-DD`

### daily-night.yml (夜盤)

**執行時間**: 每天 05:30 台灣時間
**抓取因子**: F21-F25 (夜盤資料)
**執行流程**: 同上

**Commit 訊息格式**: `🌙 Night data update: YYYY-MM-DD`

---

## ⚠️ 常見問題

### Q1: Workflow 執行失敗怎麼辦？

**A**: 點擊失敗的 workflow run，查看詳細 log，常見原因：
- 網路連線問題 (retry 即可)
- 資料來源網站變動 (需要更新爬蟲程式)
- 權限不足 (檢查步驟1設定)

### Q2: 可以調整執行時間嗎？

**A**: 可以！編輯 `.github/workflows/*.yml` 檔案中的 `cron` 設定：
```yaml
schedule:
  - cron: '0 13 * * *'  # UTC 時間
```

### Q3: 如何暫停自動執行？

**A**:
1. 前往 GitHub → Actions → General
2. 找到 `Actions permissions`
3. 選擇 `Disable actions`

或是刪除 `.github/workflows/*.yml` 檔案

### Q4: 資料會存在哪裡？

**A**:
- **主要**: `data/` 目錄，commit 到 GitHub
- **備份**: GitHub Actions 會自動上傳 artifacts (保存7天)

---

## 📞 需要協助？

如果遇到問題，可以：
1. 查看 GitHub Actions log
2. 檢查本地執行 `python run.py YYYY-MM-DD` 是否正常
3. 確認權限設定正確

---

**設定完成後，系統將自動：**
- ✅ 每天 21:00 抓取早盤資料
- ✅ 每天 05:30 抓取夜盤資料
- ✅ 自動更新 GitHub
- ✅ 保留資料備份

**步驟2 完成後還會：**
- ✅ 自動生成預測儀表板
- ✅ 更新 README.md
