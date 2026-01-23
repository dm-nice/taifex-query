# Test Case Guide

## 基本資訊

| 欄位 | 內容 |
|------|------|
| **Test Case ID** | TC_[模組]_[功能]_[序號]_[POS/NEG] |
| **Title** | [一句話描述測試目的] |
| **Module** | [所屬模組名稱] |
| **Priority** | P0 / P1 / P2 / P3 |
| **Test Type** | Functional / Integration / Regression / Smoke |
| **Author** | [撰寫者] |
| **Created Date** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |

---

## 測試詳情

### Preconditions (前置條件)
```
- [環境條件，例：系統已啟動]
- [資料條件，例：測試帳號已存在]
- [權限條件，例：使用者已登入]
```

### Test Data (測試資料)
| 參數名稱 | 輸入值 | 說明 |
|---------|--------|------|
| username | test@example.com | 有效帳號 |
| password | Test@123 | 符合密碼規則 |

### Test Steps (測試步驟)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | [具體操作步驟] | [該步驟預期結果] |
| 2 | [具體操作步驟] | [該步驟預期結果] |
| 3 | [具體操作步驟] | [該步驟預期結果] |

### Expected Result (最終預期結果)
```
- [可驗證的結果 1]
- [可驗證的結果 2]
- [效能要求，例：回應時間 < 3秒]
```

### Actual Result (實際結果)
```
[執行後填寫]
```

### Status (執行狀態)
- [ ] Not Executed
- [ ] Pass
- [ ] Fail
- [ ] Blocked

### Notes (備註)
```
[相關說明、已知問題、依賴項目等]
```

---

## 附錄：Priority 定義

| Level | 定義 | 執行時機 |
|-------|------|----------|
| **P0** | 阻斷性功能，影響核心業務 | 每次必測 |
| **P1** | 主要功能，影響用戶體驗 | 每次必測 |
| **P2** | 次要功能，影響較小 | 視情況測試 |
| **P3** | 低影響功能或優化項目 | 完整測試時執行 |

## 附錄：Test Type 定義

- **Functional**: 功能測試，驗證功能是否符合需求
- **Integration**: 整合測試，驗證模組間互動
- **Regression**: 回歸測試，確保修改未破壞既有功能
- **Smoke**: 冒煙測試，快速驗證核心功能可用性
- **Performance**: 效能測試，驗證系統效能指標
- **Security**: 安全測試，驗證安全性漏洞

---

## 範例：完整 Test Case

### TC_LOGIN_AUTH_001_POS

| 欄位 | 內容 |
|------|------|
| **Test Case ID** | TC_LOGIN_AUTH_001_POS |
| **Title** | 驗證使用有效帳號密碼可成功登入系統 |
| **Module** | Authentication |
| **Priority** | P0 |
| **Test Type** | Functional |
| **Author** | QA Team |
| **Created Date** | 2026-01-24 |

#### Preconditions
- 系統已啟動並可訪問
- 測試帳號 test@example.com 已在資料庫中建立
- 密碼為 Test@123

#### Test Data
| 參數 | 值 | 說明 |
|------|-----|------|
| URL | https://app.example.com/login | 登入頁面 |
| Username | test@example.com | 有效帳號 |
| Password | Test@123 | 正確密碼 |

#### Test Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | 開啟瀏覽器，訪問登入頁面 | 頁面正常載入，顯示登入表單 |
| 2 | 在 Username 欄位輸入 "test@example.com" | 欄位顯示輸入內容 |
| 3 | 在 Password 欄位輸入 "Test@123" | 欄位顯示遮罩符號 |
| 4 | 點擊 "Login" 按鈕 | 按鈕變為 Loading 狀態 |

#### Expected Result
- 頁面跳轉至 /dashboard
- URL 變更為 https://app.example.com/dashboard
- 右上角顯示用戶名稱 "test@example.com"
- 無錯誤訊息顯示
- 回應時間 < 3 秒

#### Status
- [x] Pass

#### Notes
- 測試環境：Chrome 120, Windows 11
- 執行日期：2026-01-24
