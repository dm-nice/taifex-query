import traceback

def format_traceback(e: Exception) -> str:
    """
    將例外物件轉換為完整文字錯誤訊息（含 Traceback）
    用於 run.py 將錯誤直接寫入 log 檔案
    """
    return "".join(traceback.format_exception(type(e), e, e.__traceback__))
