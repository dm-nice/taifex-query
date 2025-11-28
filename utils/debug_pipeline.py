import datetime
import os
import traceback
from bs4 import BeautifulSoup

def debug_pipeline(module_name: str, error: Exception, snapshot_files: list, log_file: str):
    """
    整合版 Debug Pipeline：
    1. 自動產生錯誤紀錄 Markdown
    2. 附加 DOM <select> / <table> 區塊
    3. 附加 log 錯誤訊息
    """

    # 建立 issues 目錄
    os.makedirs("issues", exist_ok=True)

    # 日期
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    # Issue 檔案名稱
    issue_file = f"issues/{date_str}_{module_name}_error.md"

    # 錯誤訊息
    error_msg = "".join(traceback.format_exception(type(error), error, error.__traceback__))

    # 初始 Markdown 內容
    content = f"""# 錯誤紀錄：{module_name} 模組

## 日期
{date_str}

## 模組
{module_name}

## 錯誤摘要
{str(error)}

## 錯誤訊息 (Traceback)