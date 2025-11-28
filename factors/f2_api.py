import os
import requests
from datetime import datetime, timedelta
from typing import Optional

API_URL = "https://openapi.taifex.com.tw/v1/MarketDataOfMajorInstitutionalTradersGeneralBytheDate"
OUTPUT_DIR = r"C:\Taifex\data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "F2_foreign_oi_delta.txt")

def get_f1_value(date_str: str, debug_mode: bool = False) -> Optional[int]:
    """抓指定日期的外資期貨 OI（淨口數）"""
    url = f"{API_URL}?date={date_str}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if debug_mode:
            print(f"📅 查詢日期：{date_str}")
            print(f"📦 回傳筆數：{len(data)}")
            if data:
                print("🔍 前1筆資料：", data[0])

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
            print(f"❌ API 抓取失敗：{e}")
        return None

def get_previous_trading_date(date_str: str, debug_mode: bool = False) -> Optional[str]:
    """往前找最近有資料的交易日"""
    dt = datetime.strptime(date_str, "%Y%m%d")
    for i in range(1, 10):  # 最多往前找 10 天
        prev_dt = dt - timedelta(days=i)
        prev_str = prev_dt.strftime("%Y%m%d")
        val = get_f1_value(prev_str)
        if val is not None:
            if debug_mode:
                print(f"📅 找到前一交易日：{prev_str} → OI={val}")
            return prev_str
    return None

def get_f2_delta(today: str, debug_mode: bool = False) -> Optional[tuple[str, int]]:
    """計算 F2 增減量"""
    today_val = get_f1_value(today, debug_mode=debug_mode)
    if today_val is None:
        print(f"⚠️ 今日 {today} 沒有 OI 資料")
        return None

    prev_date = get_previous_trading_date(today, debug_mode=debug_mode)
    if not prev_date:
        print("⚠️ 找不到前一交易日")
        return None

    prev_val = get_f1_value(prev_date, debug_mode=debug_mode)
    if prev_val is None:
        print(f"⚠️ 前一交易日 {prev_date} 沒有 OI 資料")
        return None

    delta = today_val - prev_val

    if debug_mode:
        print(f"📅 今日 {today} → OI = {today_val}")
        print(f"📅 前一交易日 {prev_date} → OI = {prev_val}")
        print(f"➡️ 增減量 = {today_val} - {prev_val} = {delta}")

    return prev_date, delta

def save_f2_line(today: str, prev: str, delta: int):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    line = f"{today}     F2: 外資及陸資 OI 增減量 (相較 {prev}):  {delta}"
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print("✅ 已寫入：", line)

if __name__ == "__main__":
    target_date = "20251126"  # 你只要改這一行
    debug_mode = True         # ✅ 開啟 debug 模式
    result = get_f2_delta(target_date, debug_mode=debug_mode)
    if result:
        prev_date, delta = result
        save_f2_line(target_date, prev_date, delta)
    else:
        print("⚠️ F2 計算失敗")