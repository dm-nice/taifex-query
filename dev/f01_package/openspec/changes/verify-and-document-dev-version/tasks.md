# F01 Fetcher 重構任務清單 (v6.0 → v7.0)

**狀態**: Tasks Phase  
**優先級分組**: 文檔完善 → 代碼可維護性 → 測試驗證 → 部署  
**測試數據**: 2025-12-12 歷史數據  
**預計工時**: ~3-4 小時

---

## 📋 任務執行順序

### Phase 1: 文檔完善 (Task 1-5)
### Phase 2: 代碼改進 (Task 6-9)
### Phase 3: 測試驗證 (Task 10-13)
### Phase 4: 部署 (Task 14-16)

---

# 【Phase 1】文檔完善

## Task 1: 模組級文檔增強

**任務 ID**: T1-DOC-MODULE  
**優先級**: ⭐⭐⭐⭐⭐ (高)  
**預計工時**: 30 分鐘  
**依賴**: 無

### 描述
增強 `f01_fetcher.py` 頂部的模組文檔，補充完整的 API 說明、限制說明和依賴說明。

### 具體改進
在模組頂部 docstring 中添加以下內容：

```python
"""
f01_fetcher.py - 台指期貨外資未平倉淨口數抓取模組 v7.0

【模組功能】
- 從 TAIFEX 網站抓取台指期貨外資未平倉資料
- 提供統一的 fetch(date: str) -> str 介面
- 自動偵測 MultiIndex 和單層表頭格式
- 完整的錯誤處理和日誌記錄

【主要入口】
- fetch(date: str) -> str
  入參: 日期字串 (YYYY-MM-DD 格式)
  返值: 統一格式的文字結果
  
  成功範例: "2025.12.12  F01: 台指期貨外資 [未平倉] [多空淨額] : -31,008 口 [TAIFEX]"
  失敗範例: "F01 錯誤: 連線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)"

【重要限制】
- TAIFEX API 端點無視日期參數，永遠返回最後交易日資料
- 若要支援歷史日期查詢，需使用 Selenium 或其他完整瀏覽器自動化
- 表格格式可能隨 TAIFEX 網站更新而改變，需定期驗證

【依賴套件】
- requests >= 2.28.0 (HTTP 請求)
- pandas >= 1.5.0 (表格解析)
- lxml >= 4.9.0 (HTML 解析，可選)
- beautifulsoup4 >= 4.11.0 (HTML 解析備選)

【版本歷史】
- v5.0: 初始版本 + 錯誤日誌增強
- v6.0: 增加 timestamp 和 context 參數
- v7.0: 完善文檔、改進代碼結構（當前）

【錯誤代碼表】
| 錯誤類型 | 原因 | 解決方案 |
|---------|------|--------|
| 日期格式錯誤 | 輸入格式非 YYYY-MM-DD | 檢查日期格式 |
| 連線逾時 | 網路延遲或 TAIFEX 無回應 | 檢查網路、稍後重試 |
| HTTP 錯誤 | 伺服器返回 4xx/5xx | 檢查 API 端點 |
| HTML 解析失敗 | 表格格式改變 | 更新欄位搜尋邏輯 |
| 無交易資料 | 假日或休市日 | 改查交易日期 |

【日誌配置】
模組使用 Python logging，預設級別為 INFO
- INFO: 主要操作（開始抓取、完成、失敗）
- DEBUG: 流程分支（格式偵測、欄位搜尋）
- ERROR: 無法恢復的異常
"""
```

### 驗收標準
- ✅ 模組文檔包含【功能】【入口】【限制】【依賴】【版本】【錯誤表】【日誌】7 個部分
- ✅ 至少包含 2 個具體的成功/失敗輸出範例
- ✅ 依賴套件列出版本要求
- ✅ 錯誤代碼表覆蓋所有 5 種異常類型

### 檢查清單
- [ ] 頂部文檔已更新
- [ ] 所有 7 個部分都齊全
- [ ] 範例格式與實際一致
- [ ] 可讀性良好，無拼寫錯誤

---

## Task 2: fetch() 函數文檔增強

**任務 ID**: T2-DOC-FETCH  
**優先級**: ⭐⭐⭐⭐⭐ (高)  
**預計工時**: 30 分鐘  
**依賴**: T1

### 描述
補充 `fetch(date: str) -> str` 的完整 docstring，包含 Args、Returns、Raises 和使用範例。

### 具體改進
將現有的簡陋文檔替換為完整版本：

```python
def fetch(date: str) -> str:
    """
    抓取指定日期的台指期貨外資未平倉資料
    
    【功能說明】
    從 TAIFEX 網站的 futContractsDate API 抓取台指期貨外資未平倉資料。
    由於 API 限制，實際返回的是最後交易日資料，而非指定日期資料。
    
    【參數】
    Args:
        date (str): 日期字串，格式必須為 YYYY-MM-DD
                    範例: "2025-12-12"
                    
    【返回值】
    Returns:
        str: 統一格式的文字字串，包含以下情況：
        
        1. 成功情況 (包含外資資料):
           格式: "{date}  F01: 台指期貨外資 [未平倉] [多空淨額] : {net} 口 [TAIFEX]"
           範例: "2025.12.12  F01: 台指期貨外資 [未平倉] [多空淨額] : -31,008 口 [TAIFEX]"
           
        2. 失敗情況 (可恢復的異常):
           格式: "F01 錯誤: {錯誤訊息} [TAIFEX]"
           範例: "F01 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]"
           
        3. 異常情況 (需增強上下文):
           格式: "F01 錯誤: {訊息} [TAIFEX] ({timestamp}, {context})"
           範例: "F01 錯誤: 連線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)"
    
    【異常處理】
    Raises:
        (函數不拋出異常，所有異常都被捕捉並轉為文字返回)
        
        但會記錄以下異常類型到日誌：
        
        1. ValueError - 日期格式驗證失敗
           觸發時機: 輸入不符 YYYY-MM-DD 格式
           日誌級別: INFO
           返回範例: "F01 錯誤: 日期格式錯誤，請使用 YYYY-MM-DD [TAIFEX]"
           
        2. requests.Timeout - 網路連線逾時
           觸發時機: HTTP 請求超過 30 秒無回應
           日誌級別: ERROR + context = {timeout: 30}
           返回範例: "F01 錯誤: 連線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)"
           
        3. requests.HTTPError - HTTP 狀態碼異常 (4xx/5xx)
           觸發時機: TAIFEX 伺服器返回錯誤碼
           日誌級別: ERROR + context = {status_code: xxx}
           返回範例: "F01 錯誤: HTTP 錯誤 404 [TAIFEX] (2025-12-15 14:30:45, status_code=404)"
           
        4. requests.RequestException - 其他網路異常
           觸發時機: DNS 解析失敗、連線被拒等
           日誌級別: ERROR
           返回範例: "F01 錯誤: 網路請求失敗: [Errno 11001] getaddrinfo failed [TAIFEX]"
           
        5. Exception - 未預期的異常
           觸發時機: HTML 解析、邏輯計算等意外錯誤
           日誌級別: ERROR (使用 logger.exception 記錄完整 traceback)
           返回範例: "F01 錯誤: 未預期的錯誤: index out of range [TAIFEX]"
    
    【使用範例】
    
    Example 1 - 正常使用:
        >>> result = fetch("2025-12-12")
        >>> print(result)
        2025.12.12  F01: 台指期貨外資 [未平倉] [多空淨額] : -31,008 口 [TAIFEX]
    
    Example 2 - 日期格式錯誤:
        >>> result = fetch("2025-12/12")  # 錯誤格式
        >>> print(result)
        F01 錯誤: 日期格式錯誤，請使用 YYYY-MM-DD [TAIFEX]
    
    Example 3 - 網路異常:
        >>> result = fetch("2025-12-12")  # 當網路無法連接時
        >>> print(result)
        F01 錯誤: 連線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)
    
    Example 4 - 假日查詢:
        >>> result = fetch("2025-12-14")  # 假日
        >>> print(result)
        F01 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]
    
    【注意事項】
    - 函數會自動將日期轉換為 TAIFEX API 格式 (YYYY/MM/DD)
    - 由於 API 限制，任何日期輸入都返回最後交易日的資料
    - 函數使用 30 秒逾時設定，用於檢測卡住的連線
    - 所有異常都會記錄到 logger，支援日誌分析和追蹤
    """
```

### 驗收標準
- ✅ docstring 包含【功能說明】【參數】【返回值】【異常處理】【使用範例】【注意事項】
- ✅ 返回值說明包含 3 種情況（成功、失敗、異常）的格式和範例
- ✅ 異常處理說明 5 種異常的觸發時機、日誌級別、返回值
- ✅ 至少 4 個具體的使用範例，覆蓋成功、失敗、異常、邊界情況

### 檢查清單
- [ ] 函數文檔已更新
- [ ] 包含【功能說明】
- [ ] 包含完整 Args 說明
- [ ] 包含完整 Returns 說明（3 種情況）
- [ ] 包含完整 Raises 說明（5 種異常）
- [ ] 包含 4+ 個使用範例
- [ ] 包含【注意事項】
- [ ] 格式清晰，無拼寫錯誤

---

## Task 3: format_f01_output() 函數文檔增強

**任務 ID**: T3-DOC-FORMAT  
**優先級**: ⭐⭐⭐⭐ (高)  
**預計工時**: 20 分鐘  
**依賴**: T1

### 描述
補充 `format_f01_output()` 的完整 docstring，詳細說明 timestamp 和 context 參數的用法。

### 具體改進
替換現有文檔為完整版本：

```python
def format_f01_output(
    date: str,
    status: str,
    data: Optional[Dict] = None,
    error: Optional[str] = None,
    timestamp: Optional[str] = None,
    context: Optional[Dict] = None
) -> str:
    """
    格式化 F01 輸出為統一文字格式 v7.0
    
    【功能說明】
    將抓取結果（成功/失敗/異常）轉換為標準化的文字格式。
    支援多層級的錯誤上下文記錄，便於問題追蹤和日誌分析。
    
    【參數說明】
    Args:
        date (str): 查詢日期 (YYYY-MM-DD 格式)
                    - 僅用於失敗訊息的定位（成功時不顯示日期）
                    - 範例: "2025-12-12"
        
        status (str): 操作狀態，可選值：
                    - "success": 成功抓取資料
                    - "failed": 可恢復的失敗（假日、無資料等）
                    - "error": 無法恢復的異常（網路、解析等）
        
        data (Optional[Dict]): 成功時的資料字典
                    只在 status="success" 時使用
                    結構:
                    {
                        "net_position": int,      # 多空淨額 (必須)
                        "long_position": int,     # 多方口數 (可選)
                        "short_position": int,    # 空方口數 (可選)
                        "source": str            # 資料來源 (預設 "TAIFEX")
                    }
                    範例: {"net_position": -31008, "long_position": 45000, 
                           "short_position": 76008, "source": "TAIFEX"}
        
        error (Optional[str]): 失敗或異常時的錯誤訊息
                    - 應為使用者友善的簡短訊息
                    - 範例: "連線逾時，請檢查網路連線"
                    - 範例: "該日無交易資料（可能是假日或休市日）"
        
        timestamp (Optional[str]): [v7.0 新增] 異常發生時間戳
                    只在 status="error" 時使用，搭配 error 使用
                    格式: "YYYY-MM-DD HH:MM:SS"
                    範例: "2025-12-15 14:30:45"
                    生成方式: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        context (Optional[Dict]): [v7.0 新增] 異常上下文字典
                    只在 status="error" 時使用，記錄詳細信息便於追蹤
                    常見欄位:
                    - "timeout": 整數，逾時秒數 (如 30)
                    - "status_code": 整數，HTTP 狀態碼 (如 404)
                    - "step": 字串，失敗步驟 (如 "html_parsing")
                    範例: {"timeout": 30}
                    範例: {"status_code": 404}
    
    【返回值】
    Returns:
        str: 格式化後的統一文字字串
        
        格式化規則:
        
        1. 成功 (status="success" + data):
           格式: "{date}  F01: 台指期貨外資 [未平倉] [多空淨額] : {net:,} 口 [TAIFEX]"
           說明: 日期用點號分隔 (2025.12.12 格式)，數字用逗號千分位
           範例: "2025.12.12  F01: 台指期貨外資 [未平倉] [多空淨額] : -31,008 口 [TAIFEX]"
        
        2. 失敗 (status="failed" + error):
           格式: "F01 錯誤: {error} [TAIFEX]"
           說明: 無時間戳和上下文
           範例: "F01 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]"
        
        3. 異常 (status="error" + error + timestamp):
           基礎格式: "F01 錯誤: {error} [TAIFEX] ({timestamp}"
           說明: 包含時間戳，用於精確定位
           範例: "F01 錯誤: 連線逾時 [TAIFEX] (2025-12-15 14:30:45)"
        
        4. 異常+上下文 (status="error" + error + timestamp + context):
           完整格式: "F01 錯誤: {error} [TAIFEX] ({timestamp}, context_str)"
           說明: 包含時間戳和詳細上下文
           上下文格式化規則:
           - "timeout" 值後加 "s" (如 timeout=30s)
           - 其他值直接格式化 (如 status_code=404)
           - 多個欄位用逗號分隔
           範例: "F01 錯誤: 連線逾時 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)"
           範例: "F01 錯誤: HTTP 錯誤 404 [TAIFEX] (2025-12-15 14:30:45, status_code=404)"
    
    【內部行為】
    - 成功情況：不記錄日誌
    - failed 情況：logger.warning() 記錄警告
    - error 情況：logger.error() 記錄錯誤信息
    - 敏感信息過濾：URL 和完整 traceback 不寫入日誌
    
    【使用範例】
    
    Example 1 - 成功情況:
        >>> result = format_f01_output(
        ...     date="2025-12-12",
        ...     status="success",
        ...     data={
        ...         "net_position": -31008,
        ...         "long_position": 45000,
        ...         "short_position": 76008,
        ...         "source": "TAIFEX"
        ...     }
        ... )
        >>> print(result)
        2025.12.12  F01: 台指期貨外資 [未平倉] [多空淨額] : -31,008 口 [TAIFEX]
    
    Example 2 - 失敗情況（假日）:
        >>> result = format_f01_output(
        ...     date="2025-12-14",
        ...     status="failed",
        ...     error="該日無交易資料（可能是假日或休市日）"
        ... )
        >>> print(result)
        F01 錯誤: 該日無交易資料（可能是假日或休市日） [TAIFEX]
    
    Example 3 - 異常情況（逾時，只有時間戳）:
        >>> result = format_f01_output(
        ...     date="2025-12-12",
        ...     status="error",
        ...     error="連線逾時，請檢查網路連線",
        ...     timestamp="2025-12-15 14:30:45"
        ... )
        >>> print(result)
        F01 錯誤: 連線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45)
    
    Example 4 - 異常情況（逾時+上下文）:
        >>> result = format_f01_output(
        ...     date="2025-12-12",
        ...     status="error",
        ...     error="連線逾時，請檢查網路連線",
        ...     timestamp="2025-12-15 14:30:45",
        ...     context={"timeout": 30}
        ... )
        >>> print(result)
        F01 錯誤: 連線逾時，請檢查網路連線 [TAIFEX] (2025-12-15 14:30:45, timeout=30s)
    
    Example 5 - 異常情況（HTTP 錯誤+上下文）:
        >>> result = format_f01_output(
        ...     date="2025-12-12",
        ...     status="error",
        ...     error="HTTP 錯誤 404",
        ...     timestamp="2025-12-15 14:30:45",
        ...     context={"status_code": 404}
        ... )
        >>> print(result)
        F01 錯誤: HTTP 錯誤 404 [TAIFEX] (2025-12-15 14:30:45, status_code=404)
    
    【向後兼容性】
    - v5.0 的調用方式仍然支援 (不傳 timestamp/context 也能運作)
    - 新增參數都是可選的，不破壞現有代碼
    """
```

### 驗收標準
- ✅ docstring 包含【功能說明】【參數說明】【返回值】【內部行為】【使用範例】【向後兼容性】
- ✅ 參數說明詳細，包含格式、範例、生成方式
- ✅ 返回值說明 4 種情況的格式規則和範例
- ✅ 至少 5 個使用範例，覆蓋所有情況

### 檢查清單
- [ ] 函數文檔已更新
- [ ] 包含【功能說明】
- [ ] 包含完整 Args 說明（每個參數都有格式和範例）
- [ ] 包含完整 Returns 說明（4 種情況）
- [ ] 包含【內部行為】
- [ ] 包含 5+ 個使用範例
- [ ] 包含【向後兼容性】
- [ ] 格式清晰，無拼寫錯誤

---

## Task 4: 輔助函數文檔增強

**任務 ID**: T4-DOC-HELPER  
**優先級**: ⭐⭐⭐⭐ (高)  
**預計工時**: 30 分鐘  
**依賴**: T1

### 描述
補充以下輔助函數的完整 docstring：
- `convert_to_int(value) -> int`
- `find_column_multiindex(df, keywords) -> Optional[tuple]`
- `find_column_single(df, possible_names) -> Optional[str]`
- `extract_foreign_data_multiindex(df, date) -> Dict`
- `extract_foreign_data_single(df, date) -> Dict`

### 具體改進
每個函數都要補充：
1. 【功能說明】- 2-3 句簡要說明
2. 【參數說明】- Args 詳細
3. 【返回值說明】- Returns 詳細
4. 【異常說明】- 可能返回的錯誤結構
5. 【使用範例】- 1-2 個真實範例

### 檢查清單 (convert_to_int 為例)
```python
def convert_to_int(value) -> int:
    """
    將字串轉換為整數，安全處理千分位逗號和空值。
    
    【功能說明】
    用於解析 HTML 表格中的數字字串，自動移除千分位逗號，
    並妥善處理 NaN、空字串等邊界情況。
    
    【參數說明】
    Args:
        value: 待轉換的值，可為以下類型：
            - str: 數字字串，可包含千分位逗號 (如 "45,000" 或 "45000")
            - int: 直接整數
            - float: 浮點數，會被轉為整數
            - np.nan / pd.NA: 空值，返回 0
            - None: 空值，返回 0
    
    【返回值】
    Returns:
        int: 轉換後的整數值
        - 成功: 轉換後的正確整數
        - 失敗: 0（用於表示無效或缺失值）
    
    【邊界情況】
    - "45,000" → 45000 ✓
    - "45000" → 45000 ✓
    - "" → 0 ✓
    - None → 0 ✓
    - np.nan → 0 ✓
    - "abc" → 0 ✓
    
    【使用範例】
    Example 1:
        >>> convert_to_int("45,000")
        45000
    
    Example 2:
        >>> convert_to_int(None)
        0
    """
```

### 驗收標準
- ✅ 所有 5 個輔助函數都有完整 docstring
- ✅ 每個函數都包含【功能說明】【參數說明】【返回值說明】
- ✅ 複雜函數包含【邊界情況】或【異常說明】
- ✅ 每個函數都有至少 1 個使用範例

---

## Task 5: 代碼內聯註釋補充

**任務 ID**: T5-DOC-INLINE  
**優先級**: ⭐⭐⭐⭐ (中)  
**預計工時**: 30 分鐘  
**依賴**: T1-T4

### 描述
在核心邏輯複雜的地方補充內聯註釋，解釋「為什麼」而不是「做什麼」。

### 具體改進位置

**位置 1: fetch() 中的表格格式偵測**
```python
# 根據表格類型處理
# MultiIndex 通常表示複雜的多層表頭（如「未平倉」→「多方」→「口數」）
# 單層表頭表示扁平結構（如「身份別」「多方口數」「空方口數」）
if isinstance(df.columns, pd.MultiIndex):
    logger.debug("偵測到 MultiIndex 表頭")
    result_dict = extract_foreign_data_multiindex(df, date)
else:
    logger.debug("偵測到單層表頭")
    result_dict = extract_foreign_data_single(df, date)
```

**位置 2: format_f01_output() 中的上下文格式化**
```python
# 格式化上下文時，timeout 需要特殊處理（加 "s" 單位）
# 其他欄位直接拼接（如 status_code=404）
context_parts = []
for k, v in context.items():
    if k == "timeout":
        context_parts.append(f"{k}={v}s")  # timeout 特殊處理
    else:
        context_parts.append(f"{k}={v}")    # 其他直接拼接
```

**位置 3: extract_foreign_data_*() 中的欄位搜尋**
```python
# 尋找外資行時使用 isin() 檢查多個可能值
# 因為 TAIFEX 可能用「外資及陸資」或「外資」表示同一類型
foreign_rows = df[df[trader_col].isin(['外資及陸資', '外資'])]
```

### 檢查清單
- [ ] 關鍵邏輯分支都有註釋
- [ ] 表格格式偵測邏輯有註釋
- [ ] 欄位搜尋邏輯有註釋
- [ ] 異常處理邏輯有註釋
- [ ] 註釋解釋「為什麼」，不是重複代碼
- [ ] 註釋清晰簡潔，無冗餘

---

# 【Phase 2】代碼改進

## Task 6: 類型提示完善 - TypedDict 定義

**任務 ID**: T6-TYPE-TYPEDDICT  
**優先級**: ⭐⭐⭐⭐ (中)  
**預計工時**: 20 分鐘  
**依賴**: T1-T5

### 描述
在模組頂部定義 TypedDict，用於精確定義複雜字典的結構。

### 具體改進
在 `from typing import` 之後添加：

```python
from typing import Dict, Optional, TypedDict

class ForeignDataDict(TypedDict):
    """外資資料字典結構（用於 format_f01_output 的 data 參數）"""
    net_position: int          # 多空淨額
    long_position: int         # 多方未平倉口數
    short_position: int        # 空方未平倉口數
    source: str               # 資料來源（通常為 "TAIFEX"）

class ErrorContextDict(TypedDict, total=False):
    """錯誤上下文字典結構（用於 format_f01_output 的 context 參數）"""
    timeout: int              # 逾時秒數
    status_code: int          # HTTP 狀態碼
    step: str                 # 失敗步驟名稱
    error_type: str           # 異常類型
```

然後更新函數簽名：
```python
def format_f01_output(
    date: str,
    status: str,
    data: Optional[ForeignDataDict] = None,
    error: Optional[str] = None,
    timestamp: Optional[str] = None,
    context: Optional[ErrorContextDict] = None
) -> str:
```

### 驗收標準
- ✅ TypedDict 已在模組頂部定義
- ✅ ForeignDataDict 包含所有 4 個欄位
- ✅ ErrorContextDict 標記為 total=False（可選欄位）
- ✅ 函數簽名已使用 TypedDict

### 檢查清單
- [ ] TypedDict 已定義
- [ ] 函數簽名已更新
- [ ] IDE 類型檢查無誤
- [ ] 運行測試通過

---

## Task 7: 日誌策略統一

**任務 ID**: T7-LOG-UNIFIED  
**優先級**: ⭐⭐⭐⭐ (中)  
**預計工時**: 30 分鐘  
**依賴**: T1-T6

### 描述
統一代碼中所有的日誌記錄，確保級別、格式和上下文一致。

### 具體改進

**日誌級別統一**:
- `logger.info`: 操作開始 / 操作完成 / 主流程進度
- `logger.debug`: 格式偵測 / 欄位搜尋 / 分支判斷
- `logger.warning`: 可恢復的異常 / failed 狀態
- `logger.error`: 無法恢復的異常 / error 狀態

**日誌上下文統一** - 添加公共日誌輔助函數：
```python
def _log_fetch_step(level: str, message: str, date: str, **context):
    """
    統一的日誌記錄函數，確保所有日誌都包含必要上下文。
    
    Args:
        level: 日誌級別 ("info", "debug", "warning", "error")
        message: 日誌訊息
        date: 查詢日期
        **context: 額外的上下文信息
    """
    log_fn = getattr(logger, level)
    log_fn(
        f"[F01] {message}",
        extra={"date": date, **context}
    )
```

**應用位置**:

1. fetch() 開始：
   ```python
   logger.info(f"[F01] 開始抓取 {date} 資料")
   ```

2. 表格解析成功：
   ```python
   logger.debug(f"[F01] {date} 偵測到表格格式: {'MultiIndex' if is_multiindex else '單層'}")
   ```

3. 異常記錄：
   ```python
   timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   logger.error(
       f"[F01] {date} 連線逾時",
       extra={"timestamp": timestamp, "timeout": 30}
   )
   ```

### 驗收標準
- ✅ 所有日誌都包含 [F01] 前綴
- ✅ 所有日誌都包含 date 上下文
- ✅ 關鍵異常都記錄 timestamp 和詳細上下文
- ✅ 日誌級別符合規定（info/debug/warning/error）

### 檢查清單
- [ ] 所有 logger.* 調用都已檢查
- [ ] 所有異常都有對應的 logger.error
- [ ] 日誌格式統一
- [ ] 上下文信息完整
- [ ] 敏感信息已過濾

---

## Task 8: 異常類型和返回值統一

**任務 ID**: T8-EXCEPTION-UNIFIED  
**優先級**: ⭐⭐⭐ (中)  
**預計工時**: 20 分鐘  
**依賴**: T6-T7

### 描述
確保所有異常都被正確捕捉、記錄和轉為統一格式的返回值。

### 具體改進

**異常對照表**:
| 異常類型 | 觸發條件 | 日誌級別 | 返回格式 | 上下文 |
|---------|--------|--------|--------|------|
| ValueError | 日期格式驗證失敗 | INFO | F01 錯誤: 日期格式錯誤 | - |
| Timeout | HTTP 請求超過 30 秒 | ERROR | F01 錯誤: 連線逾時 | timeout=30s |
| HTTPError | 伺服器返回 4xx/5xx | ERROR | F01 錯誤: HTTP 錯誤 {code} | status_code=xxx |
| RequestException | DNS/連線其他異常 | ERROR | F01 錯誤: 網路請求失敗 | - |
| Exception | 未預期的異常 | ERROR | F01 錯誤: 未預期的錯誤 | (traceback 不入返回值) |

**驗收檢查**:
```python
# 驗證 fetch() 中所有 except 塊都有正確的返回值
def fetch(date: str) -> str:
    try:
        # 主邏輯
        pass
    except ValueError:
        # ✅ 應該返回: F01 錯誤: 日期格式錯誤...
        pass
    except requests.Timeout:
        # ✅ 應該返回: F01 錯誤: 連線逾時... (timestamp + timeout=30s)
        pass
    except requests.HTTPError as e:
        # ✅ 應該返回: F01 錯誤: HTTP 錯誤 {status_code}... (timestamp + status_code=xxx)
        pass
    except requests.RequestException:
        # ✅ 應該返回: F01 錯誤: 網路請求失敗...
        pass
    except Exception:
        # ✅ 應該返回: F01 錯誤: 未預期的錯誤... (不含詳細 traceback)
        pass
```

### 驗收標準
- ✅ 5 種異常都被捕捉
- ✅ 每種異常都有日誌記錄
- ✅ 每種異常都有格式化的返回值
- ✅ 異常返回值符合 v5.0 格式

### 檢查清單
- [ ] 所有異常都被正確捕捉
- [ ] 所有異常都有 logger.error 記錄
- [ ] 異常返回值格式統一
- [ ] Timeout/HTTPError 有上下文信息
- [ ] 敏感信息（詳細 traceback）不返回給用戶

---

## Task 9: 代碼風格和結構驗證

**任務 ID**: T9-CODE-STYLE  
**優先級**: ⭐⭐⭐ (低)  
**預計工時**: 15 分鐘  
**依賴**: T6-T8

### 描述
驗證代碼風格，確保沒有不必要的改動和代碼質量。

### 檢查清單
- [ ] 沒有引入新的依賴
- [ ] 函數簽名保持不變（向後兼容）
- [ ] 變數命名一致（snake_case）
- [ ] 函數命名一致（snake_case）
- [ ] 常用的 Python 風格（PEP 8）
- [ ] 沒有重複代碼
- [ ] 沒有無用的 import
- [ ] 代碼行長不超過 120 個字符

---

# 【Phase 3】測試驗證

## Task 10: 單元測試執行 - 正常路徑

**任務 ID**: T10-TEST-HAPPY  
**優先級**: ⭐⭐⭐⭐⭐ (高)  
**預計工時**: 20 分鐘  
**依賴**: T1-T9

### 描述
使用 2025-12-12 的歷史數據，測試 f01_fetcher_dev.py 的正常路徑。

### 測試步驟
1. 讀取 data/2025-12-12_0719_f01_fetcher.txt 中的預期輸出
2. 執行 fetch("2025-12-12")
3. 對比輸出格式和數字

### 測試程式碼
```python
# test_f01_fetcher_v7.py
import sys
sys.path.insert(0, r'c:\Taifex\dev\f01_package')
from f01_fetcher_dev import fetch

def test_fetch_2025_12_12():
    """測試 2025-12-12 的資料"""
    result = fetch("2025-12-12")
    expected = "2025.12.12  F01: 台指期貨外資 [未平倉] [多空淨額] : -31,008 口 [TAIFEX]"
    
    print(f"預期: {expected}")
    print(f"實際: {result}")
    
    # 驗證格式
    assert "F01" in result, "輸出應包含 F01"
    assert "2025.12.12" in result or "台指期貨" in result, "輸出應包含日期或產品名稱"
    assert "-31,008" in result, "輸出應包含正確的淨額數字"
    assert "TAIFEX" in result, "輸出應包含 TAIFEX 來源"
    
    # 完全匹配
    assert result == expected, f"輸出不匹配：\n預期: {expected}\n實際: {result}"
    
    print("✅ 測試通過")

if __name__ == "__main__":
    test_fetch_2025_12_12()
```

### 驗收標準
- ✅ fetch("2025-12-12") 能成功執行
- ✅ 輸出格式與預期一致
- ✅ 淨額數字 -31,008 正確
- ✅ 無異常拋出

---

## Task 11: 單元測試執行 - 異常路徑

**任務 ID**: T11-TEST-EXCEPTION  
**優先級**: ⭐⭐⭐⭐ (高)  
**預計工時**: 20 分鐘  
**依賴**: T10

### 描述
測試所有 5 種異常的正確處理和記錄。

### 測試用例

1. **日期格式驗證異常**:
   ```python
   result = fetch("2025-12/12")  # 錯誤格式
   assert "日期格式錯誤" in result
   ```

2. **假日 / 無資料**:
   ```python
   result = fetch("2025-12-14")  # 假日（預計失敗）
   assert "無交易資料" in result or "錯誤" in result
   ```

3. **網路異常模擬** (使用 mock):
   ```python
   from unittest.mock import patch
   with patch('requests.get') as mock_get:
       mock_get.side_effect = requests.Timeout
       result = fetch("2025-12-12")
       assert "連線逾時" in result
       assert "timeout=30s" in result
   ```

4. **HTTP 404 模擬**:
   ```python
   with patch('requests.get') as mock_get:
       mock_get.return_value.raise_for_status.side_effect = \
           requests.HTTPError(response=Mock(status_code=404))
       result = fetch("2025-12-12")
       assert "HTTP 錯誤 404" in result
   ```

5. **未預期的異常**:
   ```python
   with patch('pd.read_html') as mock_read:
       mock_read.side_effect = Exception("未預期的錯誤")
       result = fetch("2025-12-12")
       assert "未預期的錯誤" in result
   ```

### 驗收標準
- ✅ 日期格式驗證異常被正確處理
- ✅ 無資料情況返回 failed 訊息
- ✅ 5 種網路異常都被正確捕捉
- ✅ 異常訊息符合 v5.0 格式
- ✅ 異常被記錄到日誌

---

## Task 12: 對比測試 - dev vs prod

**任務 ID**: T12-TEST-COMPARE  
**優先級**: ⭐⭐⭐⭐⭐ (高)  
**預計工時**: 30 分鐘  
**依賴**: T10-T11

### 描述
用 2025-12-12 的數據對比 f01_fetcher_dev.py 和 modules/f01_fetcher.py 的輸出。

### 對比測試程式碼
```python
# test_compare_dev_vs_prod.py
import sys
sys.path.insert(0, r'c:\Taifex\dev\f01_package')
sys.path.insert(0, r'c:\Taifex')

from f01_fetcher_dev import fetch as fetch_dev
from modules.f01_fetcher import fetch as fetch_prod

def test_compare_2025_12_12():
    """對比 dev 和 prod 版本"""
    
    print("=" * 60)
    print("F01 Fetcher - Dev vs Prod 對比測試")
    print("=" * 60)
    
    # 運行兩個版本
    result_dev = fetch_dev("2025-12-12")
    result_prod = fetch_prod("2025-12-12")
    
    print(f"\n【Dev 版本】")
    print(f"  {result_dev}")
    
    print(f"\n【Prod 版本】")
    print(f"  {result_prod}")
    
    # 對比結果
    print(f"\n【對比結果】")
    if result_dev == result_prod:
        print(f"  ✅ 完全相同")
        return True
    else:
        print(f"  ❌ 不相同")
        print(f"\n  差異分析:")
        print(f"    Dev:  {repr(result_dev)}")
        print(f"    Prod: {repr(result_prod)}")
        
        # 提取數字進行對比
        import re
        dev_match = re.search(r':\s*([-\d,]+)\s*口', result_dev)
        prod_match = re.search(r':\s*([-\d,]+)\s*口', result_prod)
        
        if dev_match and prod_match:
            dev_num = dev_match.group(1)
            prod_num = prod_match.group(1)
            print(f"    Dev 數字:  {dev_num}")
            print(f"    Prod 數字: {prod_num}")
            
            if dev_num == prod_num:
                print(f"    💡 數字相同，可能是格式差異")
        
        return False

if __name__ == "__main__":
    success = test_compare_2025_12_12()
    sys.exit(0 if success else 1)
```

### 驗收標準
- ✅ dev 和 prod 的輸出完全相同
- ✅ 日期格式相同（2025.12.12）
- ✅ 淨額數字相同（-31,008）
- ✅ 格式和單位相同

### 檢查清單
- [ ] 兩版本輸出完全匹配
- [ ] 日期、數字、格式都一致
- [ ] 沒有額外的空格或換行符
- [ ] 測試代碼可重複執行

---

## Task 13: 回歸測試 - 邊界情況

**任務 ID**: T13-TEST-EDGE  
**優先級**: ⭐⭐⭐⭐ (中)  
**預計工時**: 20 分鐘  
**依賴**: T12

### 描述
測試邊界情況，確保代碼穩定性。

### 測試用例

| 用例 | 輸入 | 預期行為 |
|-----|------|---------|
| 有效日期-歷史 | "2025-12-12" | 返回該日資料或"無交易資料" |
| 有效日期-假日 | "2025-12-14" | 返回"無交易資料"或"該日無交易資料" |
| 無效日期-格式 | "2025-12-32" | 返回"日期格式錯誤" |
| 無效日期-格式 | "12/25/2025" | 返回"日期格式錯誤" |
| 無效日期-格式 | "2025.12.12" | 返回"日期格式錯誤" |
| 空值 | "" | 返回"日期格式錯誤" |
| None | None | 返回"日期格式錯誤"（如適用） |

### 驗收標準
- ✅ 邊界情況都被正確處理
- ✅ 無崩潰或未捕捉的異常
- ✅ 錯誤訊息清晰有用

---

# 【Phase 4】部署

## Task 14: 部署前檢查清單

**任務 ID**: T14-DEPLOY-CHECK  
**優先級**: ⭐⭐⭐⭐⭐ (高)  
**預計工時**: 15 分鐘  
**依賴**: T13

### 描述
執行部署前的最終檢查。

### 檢查清單

**文檔檢查**:
- [ ] 模組文檔完整（【功能】【入口】【限制】【依賴】【版本】【錯誤表】【日誌】）
- [ ] fetch() 文檔完整（【說明】【參數】【返回值】【異常】【範例】【注意】）
- [ ] format_f01_output() 文檔完整（【說明】【參數】【返回值】【行為】【範例】【兼容】）
- [ ] 所有輔助函數都有文檔
- [ ] 關鍵邏輯都有內聯註釋

**代碼檢查**:
- [ ] TypedDict 已定義且正確
- [ ] 所有函數都有返回值類型標註
- [ ] 日誌調用統一（[F01] 前綴 + 上下文）
- [ ] 5 種異常都被正確捕捉
- [ ] 無新增依賴
- [ ] 無破壞現有 API

**測試檢查**:
- [ ] 正常路徑測試通過（fetch("2025-12-12")）
- [ ] 異常路徑測試通過（5 種異常）
- [ ] Dev vs Prod 對比完全相同
- [ ] 邊界情況測試通過
- [ ] 所有日誌記錄正確

**版本檢查**:
- [ ] 版本號確認更新為 v7.0
- [ ] 變更日誌已更新
- [ ] 相關文件都已檢視

---

## Task 15: 備份和部署

**任務 ID**: T15-DEPLOY-BACKUP  
**優先級**: ⭐⭐⭐⭐⭐ (高)  
**預計工時**: 10 分鐘  
**依賴**: T14

### 描述
備份現有的生產版本，然後部署新版本。

### 部署步驟

```powershell
# Step 1: 備份現有版本
Copy-Item `
  -Path "c:\Taifex\modules\f01_fetcher.py" `
  -Destination "c:\Taifex\modules\f01_fetcher.py.backup.v6.0" `
  -Force

# Step 2: 複製新版本
Copy-Item `
  -Path "c:\Taifex\dev\f01_package\f01_fetcher_dev.py" `
  -Destination "c:\Taifex\modules\f01_fetcher.py" `
  -Force

# Step 3: 驗證
Get-Item "c:\Taifex\modules\f01_fetcher.py"
```

### 驗收標準
- ✅ 備份文件已創建
- ✅ 新版本已複製
- ✅ 文件權限正確

---

## Task 16: 最終驗證 - 生產環境

**任務 ID**: T16-DEPLOY-VERIFY  
**優先級**: ⭐⭐⭐⭐⭐ (高)  
**預計工時**: 15 分鐘  
**依賴**: T15

### 描述
在部署後驗證生產版本可用。

### 驗證步驟

```python
# 驗證新部署的版本
import sys
sys.path.insert(0, r'c:\Taifex')

from modules.f01_fetcher import fetch

print("【生產環境驗證】")
print("=" * 60)

# Test 1: 正常路徑
result = fetch("2025-12-12")
print(f"\n1. 正常路徑 (2025-12-12):")
print(f"   {result}")
assert "F01" in result, "應包含 F01"
assert "-31,008" in result, "應包含正確數字"
print("   ✅ 通過")

# Test 2: 異常路徑
result = fetch("2025-12/12")  # 錯誤格式
print(f"\n2. 異常路徑 (日期格式錯誤):")
print(f"   {result}")
assert "日期格式錯誤" in result, "應提示日期格式錯誤"
print("   ✅ 通過")

# Test 3: 日誌輸出
import logging
logger = logging.getLogger('modules.f01_fetcher')
handlers = logger.handlers
print(f"\n3. 日誌配置:")
print(f"   級別: {logger.level}")
print(f"   處理器: {len(handlers)} 個")
print("   ✅ 通過")

print("\n" + "=" * 60)
print("✅ 所有驗證通過，版本 v7.0 已成功部署")
print("=" * 60)
```

### 驗收標準
- ✅ fetch("2025-12-12") 返回預期結果
- ✅ 異常情況正確處理
- ✅ 日誌記錄正常
- ✅ 版本號已更新為 v7.0
- ✅ 沒有引入新問題

### 檢查清單
- [ ] modules/f01_fetcher.py 能正常 import
- [ ] fetch() 函數可正常調用
- [ ] 輸出格式符合 v5.0 標準
- [ ] 日誌記錄完整
- [ ] 與其他模組兼容

---

# 📊 任務統計

**總任務數**: 16  
**優先級分佈**:
- ⭐⭐⭐⭐⭐ (高): T1, T2, T3, T10, T11, T12, T14, T15, T16 (9 個)
- ⭐⭐⭐⭐ (中): T4, T5, T6, T7, T8, T9, T13 (7 個)

**階段分佈**:
- Phase 1 (文檔): 5 個 (T1-T5)
- Phase 2 (代碼): 4 個 (T6-T9)
- Phase 3 (測試): 4 個 (T10-T13)
- Phase 4 (部署): 3 個 (T14-T16)

**預計總工時**: 3.5-4 小時

---

## 🎯 執行順序

**建議按照 Phase 順序執行：**

1. **Phase 1 - 文檔完善** (3.5 小時)
   - T1 → T2 → T3 → T4 → T5

2. **Phase 2 - 代碼改進** (1.25 小時)
   - T6 → T7 → T8 → T9

3. **Phase 3 - 測試驗證** (1.5 小時)
   - T10 → T11 → T12 → T13

4. **Phase 4 - 部署** (0.75 小時)
   - T14 → T15 → T16

---

**任務日期**: 2025-12-15  
**任務創建者**: OpenSpec Framework  
**下一步**: 開始執行 Task 1 (T1-DOC-MODULE)
