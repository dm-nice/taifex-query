# Change Proposal: add-f11-taiex-api

## Summary

新增一個 `/api/stock/taiex` GET 端點，用於返回加權股價收盤指數。該端點會自動從 TWSE 官網抓取最新數據並以 JSON 格式返回。

## Change ID

`add-f11-taiex-api`

## Type

新功能 (Feature)

## Scope

- **Phase**: Phase 2 (代碼實現)
- **Module**: F11 (加權股價收盤指數)
- **Components**:
  - f11_openspec_dev.py (核心抓取模組)
  - f11_api.py (HTTP API 端點 - 可選)

## Why

使用者需要一個統一的 API 端點來獲取加權股價收盤指數，而不是直接調用爬蟲函數。

## What Changes

### ADDED Requirements

#### Requirement: 建立 fetch_taiex_index() 函數

**Scenario**: 抓取 TWSE 加權股價指數

- 訪問 <https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html>
- 使用 requests + BeautifulSoup 解析 HTML
- 提取最新的收盤指數值
- 返回統一格式的結果字串

#### Requirement: 格式化輸出

**Scenario**: 返回標準格式

- 成功: `2025.12.17  F11: 加權股價收盤指數 : 18254.50 [TWSE]`
- 失敗: `F11 錯誤: 該日無交易資料（可能是假日或休市日） [TWSE]`
- 異常: `F11 錯誤: [錯誤描述] [TWSE] (時間戳)`

#### Requirement: 異常處理

**Scenario**: 處理各種失敗情況

- 網路連線失敗（HTTP 4xx/5xx）
- 頁面結構改變（HTML 解析失敗）
- 假日無交易數據
- 伺服器無回應（timeout）

#### Requirement: 日誌記錄

**Scenario**: 完整的操作日誌

- 使用 Python logging 模組
- [F11] 前綴標識模組
- INFO: 主要操作
- DEBUG: 流程分支
- ERROR: 異常情況

## Impact

- 新增 1 個模組 (f11_fetcher_dev.py ~350 行)
- 新增 1 個測試套件 (test_f11_openspec.py ~250 行)
- 新增 2 份文檔 (design.md, tasks.md)

## Timeline

- Phase 1 (文檔): 1-2 小時
- Phase 2 (代碼): 2-3 小時
- Phase 3 (測試): 1-2 小時
- Phase 4 (部署): 0.5 小時
- **總計**: ~6-8 小時

## Risks

- TWSE 頁面結構改變時需要更新選擇器
- 非交易時段可能無數據
- 網路連線不穩定

## Implementation Strategy

1. 分析 TWSE 頁面結構 (HTML 檢查)
2. 開發 fetch 函數 (requests + BeautifulSoup)
3. 開發格式化函數 (輸出統一格式)
4. 完善異常處理 (5+ 異常類型)
5. 編寫測試套件 (15+ 個測試)
6. 部署到生產環境

## Approval Gate

此提案需要在開始實現之前被審核和批准。
