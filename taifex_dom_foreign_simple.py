# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
from pathlib import Path
import csv
import re
import time

OUT_DIR = Path(r"C:\Yuanta\QAPI\outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 你可自行調整或改為動態輸入
DATES = ["2025/11/03", "2025/11/04", "2025/11/25"]

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
    # 期望順序：多方口數、空方口數、淨額口數
    return nums[:3] if len(nums) >= 3 else [None, None, None]

def main():
    out_csv = OUT_DIR / "foreign_simple.csv"
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["日期", "多單口數", "空單口數", "外資未平倉口數", "外資淨額口數"])

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={"width": 1600, "height": 900},
                device_scale_factor=1.5
            )
            page = context.new_page()

            for d in DATES:
                url = "https://www.taifex.com.tw/cht/3/totalTableDateExcel"
                print(f"\n📅 查詢日期：{d}")
                page.goto(url, wait_until="domcontentloaded")

                # 有些情況 input 不可見或受前端事件管制，提供兩種方式設定日期
                try:
                    page.wait_for_selector("input[name='queryDate']", timeout=15000)
                    page.fill("input[name='queryDate']", d)
                except Exception:
                    # 備援：用 JS 直接設值
                    page.evaluate("""
                        (value) => {
                            const el = document.querySelector("input[name='queryDate']");
                            if (el) { el.value = value; el.dispatchEvent(new Event('input', { bubbles: true })); }
                        }
                    """, d)

                # 點查詢按鈕（有時可能有多個 input[type=button]）
                try:
                    page.click("input[type=button][value='查詢']", timeout=10000)
                except Exception:
                    # 備援：嘗試文案或鍵盤 Enter
                    btn = page.locator("input[type=button]")
                    if btn.count() > 0:
                        btn.first.click()
                    else:
                        page.keyboard.press("Enter")

                # 等待資料載入
                page.wait_for_load_state("networkidle")
                time.sleep(0.8)  # 短暫延遲，讓表格渲染完成

                # 精準定位「未平倉口數與契約金額」標題的下一個 table
                table_handle = page.evaluate_handle("""
                    (headerText) => {
                      const matchText = headerText;
                      const el = Array.from(document.querySelectorAll("*"))
                        .find(e => (e.textContent || "").trim().includes(matchText));
                      if (!el) return null;
                      // 往後找第一個 table
                      let node = el;
                      for (let i=0; i<12; i++) {
                        node = node.nextElementSibling;
                        if (!node) break;
                        if (node.tagName === "TABLE") return node;
                        const t = node.querySelector && node.querySelector("table");
                        if (t) return t;
                      }
                      // 備援：頁面全部 table 中，找內文包含「外資」的候選
                      const all = Array.from(document.querySelectorAll("table"));
                      for (const t of all) {
                        const txt = t.innerText || "";
                        if (txt.includes("外資") && txt.includes("未平倉")) return t;
                      }
                      return null;
                    }
                """, "未平倉口數與契約金額")

                if not table_handle:
                    print("❌ 找不到未平倉表格（版面可能變動）")
                    continue

                rows = page.evaluate("""
                    (tbl) => {
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
                """, table_handle)

                target = extract_foreign_row(rows)
                if not target:
                    print("❌ 找不到外資列")
                    continue

                long_qty, short_qty, net_qty = extract_numbers(target)
                if None in (long_qty, short_qty, net_qty):
                    print(f"⚠️ 數字解析失敗，外資列內容：{target}")
                    continue

                foreign_oi_qty = long_qty  # 目前定義為多方口數
                print(f"✅ {d} 外資 多:{long_qty} 空:{short_qty} 淨:{net_qty}")
                writer.writerow([d, long_qty, short_qty, foreign_oi_qty, net_qty])

            browser.close()

    print(f"\n📄 已輸出 CSV：{out_csv}")

if __name__ == "__main__":
    main()