import os

def append_log_to_issue(log_file: str, issue_file: str):
    """
    從 log 檔案中抽取錯誤訊息，附加到指定的 issue Markdown 檔案
    """
    if not os.path.exists(log_file):
        return f"[log_parser] 找不到 log 檔案：{log_file}"

    # 讀取 log 檔案
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 抽取錯誤相關行 (簡單篩選含 ERROR 或 Traceback 的行)
    error_lines = [line for line in lines if "ERROR" in line or "Traceback" in line]

    if not error_lines:
        return "[log_parser] 未找到錯誤訊息"

    # 組合 Markdown 內容
    content = f"""## 錯誤 Log 片段 ({log_file})