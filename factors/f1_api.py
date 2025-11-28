import os
import requests
from typing import Optional

API_URL = "https://openapi.taifex.com.tw/v1/MarketDataOfMajorInstitutionalTradersGeneralBytheDate"
OUTPUT_DIR = r"C:\Taifex\data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "F1_foreign_oi.txt")

def get_f1_foreign_oi_by_date(date_str: str, debug_mode: bool = False) -> Optional[int]:
    url = f"{API_URL}?date={date_str}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if debug_mode:
            print(f"📅 查詢日期：{date_str}")
            print(f"🔁 回傳筆數：{len(data)}")
            if data:
                print("📦 前1筆：", data[0])

        for row in data:
            name = row.get("InstitutionalInvestor") or row.get("Item")
            if name in ["外資", "外資及陸資"]:
                val = row.get("FuturesNet") or row.get("OpenInterest(Net)")
                if val:
                    val_str = str(val).replace(",", "").strip()
                    try:
                        return int(float(val_str))
                    except:
                        return None
        return None
    except Exception as e:
        if debug_mode:
            print("❌ API 抓取失敗：", e)
        return None

def save_f1_line(date_str: str, f1_oi: int):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    line = f"{date_str}     F1: 台指期貨外資及陸資淨口數 (OI):  {f1_oi}"
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print("✅ 已寫入：", line)