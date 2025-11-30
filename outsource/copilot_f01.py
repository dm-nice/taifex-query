def fetch_data(date="2025/11/28", product_id="TX"):
    url = "https://www.taifex.com.tw/cht/3/futContractsDate"
    params = {"queryDate": date, "down_type": "1", "commodity_id": product_id}
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, params=params, headers=headers)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find("table", class_="table_f")
    if not table:
        print(f"[警告] 商品 {product_id} 查無表格")
        return None

    rows = table.find_all("tr")
    for row in rows:
        cols = [c.get_text(strip=True).replace(",", "") for c in row.find_all("td")]
        if cols and "外資" in cols[0]:
            print(f"[成功] 商品 {product_id} 抓到外資資料：{cols}")
            return {
                "date": date,
                "product_id": product_id,
                "trade_net": int(cols[2]),
                "open_interest_net": int(cols[4]),
            }

    print(f"[警告] 商品 {product_id} 無外資資料")
    return None
