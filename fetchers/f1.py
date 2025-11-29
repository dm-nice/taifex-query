import requests
from bs4 import BeautifulSoup
from typing import Optional

def _to_query_date(date_str: str) -> str:
    # "YYYYMMDD" → "YYYY/MM/DD"
    return f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:8]}"

def get_f1_foreign_oi(date_str: str, debug_mode: bool = False) -> Optional[int]:
    """
    F1: 外資期貨未平倉多空淨額口數（純期貨）
    來源：TAIFEX /cht/3/futContractsDate
    """
    url = "https://www.taifex.com.tw/cht/3/futContractsDate"
    params = {"queryDate": _to_query_date(date_str)}

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        html = resp.text
        if debug_mode:
            print("F1 HTML（前300字）：", html[:300], "...")

        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", class_="table_f")
        if not table:
            if debug_mode:
                print("F1 解析失敗：找不到 table_f")
            return None

        rows = table.find_all("tr")
        for tr in rows:
            tds = tr.find_all("td")
            if len(tds) >= 7:
                product = tds[1].get_text(strip=True)
                identity = tds[2].get_text(strip=True)
                if product == "臺股期貨" and "外資" in identity:
                    value = tds[6].get_text(strip=True).replace(",", "")
                    try:
                        return int(value)
                    except ValueError:
                        return None

        if debug_mode:
            print("F1 解析失敗：找不到外資臺股期貨資料")
        return None
    except Exception as e:
        if debug_mode:
            print("F1 抓取失敗：", e)
        return None

# 測試入口
if __name__ == "__main__":
    test_date = "20251126"  # 改成最近交易日
    print("F1 外資期貨 OI：", get_f1_foreign_oi(test_date, debug_mode=True))