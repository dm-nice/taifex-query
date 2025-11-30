"""
debug_pipeline.py
錯誤回報工具
當模組失敗或例外時，自動產生 Markdown 錯誤紀錄到 issues/
"""

import os
from datetime import datetime

def report_error(module: str, date: str, error: str) -> str:
    """
    建立錯誤紀錄檔案 issues/YYYY-MM-DD_module_error.md

    Args:
        module (str): 模組名稱 (例如 f01, f10)
        date (str): 日期字串 YYYY-MM-DD
        error (str): 錯誤訊息

    Returns:
        str: 錯誤紀錄檔案路徑
    """

    os.makedirs("issues", exist_ok=True)

    filename = f"issues/{date}_{module}_error.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content = f"""# 錯誤紀錄
- 模組: {module}
- 日期: {date}
- 時間: {timestamp}

## 錯誤訊息
錯誤訊息 (Traceback)

{error}

程式碼
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    return filename


# 測試用：模組可獨立執行
if __name__ == "__main__":
    path = report_error("f01", "2025-11-28", "測試錯誤：連線失敗")
    print(f"錯誤紀錄已建立: {path}")


===============================

效果
自動產生 Markdown：失敗時會在 issues/ 下建立 YYYY-MM-DD_module_error.md

內容清楚：包含模組名稱、日期、時間、錯誤訊息

可獨立測試：直接執行 python utils/debug_pipeline.py 就能測試錯誤紀錄功能

run.py 呼叫 report_error(...) 時，就能自動把錯誤紀錄存到 issues/。







