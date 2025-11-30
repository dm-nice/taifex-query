# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv

# ------------------------------------------------------------
# 設定：日期範圍（可依需求修改）
# ------------------------------------------------------------
START_DATE = datetime(2025, 11, 3)
END_DATE = datetime(2025, 11, 10)

OUTPUT_CSV = "foreign_summary.csv"

# ------------------------------------------------------------
# HTTP 取頁：帶基本 headers，避免被擋
# ------------------------------------------------------------
def fetch_total_table(date_str: str) -> str:
    url = "https://www.taifex.com.tw/cht/3/totalTableDate"
    params = {"queryDate": date_str}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.taifex.com.tw/cht/3/totalTableDate",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    }
    r = requests.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()
    return r.text

# ------------------------------------------------------------
# 工具：將 <tr> 解析為欄位文字陣列（去逗號、去空白）
# ------------------------------------------------------------
def row_to_cols(tr):
    tds = tr.find_all("td")
    cols = []
    for td in tds:
        # 取純文字、去頭尾空白、去數字千分位逗號
        txt = td.get_text(strip=True).replace(",", "")
        cols.append(txt)
    return cols

# ------------------------------------------------------------
# 核心解析：抓外資的「多空淨額口數」
# 這頁面通常有兩張表（class="table_f"）：
#   tables[0] -> 交易口數與契約金額
#   tables[1] -> 未平倉口數與契約金額
# 我們要各自找出外資列的「多空淨額（口數）」。
# ------------------------------------------------------------
def parse_foreign_data(html: str):
    soup = BeautifulSoup(html, "lxml")  # 若無 lxml 也可自動回退為 html.parser
    tables = soup.find_all("table", class_="table_f")

    # 有時候 class 名稱可能不同，備援找所有 table
    if len(tables) < 2:
        tables = soup.find_all("table")
        # 保險：若仍少於兩張表，回傳 None
        if len(tables) < 2:
            return None, None

    # 交易表、未平倉表
    trade_table = tables[0]
    oi_table = tables[1]

    # 取得外資的淨額（口數），並印出每列，方便除錯
    def extract_net(table, label):
        # 嘗試從表頭估算「多空淨額（口數）」所在欄位索引
        # 一般欄序：身份別 | 多方口數 | 契約金額 | 空方口數 | 契約金額 | 多空淨額口數 | 契約金額
        # 理想索引：5（第六欄）
        net_index_guess = 5

        # 嘗試找 header 列（th 或第一個 tr）
        header_found = False
        thead = table.find("thead")
        if thead:
            header_rows = thead.find_all("tr")
        else:
            header_rows = table.find_all("tr")[:1]  # 取第一列當 header 估測

        for hr in header_rows:
            ths = hr.find_all(["th", "td"])
            header_texts = [h.get_text(strip=True) for h in ths]
            if header_texts:
                header_found = True
                # 嘗試找到含「多空淨額」且含「口數」的欄位位置
                for i, htxt in enumerate(header_texts):
                    if ("多空" in htxt) and ("淨" in htxt) and ("口數" in htxt):
                        net_index_guess = i
                        break

        # 逐列掃描，印出並模糊比對「外資」
        rows = table.find_all("tr")
        for tr in rows:
            cols = row_to_cols(tr)
            if not cols:
                continue

            # 印出每列供你目視確認
            print(f"[{label}] 欄位：", cols)

            # 找到外資列（模糊比對，避免全形、空白等干擾）
            if any("外資" in c for c in cols):
                # 先用推測索引取值，不行再回退到 5
                candidates = []
                # 推測的索引
                if len(cols) > net_index_guess:
                    candidates.append(cols[net_index_guess])
                # 備援索引 5（第六欄）
                if len(cols) > 5:
                    candidates.append(cols[5])

                # 從候選取第一個可轉 int 的值
                for cand in candidates:
                    try:
                        return int(cand)
                    except:
                        continue

                # 若都失敗，嘗試從右往左找第一個可轉 int 的負數（常為淨額）
                for cand in reversed(cols):
                    try:
                        val = int(cand)
                        # 淨額常見為負數；如果找到負數就用它
                        if val < 0:
                            return val
                    except:
                        pass

                # 最後仍找不到就回 None
                return None

        return None

    trade_net = extract_net(trade_table, "交易")
    oi_net = extract_net(oi_table, "未平倉")
    return trade_net, oi_net

# ------------------------------------------------------------
# 主流程：多日抓取 + 列印 + CSV 儲存
# ------------------------------------------------------------
def main():
    results = []
    current = START_DATE

    while current <= END_DATE:
        # 跳過週末
        if current.weekday() >= 5:
            current += timedelta(days=1)
            continue

        date_str = current.strftime("%Y/%m/%d")
        try:
            html = fetch_total_table(date_str)
            trade_net, oi_net = parse_foreign_data(html)

            print(f"{date_str} → 交易淨額:{trade_net}, 未平倉淨額:{oi_net}")

            results.append({
                "日期": date_str,
                "外資交易淨額": trade_net,
                "外資未平倉淨額": oi_net,
                "錯誤": "" if (trade_net is not None or oi_net is not None) else "解析失敗或結構改變"
            })
        except Exception as e:
            print(f"{date_str} → 抓取失敗: {e}")
            results.append({
                "日期": date_str,
                "外資交易淨額": None,
                "外資未平倉淨額": None,
                "錯誤": str(e)
            })

        current += timedelta(days=1)

    # 儲存 CSV（UTF-8-SIG，Excel 友善）
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["日期", "外資交易淨額", "外資未平倉淨額", "錯誤"])
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print(f"✅ 已儲存 {OUTPUT_CSV}")

# ------------------------------------------------------------
# 入口
# ------------------------------------------------------------
if __name__ == "__main__":
    main()