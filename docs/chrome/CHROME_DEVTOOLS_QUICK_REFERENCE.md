# Chrome DevTools MCP 快速參考卡

## 🚀 一句話安裝

```bash
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
```

驗證: `claude mcp list` → 應該看到 `chrome-devtools`

---

## 📌 最常用的 3 個提示

### 1️⃣ 驗證 taifex 資料爬蟲 (F14)

複製以下內容到 **Claude Code** 中執行：

```
使用 Chrome DevTools 幫我驗證台期所資料爬蟲：

1. 打開 https://www.taifex.com.tw/cht/3/totalTableDate
2. 確認「外資未平倉」數據正確載入
3. 檢查 Network tab - 確認沒有紅色錯誤
4. 檢查 Console - 確認沒有 JavaScript 錯誤
5. 拍攝截圖驗證結果

期望看到的數據 (2026/01/14)：
- 外資多方未平倉: 297,271 口
- 外資空方未平倉: 473,500 口  
- 外資多空淨額: -176,229 口
```

---

### 2️⃣ 驗證網站頁面 (DGtech M00-M17)

```
使用 Chrome DevTools 幫我驗證網頁：

1. 打開 http://localhost:8000/[頁面名稱]
2. 拍攝整個頁面的截圖
3. 檢查 Console - 有無紅色錯誤？
4. 檢查 Network - 有無紅色 (5xx) 或黃色 (4xx)？
5. 點擊測試所有按鈕和連結

報告格式：
✅ 頁面載入時間: X 秒
✅ 視覺效果: [正常/有問題]
✅ Console 錯誤: [無/有 - 列出]
✅ Network 問題: [無/有 - 列出]
```

---

### 3️⃣ 快速效能檢查

```
使用 Chrome DevTools 檢查網站效能：

1. 打開目標 URL
2. 打開 Lighthouse (DevTools > Lighthouse)
3. 選擇 "Mobile" 和 "Desktop" 測試
4. 記錄以下指標：
   - LCP: __ 秒 (目標 < 2.5)
   - FID: __ 毫秒 (目標 < 100)
   - CLS: __ (目標 < 0.1)
   - 總體評分: __ / 100
5. 拍攝 Lighthouse 報告截圖
```

---

## 🎯 針對不同場景的提示模板

### 場景 A: 爬蟲驗證 (taifex-query)

```
從台期所爬蟲 F14 - 外資未平倉

🔍 驗證步驟：
- 目標網址: https://www.taifex.com.tw/cht/3/totalTableDate
- 檢查項目: [勾選下列]
  □ 頁面 3 秒內載入
  □ 外資數據表格可見
  □ 3 個外資欄位有數值
  □ Network 無紅色 (5xx) 或黃色 (4xx)
  □ Console 無紅色錯誤

📊 期望結果格式:
{
  "date": "YYYY/MM/DD",
  "foreign_investor_oi": {
    "long": 297271,
    "short": 473500,
    "net": -176229
  }
}
```

### 場景 B: 頁面驗證 (DGtech 網站)

```
驗證 DGtech 網站頁面: [M00/M01/M02...]

📋 逐項驗證：
1. 視覺檢查
   - 頁面布局: 正常 / 異常
   - 圖片載入: 正常 / 缺失
   - 文字清晰: 正常 / 不清

2. 功能檢查
   - 所有連結: 可點 / 有死連結
   - 表單: 可提交 / 有問題
   - 按鈕: 反應正常 / 無反應

3. 技術檢查 (DevTools)
   - Console 錯誤: 無 / 有 (列出)
   - Network 失敗: 無 / 有 (列出)
   - 載入時間: __ 秒

4. 截圖
   - 整頁截圖
   - Console 截圖 (如有錯誤)
   - Network 截圖 (如有失敗)
```

### 場景 C: 表單驗證

```
驗證 [表單名稱] 表單功能

✅ 必填驗證:
- 不填任何欄位 → 提交 → 顯示「欄位必填」? 是/否

✅ 格式驗證:
- Email 欄位：輸入「abc」→ 提交 → 顯示「格式錯誤」? 是/否
- 密碼欄位：輸入「123」→ 提交 → 提示強度? 是/否

✅ 提交驗證:
- 填入正確資料 → 提交
- Network tab 顯示 API 呼叫嗎? 是/否
- 伺服器回應狀態: 200 / 其他
- 提交後重定向到: __________

✅ Console 檢查:
- 有紅色錯誤嗎? 是/否 (如有，列出)
- 有黃色警告嗎? 是/否
```

---

## 🛠️ 故障排除快速指南

| 問題 | 解決方案 |
|------|--------|
| `Command not found: claude mcp` | 確保已安裝 Claude Code 最新版本 |
| Chrome 自動啟動失敗 | 檢查 Chrome 是否已安裝 |
| 連接逾時 | 重啟 Claude Code，重新執行命令 |
| `MCP server not found` | 執行 `claude mcp list` 確認，若無則重新安裝 |
| 無法連接本機開發伺服器 | 確認伺服器運行中 (`localhost:8000`) |

---

## 📊 推薦的驗證流程

### 開發階段
```
編寫代碼 
  ↓
用 Chrome DevTools 快速驗證
  ↓
修改問題
  ↓
再次驗證
```

### 交付前
```
功能完成
  ↓
完整的 Chrome DevTools 驗證
  ↓
拍攝所有截圖
  ↓
生成驗證報告
  ↓
準備交付
```

### 外包驗收
```
收到廠商代碼
  ↓
運行回歸測試 (Chrome DevTools)
  ↓
檢查驗證報告
  ↓
確認無誤 → 接受
  或有問題 → 退回修改
```

---

## 💾 檔案路徑速查

| 檔案 | 用途 |
|------|------|
| `CHROME_DEVTOOLS_MCP_SETUP.md` | 完整文檔 |
| `chrome_integration.py` | Python 模組 |
| 本文件 | 快速參考 |

---

## 🔗 快速連結

- 台期所三大法人頁面: https://www.taifex.com.tw/cht/3/totalTableDate
- 本機開發伺服器: http://localhost:8000
- Chrome DevTools 文檔: https://github.com/ChromeDevTools/chrome-devtools-mcp

---

## 📝 筆記

**重要**: 每次驗證會建立新的 Chrome 實例，不會影響你的正常瀏覽

**提示**: 將常用的驗證提示 (上面的 1️⃣ 2️⃣ 3️⃣) 保存為書籤，快速複製使用

**建議**: 定期執行「完整驗證套件」，確保沒有迴歸問題

---

## ⭐ 最後提醒

✨ 開始前確認已執行:
```bash
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
```

✨ 每次開始驗證前可以測試連接:
```
請打開 https://developers.chrome.com 並拍攝截圖
```

✨ 有問題隨時回到完整文檔 `CHROME_DEVTOOLS_MCP_SETUP.md`

---

**祝你驗證順利！** 🎉
