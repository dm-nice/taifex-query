import os
from bs4 import BeautifulSoup

def extract_dom_snippets(html_file: str, output_file: str):
    """
    從 HTML 檔案中抽取 <select> 和 <table> 區塊，
    並寫入到指定的輸出檔案 (通常是 issues/ 的 .md)
    """
    if not os.path.exists(html_file):
        return f"[html_cleaner] 找不到檔案：{html_file}"

    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # 抽取 <select> 區塊
    selects = soup.find_all("select")
    select_snippets = "\n\n".join(str(s) for s in selects) if selects else "（未找到 <select> 區塊）"

    # 抽取 <table> 區塊
    tables = soup.find_all("table")
    table_snippets = "\n\n".join(str(t) for t in tables) if tables else "（未找到 <table> 區塊）"

    # 組合 Markdown 內容
    content = f"""## DOM 抽取結果：{html_file}

### <select> 區塊