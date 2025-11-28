import os
import datetime
import traceback

def write_error_report(module_name: str, error: Exception, snapshot_files: list):
    """
    自動產生錯誤紀錄 Markdown 檔案，存放在 issues/ 目錄下
    """
    # 建立 issues 目錄
    os.makedirs("issues", exist_ok=True)

    # 日期
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    # 檔案名稱
    filename = f"issues/{date_str}_{module_name}_error.md"

    # 錯誤訊息
    error_msg = "".join(traceback.format_exception(type(error), error, error.__traceback__))

    # Markdown 內容
    content = f"""# 錯誤紀錄：{module_name} 模組

## 日期
{date_str}

## 模組
{module_name}

## 錯誤摘要
{str(error)}

## 錯誤訊息 (Log)