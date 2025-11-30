import requests
from bs4 import BeautifulSoup

def fetch_total_table(date_str):
    url = "https://www.taifex.com.tw/cht/3/totalTableDate"
    params = {"queryDate": date_str}
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()
    return r.text

def parse_foreign_data(html):
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table", class_="table_f")
    if len(tables) < 2:
        return None, None

    def extract_net(table):
        for row in table.find_all("tr"):
            cols = [c.get_text(strip=True).replace(",", "") for c in row.find_all("td")]
            if cols and "外資" in cols[0]:
                try:
                    return int(cols[5])  # 第6欄是「多空淨額口數」
                except:
                    return None
        return None

    trade_net = extract_net(tables[0])  # 交易口數表
    oi_net = extract_net(tables[1])     # 未平倉口數表
    return trade_net, oi_net

# 測試抓取 2025/11/03
html = fetch_total_table("2025/11/03")
trade_net, oi_net = parse_foreign_data(html)
print("日期: 2025/11/03")
print("外資交易淨額:", trade_net)
print("外資未平倉淨額:", oi_net)