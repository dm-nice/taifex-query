# Taifex 工具模組

這個資料夾包含各種實用的工具腳本。

## 📁 目錄結構

```
tools/
├── __init__.py          # 模組初始化檔案
├── sys_info.py          # 系統資訊檢查工具
└── README.md            # 說明文件
```

## 🛠️ 可用工具

### 1. sys_info.py - 系統資訊檢查
檢查作業系統版本、CPU 使用率、記憶體資訊，並輸出 JSON 報告。

**使用方式：**
```bash
python tools/sys_info.py
```

**輸出檔案：** `report.json`

---

## 📦 如何使用這些工具

### 方法 1: 直接執行
```bash
python tools/sys_info.py
```

### 方法 2: 作為模組匯入
```python
from tools import sys_info

# 取得系統資訊
info = sys_info.get_system_info()
print(info)
```

### 方法 3: 使用統一入口 (建議)
```bash
python main_tools.py
```

---

## 📝 新增工具指南

1. 在 `tools/` 資料夾建立新的 `.py` 檔案
2. 在 `__init__.py` 中加入匯入語句
3. 更新此 README 文件

---

**版本：** 1.0.0
**最後更新：** 2025-12-28
