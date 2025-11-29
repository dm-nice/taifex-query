import requests
from bs4 import BeautifulSoup

def _to_query_date(date_str: str) -> str:
    return f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:8]}"

def debug_f1_foreign_oi(date_str: str):
    """
    Debug 版：列印期交所 futContractsDate 全部表格列
    """
    url = "https://www.taifex.com.tw/cht/3/futContractsDate"
    params = {"queryDate": _to_query_date(date_str)}

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        html = resp.text
        print("HTML 前300字：", html[:300], "...")

        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", class_="table_f")
        if not table:
            print("解析失敗：找不到 table_f")
            return

        rows = table.find_all("tr")
        for idx, tr in enumerate(rows):
            tds = [td.get_text(strip=True) for td in tr.find_all("td")]
            if tds:
                print(f"Row {idx}: {tds}")

    except Exception as e:
        print("抓取失敗：", e)

# 測試入口
if __name__ == "__main__":
    test_date = "20251126"  # 改成最近交易日
    debug_f1_foreign_oi(test_date)