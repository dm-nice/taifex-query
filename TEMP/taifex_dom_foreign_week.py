# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
from pathlib import Path
import csv
import re
import time
from datetime import datetime, timedelta

OUT_DIR = Path(r"C:\Yuanta\QAPI\outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def get_recent_weekdays(n=5):
    today = datetime.today()
    dates = []
    delta = 0
    while len(dates) < n:
        d = today - timedelta(days=delta)
        if d.weekday() < 5:  # 0=Mon, 4=Fri
            dates.append(d.strftime("%Y/%m/%d"))
        delta += 1
    return sorted(dates)

def extract_foreign_row(rows):
    for r in rows:
        if any("外資" in (cell or "") for cell in r):
            return r
    return None

def extract_numbers(row):
    nums = []
    for cell in row:
        for m in re.findall(r"\d{1,3}(?:,\d{3})*", cell or ""):
            try:
                nums.append(int(m.replace(",", "")))
            except:
                pass
    return nums[:3] if len(nums) >= 3 else [None, None, None]

def main():
    dates = get_recent_weekdays()
    out_csv = OUT_DIR / "foreign_week.csv"
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["日期", "多單口數", "空單口數", "外資未平倉口數", "外資淨額口數"])

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(viewport={"width": 1600, "height": 900}, device_scale_factor=1.5)
            page = context.new_page()

            for d in dates:
                # ✅ 直接用帶 queryDate 的網址
                url = f"https://www.taifex.com.tw/cht/3/totalTableDateExcel?queryDate={d}"
                print(f"\n📅 查詢日期：{d}")
                page.goto(url, wait_until="domcontentloaded")

                page.wait_for_selector("table", timeout=15000)
                time.sleep(1.5)

                rows = page.evaluate("""
                    () => {
                      const tbls = Array.from(document.querySelectorAll("table"));
                      // 找到包含「外資」的表格
                      for (const tbl of tbls) {
                        if ((tbl.innerText || "").includes("外資")) {
                          const rows = [];
                          for (const tr of tbl.querySelectorAll("tr")) {
                            const cells = [];
                            for (const td of tr.querySelectorAll("th, td")) {
                              cells.push((td.innerText || "").trim());
                            }
                            rows.push(cells);
                          }
                          return rows;
                        }
                      }
                      return [];
                    }
                """)

                target = extract_foreign_row(rows)
                if not target:
                    print("❌ 找不到外資列")
                    continue

                long_qty, short_qty, net_qty = extract_numbers(target)
                if None in (long_qty, short_qty, net_qty):
                    print(f"⚠️ 數字解析失敗，外資列內容：{target}")
                    continue

                foreign_oi_qty = long_qty
                print(f"✅ {d} 外資 多:{long_qty} 空:{short_qty} 淨:{net_qty}")
                writer.writerow([d, long_qty, short_qty, foreign_oi_qty, net_qty])

            browser.close()

    print(f"\n📄 已輸出整週 CSV：{out_csv}")

if __name__ == "__main__":
    main()