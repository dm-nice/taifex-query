from typing import Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def _to_query_date(date_str: str) -> str:
    return f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:8]}"

def get_f1_foreign_oi(date_str: str, debug_mode: bool = False) -> Optional[int]:
    url = "https://www.taifex.com.tw/cht/3/totalTableDate"
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
            if len(tds) >= 6 and "外資" in tds[0].get_text(strip=True):
                text = tds[5].get_text(strip=True).replace(",", "")
                try:
                    return int(text)
                except ValueError:
                    return None

        return None
    except Exception as e:
        if debug_mode:
            print("F1 抓取失敗：", e)
        return None

def get_f2_foreign_oi_delta(date_str: str, debug_mode: bool = False) -> Optional[int]:
    today_oi = get_f1_foreign_oi(date_str, debug_mode)
    if today_oi is None:
        if debug_mode:
            print("F2 中斷：今日 OI 為 None，跳過計算")
        return None

    try:
        prev_date = (datetime.strptime(date_str, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
        prev_oi = get_f1_foreign_oi(prev_date, debug_mode)
    except:
        prev_oi = None

    if prev_oi is None:
        if debug_mode:
            print("F2 中斷：昨日 OI 為 None，跳過計算")
        return None

    return today_oi - prev_oi

# ✅ 主程式區塊：先跑 F1 成功後再跑 F2
if __name__ == "__main__":
    test_date = "20251125"
    f1_value = get_f1_foreign_oi(test_date, debug_mode=True)
    print("F1 外資期貨 OI：", f1_value)

    if f1_value is not None:
        f2_value = get_f2_foreign_oi_delta(test_date, debug_mode=True)
        print("F2 外資 OI 增減量：", f2_value)
    else:
        print("F1 無資料，跳過 F2 計算")