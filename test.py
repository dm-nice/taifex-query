import re
import requests
from bs4 import BeautifulSoup

def main():
    url = "https://www.taifex.com.tw/cht/3/totalTableDate"
    print(f"測試網址：{url}")

    resp = requests.get(url, timeout=10)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    # 1) 抓實際資料日期（頁面有「日期YYYY/MM/DD」字樣）
    text = soup.get_text(" ", strip=True)
    m = re.search(r"日期\s*([0-9]{4}/[0-9]{2}/[0-9]{2})", text)
    actual_date = m.group(1) if m else "未知"
    print(f"實際資料日期 actual_date：{actual_date}")

    # 2) 範例解析：抓「未平倉口數 與 契約金額」表格中的『外資』多空淨額
    #    注意：此頁是「總表」，包含多種商品與彙總；你若要「台指期」需改用對應商品頁或再過濾
    net_value = None
    table = soup.find("table")  # 頁面第一個表格通常是「交易口數與契約金額」
    tables = soup.find_all("table")
    # 嘗試在所有表格中找包含「未平倉口數」字樣的表格
    target = None
    for t in tables:
        if "未平倉口數" in t.get_text():
            target = t
            break
    if target is None:
        target = table

    if target:
        for tr in target.find_all("tr"):
            cols = [c.get_text(strip=True) for c in tr.find_all(["th", "td"])]
            # 例：['外資', '167,075', '187,770', '472,159', '445,506', '-305,084', '-257,736']
            if cols and ("外資" in cols[0]):
                # 嘗試抓「多空淨額」欄位（通常是第 6 欄或最後一欄）
                for v in reversed(cols):
                    if re.match(r"^-?\d{1,3}(,\d{3})*$", v):
                        net_value = v
                        break
                break

    print(f"外資未平倉多空淨額（總表）net_value：{net_value if net_value else '未找到'}")

if __name__ == "__main__":
    main()
