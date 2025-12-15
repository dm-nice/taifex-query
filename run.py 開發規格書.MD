# run.py 開發規格書

**程式名稱**: run.py
**功能**: 模組統一執行程式
**版本**: 2.1（UTF-8 包裝修復）
**最後更新**: 2025-12-15

---

## 📋 目錄

1. [程式概述](#程式概述)
2. [核心功能](#核心功能)
3. [架構設計](#架構設計)
4. [函式規格](#函式規格)
5. [執行流程](#執行流程)
6. [輸出規格](#輸出規格)
7. [錯誤處理](#錯誤處理)
8. [使用範例](#使用範例)
9. [維護指南](#維護指南)

---

## 程式概述

### 用途

`run.py` 是整個系統的**主控程式**，負責：
- 自動載入並執行所有 fetcher 模組
- 統一處理模組回傳結果
- 集中輸出 JSON 檔案和日誌
- 提供友善的中文介面給使用者

### 設計理念

```
┌─────────────────┐
│   使用者介面    │ ← 全中文顯示
├─────────────────┤
│     run.py      │ ← 混合模式（英文 key + 中文顯示）
├─────────────────┤
│  fetcher 模組   │ ← 回傳英文 key
└─────────────────┘
```

**混合模式**:
- 模組間通訊：使用英文 key
- 使用者介面：顯示中文訊息

### 不應修改的原則

⚠️ **一般開發者不需要修改 `run.py`**  
- fetcher 模組開發者：只需確保回傳格式正確
- 系統維護者：才需要了解 `run.py` 內部

---

## 核心功能

### 1. 模組自動載入

```python
# 自動掃描 dev/ 或 modules/ 資料夾
# 找到所有 xxx_fetcher.py 檔案
# 動態載入並執行
```

### 2. 統一執行介面

```bash
# 支援多種執行模式
python run.py                              # 今天日期
python run.py 2025-12-01                   # 指定日期
python run.py 2025-12-01 dev               # 驗收模式
python run.py 2025-12-01 dev --module f01  # 單一模組
```

### 3. 結果集中輸出

所有結果統一輸出到 `C:\Taifex\data\`:
- JSON 檔案：`YYYY-MM-DD_模組名稱.json`
- 日誌檔案：`YYYY-MM-DD_run.log`

### 4. 友善的中文介面

```
======================================================================
  📅 查詢日期: 2025-12-01
  ⏰ 執行時間: 2025-12-04 10:30:00
  🔧 執行模式: 驗收模式
======================================================================

📦 找到 3 個模組

[1/3] ──────────────────────────────────────────────────
執行模組: dev.f01_fetcher_dev
💾 檔案: 2025-12-04_f01_fetcher_dev_dev.json
  ✅ 狀態: 成功
  📊 台指期外資淨額 -29,032 口（多方 18,268，空方 47,300）
     • 多方口數: 18,268
     • 空方口數: 47,300
     • 淨額: -29,032
```

---

## 架構設計

### 程式結構

```python
# ===== 設定 =====
BASE_DIR = Path(r"C:\Taifex\data")
STATUS_ICONS = {...}

# ===== 核心函式 =====
def setup_logger()          # 設定日誌
def get_module_list()       # 取得模組列表
def validate_result_format() # 驗證回傳格式
def save_result()           # 儲存結果
def execute_module()        # 執行模組
def print_summary()         # 顯示摘要
def run()                   # 主執行函式
def validate_date()         # 驗證日期
def print_usage()           # 顯示說明
def main()                  # 程式進入點
```

### 資料流向

```
命令列參數
    ↓
解析參數（日期、模式、指定模組）
    ↓
取得模組列表（get_module_list）
    ↓
逐一執行模組（execute_module）
    ↓
    ├→ 載入模組（importlib）
    ├→ 呼叫 fetch()
    ├→ 驗證格式（validate_result_format）
    └→ 儲存結果（save_result）
    ↓
顯示統計報告
```

---

## 函式規格

### setup_logger(log_file: Path) -> logging.Logger

**功能**: 設定日誌記錄器

**參數**:
- `log_file`: 日誌檔案路徑

**回傳**: 配置好的 logger 物件

**特點**:
- 檔案 handler: 記錄詳細資訊（DEBUG 層級）
- 終端機 handler: 簡潔輸出（INFO 層級）
- 自動處理 UTF-8 編碼

**範例**:
```python
log_file = BASE_DIR / "2025-12-04_run.log"
logger = setup_logger(log_file)
logger.info("開始執行")
```

---

### get_module_list(folder: str, only_module: Optional[str]) -> List[str]

**功能**: 取得模組列表

**參數**:
- `folder`: 模組資料夾（"dev" 或 "modules"）
- `only_module`: 僅執行特定模組（可選）

**回傳**: 排序後的模組名稱列表

**邏輯**:
```python
# 1. 掃描資料夾中的 .py 檔案
# 2. 排除 _ 開頭的檔案（例如 __init__.py）
# 3. 組成完整模組路徑（例如 "dev.f01_fetcher"）
# 4. 如果指定特定模組，進行過濾
# 5. 排序後回傳
```

**範例**:
```python
# 取得 dev/ 下所有模組
modules = get_module_list("dev")
# ['dev.f01_fetcher_dev', 'dev.f02_fetcher_dev']

# 只取得特定模組
modules = get_module_list("dev", "f01_fetcher_dev")
# ['dev.f01_fetcher_dev']
```

---

### validate_result_format(result: Dict, module_name: str, query_date: str) -> Tuple[Dict, str]

**功能**: 驗證並正規化模組返回結果

**參數**:
- `result`: 模組回傳的結果
- `module_name`: 模組名稱
- `query_date`: 查詢日期

**回傳**: (正規化後的結果, 狀態碼)

**驗證項目**:
1. ✅ 是否為 dict 類型
2. ✅ 是否包含 "status" 欄位
3. ✅ 補充缺少的 "module" 和 "date" 欄位

**處理邏輯**:
```python
# 如果格式錯誤
if not isinstance(result, dict):
    return (invalid_result, "invalid")

# 如果缺少 status
if "status" not in result:
    return (invalid_result, "invalid")

# 補充缺少的欄位
if "module" not in result:
    result["module"] = module_short

return (result, status)
```

---

### execute_module(module_name: str, query_date: str, logger: logging.Logger) -> Tuple[Dict, str]

**功能**: 執行單一模組

**參數**:
- `module_name`: 模組完整名稱（例如 "dev.f01_fetcher_dev"）
- `query_date`: 查詢日期
- `logger`: 日誌記錄器

**回傳**: (執行結果, 狀態碼)

**執行流程**:
```python
try:
    # 1. 動態載入模組
    mod = importlib.import_module(module_name)
    
    # 2. 檢查是否有 fetch 函式
    if not hasattr(mod, 'fetch'):
        return (error_result, "error")
    
    # 3. 執行 fetch 函式
    result = mod.fetch(query_date)
    
    # 4. 驗證並正規化結果
    validated_result, status = validate_result_format(result, module_name, query_date)
    
    return (validated_result, status)
    
except ImportError:
    return (error_result, "error")
except Exception:
    return (error_result, "error")
```

---

### print_summary(result: Dict, status: str, logger: logging.Logger)

**功能**: 顯示執行摘要（中文）

**參數**:
- `result`: 執行結果
- `status`: 狀態碼
- `logger`: 日誌記錄器

**顯示邏輯**:
```python
# 1. 顯示狀態（中文）
logger.info(f"  {icon} 狀態: {status_zh}")

# 2. 顯示摘要或錯誤訊息
if "summary" in result:
    logger.info(f"  📊 {result['summary']}")
elif "error" in result:
    logger.info(f"  💬 {result['error']}")

# 3. 顯示資料內容（將英文 key 轉為中文）
if status == "success" and "data" in result:
    for key, value in result["data"].items():
        key_zh = KEY_MAPPING.get(key, key)
        logger.info(f"     • {key_zh}: {value:,}")
```

**英文 key 轉中文對照**:
```python
KEY_MAPPING = {
    "long_position": "多方口數",
    "short_position": "空方口數",
    "net_position": "淨額"
}
```

---

### run(query_date: str, dev_mode: bool, only_module: Optional[str])

**功能**: 主執行函式

**參數**:
- `query_date`: 查詢日期（YYYY-MM-DD）
- `dev_mode`: 是否為驗收模式
- `only_module`: 僅執行特定模組（可選）

**執行流程**:

```
1. 建立輸出目錄
   ↓
2. 設定參數（folder, mode, exec_day, log_file）
   ↓
3. 設定日誌記錄器
   ↓
4. 顯示標題
   ↓
5. 取得模組列表
   ↓
6. 逐一執行模組
   │  ├→ 執行模組（execute_module）
   │  ├→ 儲存結果（save_result）
   │  └→ 顯示摘要（print_summary）
   ↓
7. 顯示統計報告
```

---

## 執行流程

### 完整流程圖

```
使用者執行命令
    ↓
main() 解析參數
    ├─ 日期（query_date）
    ├─ 模式（dev_mode）
    └─ 模組（only_module）
    ↓
驗證日期格式
    ↓
呼叫 run()
    ↓
取得模組列表
    ↓
┌──────────────────────┐
│  逐一執行模組（迴圈）  │
├──────────────────────┤
│  1. execute_module   │
│     ├─ importlib     │
│     ├─ 呼叫 fetch()  │
│     └─ validate      │
│  2. save_result      │
│  3. print_summary    │
└──────────────────────┘
    ↓
顯示統計報告
    ↓
結束
```

### 模組執行細節

每個模組的執行過程：

```python
for idx, module_name in enumerate(modules, 1):
    # 1. 顯示進度
    logger.info(f"[{idx}/{len(modules)}] ───────")
    
    # 2. 執行模組
    result, status = execute_module(module_name, query_date, logger)
    
    # 3. 更新統計
    stats[status] += 1
    
    # 4. 儲存結果
    data_file = save_result(result, module_name, exec_day, dev_mode)
    logger.info(f"💾 檔案: {data_file.name}")
    
    # 5. 顯示摘要
    print_summary(result, status, logger)
```

---

## 輸出規格

### JSON 檔案

**檔名格式**:
- 正式模式: `YYYY-MM-DD_模組名稱.json`
- 驗收模式: `YYYY-MM-DD_模組名稱_dev.json`

**內容範例**:
```json
{
  "module": "f01",
  "date": "2025-12-01",
  "status": "success",
  "summary": "台指期外資淨額 -29,032 口（多方 18,268，空方 47,300）",
  "data": {
    "long_position": 18268,
    "short_position": 47300,
    "net_position": -29032
  },
  "source": "TAIFEX"
}
```

### 日誌檔案

**檔名格式**:
- 正式模式: `YYYY-MM-DD_run.log`
- 驗收模式: `YYYY-MM-DD_run_dev.log`

**內容範例**:
```
2025-12-04 10:30:00 [INFO] ======================================
2025-12-04 10:30:00 [INFO]   查詢日期: 2025-12-01
2025-12-04 10:30:00 [INFO]   執行時間: 2025-12-04 10:30:00
2025-12-04 10:30:00 [INFO]   執行模式: 驗收模式
2025-12-04 10:30:00 [INFO] ======================================
2025-12-04 10:30:01 [INFO] 執行模組: dev.f01_fetcher_dev
2025-12-04 10:30:02 [INFO] 💾 檔案: 2025-12-04_f01_fetcher_dev_dev.json
2025-12-04 10:30:02 [INFO]   ✅ 狀態: 成功
```

### 終端機輸出

```
======================================================================
  📅 查詢日期: 2025-12-01
  ⏰ 執行時間: 2025-12-04 10:30:00
  🔧 執行模式: 驗收模式
======================================================================

📦 找到 3 個模組

[1/3] ──────────────────────────────────────────────────
執行模組: dev.f01_fetcher_dev
💾 檔案: 2025-12-04_f01_fetcher_dev_dev.json
  ✅ 狀態: 成功
  📊 台指期外資淨額 -29,032 口（多方 18,268，空方 47,300）
     • 多方口數: 18,268
     • 空方口數: 47,300
     • 淨額: -29,032

======================================================================
  📊 執行統計
======================================================================
  總數: 3
  ✅ 成功: 2 (66.7%)
  ⚠️  失敗: 1 (33.3%)
  ❌ 錯誤: 0 (0.0%)
  ⛔ 無效: 0 (0.0%)
======================================================================
📝 詳細日誌: C:\Taifex\data\2025-12-04_run_dev.log
======================================================================
```

---

## 錯誤處理

### ⚠️ UTF-8 包裝重複問題（2025-12-15 修復）

**問題描述：**
在 Windows 環境下，當 `sys.stdout` 被**重複包裝**時會導致 `ValueError: I/O operation on closed file` 錯誤。

**發生原因：**
```
python run.py 2025-12-15
    ↓
run.py main() 第一次包裝 sys.stdout
    ↓
載入 modules.f01_fetcher
    ↓
f01_fetcher.py 第二次包裝 sys.stdout  ← 💥 問題！
    ↓
第一次的 stdout 文件流被關閉
    ↓
logger 無法寫入 → ValueError
```

**技術細節：**
```python
# 第一次包裝（run.py）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')  # 創建對象 A

# 第二次包裝（模組載入時）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')  # 創建對象 B
# 問題：對象 B 使用對象 A 的 .buffer，導致對象 A 被關閉
# 結果：logger 還在使用對象 A，但對象 A 已關閉 → I/O 錯誤
```

**解決方案：**

在所有包裝 `sys.stdout` 的地方加入檢查機制：

```python
# ❌ 錯誤寫法（會重複包裝）
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ✅ 正確寫法（避免重複包裝）
if sys.stdout.encoding != 'utf-8' and not hasattr(sys.stdout, '_wrapped_for_utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stdout._wrapped_for_utf8 = True  # 標記已包裝
```

**修復位置：**
- ✅ [run.py:497-500](run.py#L497-L500) - main() 函式
- ✅ [modules/f01_fetcher.py:32-37](modules/f01_fetcher.py#L32-L37) - 模組初始化
- ✅ [modules/f02_fetcher.py:29-34](modules/f02_fetcher.py#L29-L34) - 模組初始化
- ✅ 所有 dev/ 目錄下的模組（38 個檔案已驗證）

**症狀表現：**
```bash
# 執行時會出現大量這樣的錯誤
--- Logging error ---
Traceback (most recent call last):
  File "C:\Python39-32bit\lib\logging\__init__.py", line 1082, in emit
    stream.write(msg + self.terminator)
ValueError: I/O operation on closed file.
```

**影響範圍：**
| 功能 | 狀態 | 說明 |
|------|------|------|
| 模組執行 | ✅ 正常 | fetch() 函式本身沒問題 |
| 資料寫入 | ✅ 正常 | 直接寫檔案，不受影響 |
| 日誌輸出 | ❌ 失敗 | logger 使用被關閉的 stdout |
| 統計報告 | ❌ 失敗 | logger.info() 全部失敗 |

**預防措施：**
1. 所有新模組都應使用標記檢查機制
2. 不要直接包裝 `sys.stdout`，先檢查是否已包裝
3. 使用 `_wrapped_for_utf8` 標記追蹤包裝狀態

**相關工具：**
- [fix_utf8_wrapper.py](fix_utf8_wrapper.py) - 批次檢查和修復工具

---

### 模組載入錯誤

```python
except ImportError as e:
    logger.error(f"模組載入失敗: {e}")
    error_result = {
        "module": module_short,
        "date": query_date,
        "status": "error",
        "error": f"無法載入模組: {str(e)}"
    }
```

### 模組執行錯誤

```python
except Exception as e:
    logger.error(f"執行異常: {str(e)}")
    logger.debug(traceback.format_exc())  # 記錄完整 traceback
    error_result = {
        "module": module_short,
        "date": query_date,
        "status": "error",
        "error": f"執行失敗: {str(e)}"
    }
```

### 儲存結果錯誤

```python
try:
    data_file = save_result(result, module_name, exec_day, dev_mode)
except Exception as e:
    logger.error(f"❌ 儲存失敗: {e}")
    stats["error"] += 1
```

### 使用者中斷

```python
try:
    run(query_date, dev_mode, only_module)
except KeyboardInterrupt:
    print("\n\n⚠️  執行被使用者中斷 (Ctrl+C)")
    sys.exit(130)  # 標準 SIGINT 退出碼
```

---

## 使用範例

### 基本使用

```bash
# 執行今天的日期
python run.py

# 執行指定日期
python run.py 2025-12-01

# 顯示說明
python run.py --help
```

### 驗收模式

```bash
# 執行 dev/ 資料夾的所有模組
python run.py 2025-12-01 dev

# 只執行特定模組
python run.py 2025-12-01 dev --module f01_fetcher_dev
```

### 正式模式

```bash
# 執行 modules/ 資料夾的所有模組
python run.py 2025-12-01

# 只執行特定模組
python run.py 2025-12-01 --module f01_fetcher
```

### 檢查結果

```bash
# 查看 JSON 輸出
type data\2025-12-04_f01_fetcher.json

# 查看日誌
type data\2025-12-04_run.log

# 列出所有輸出
dir data\2025-12-04*
```

---

## 維護指南

### 何時需要修改 run.py

通常**不需要修改**，除非：

1. **新增功能**
   - 增加新的命令列參數
   - 增加新的輸出格式
   - 增加新的驗證規則

2. **修改規範**
   - 改變模組回傳格式
   - 改變檔案命名規則
   - 改變輸出目錄

3. **效能優化**
   - 加入平行處理
   - 優化載入速度
   - 增加快取機制

### 修改時的注意事項

⚠️ **重要**：修改前先備份！

```bash
# 備份當前版本
copy run.py run_backup_YYYYMMDD.py
```

✅ **測試流程**：
1. 在 `dev/` 模式測試
2. 確認所有模組都能正常執行
3. 檢查 JSON 和日誌輸出
4. 再切換到正式模式

### 常見維護任務

#### 1. 增加新的 key 轉換對照

如果有新的 data key 需要顯示中文：

```python
# 在 print_summary() 函式中
key_zh = {
    "long_position": "多方口數",
    "short_position": "空方口數",
    "net_position": "淨額",
    "new_field": "新欄位名稱"  # ← 增加這裡
}.get(key, key)
```

#### 2. 修改輸出目錄

```python
# 在檔案開頭
BASE_DIR = Path(r"C:\Taifex\data")  # ← 修改這裡
```

#### 3. 調整日誌格式

```python
# 在 setup_logger() 函式中
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"  # ← 修改這裡
```

---

## 技術細節

### 動態載入機制

```python
# 使用 importlib 動態載入模組
import importlib

module_name = "dev.f01_fetcher_dev"
mod = importlib.import_module(module_name)

# 檢查是否有 fetch 函式
if hasattr(mod, 'fetch'):
    result = mod.fetch(date)
```

### 路徑處理

```python
# 使用 pathlib 處理路徑（跨平台）
from pathlib import Path

BASE_DIR = Path(r"C:\Taifex\data")
log_file = BASE_DIR / f"{exec_day}_run.log"
data_file = BASE_DIR / f"{exec_day}_{module}.json"
```

### 日誌雙輸出

```python
# 同時輸出到檔案和終端機
file_handler = logging.FileHandler(log_file, encoding='utf-8')
console_handler = logging.StreamHandler(sys.stdout)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
```

---

## 版本歷史

### v2.1（UTF-8 包裝修復）- 2025-12-15
- 🐛 **重要修復**：解決 Windows 環境下 sys.stdout 重複包裝導致的 I/O 錯誤
- ✅ 加入 `_wrapped_for_utf8` 標記機制防止重複包裝
- ✅ 修復 logger 無法寫入的問題
- ✅ 修復統計報告無法顯示的問題
- 📝 更新錯誤處理文檔，記錄 UTF-8 包裝問題
- 🛠️ 建立 [fix_utf8_wrapper.py](fix_utf8_wrapper.py) 批次修復工具

### v2.0（混合模式）- 2025-12-04
- ✨ 採用混合模式設計（英文 key + 中文顯示）
- ✨ 改進終端機輸出（加入表情符號和進度）
- ✨ 增加資料欄位自動轉換（英文 → 中文顯示）
- 🐛 修正 Git 同步問題

### v1.0（初版）
- 基本的模組執行功能
- 使用中文 key

---

## 相關文件

- [共同開發規範書](共同開發規範書_V1.md) - 所有 fetcher 模組的通用規範
- [f01_fetcher 開發規範書](f01_package/f01_fetcher_開發規範書.md) - f01 模組專屬規範

---

**文件結束**