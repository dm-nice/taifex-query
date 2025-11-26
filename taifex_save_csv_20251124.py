# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import csv
import time

TARGET_DATE = "2025/11/24"

def extract_table_array(page, table_index=0):
    # 回傳二維陣列：每列是 list，每格是純文字
    rows = page.locator("table").nth(table_index).locator("tr")
    row_count = rows.count()
    table = []
    for i in range(row_count):
        cells = rows.nth(i).locator("th, td")
        cell_count = cells.count()
        row = []
        for j in range(cell_count):
            txt = cells.nth(j).inner_text().strip().replace("\u00a0"," ")
            row.append(txt)
        table.append(row)
    return table

def save_csv(filename, table):
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        for row in table:
            writer.writerow(row)

def main():
    print(f"📅 目標日期：{TARGET_DATE}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()

        # 開啟查詢頁
        page.goto("https://www.taifex.com.tw/cht/3/totalTableDate", wait_until="domcontentloaded")
        page.wait_for_selector("input[name='queryDate']", timeout=15000)

        # 填入日期並按 Enter
        page.evaluate("""
            (value) => {
                const el = document.querySelector("input[name='queryDate']");
                if (el) {
                    el.value = value;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        """, TARGET_DATE)
        page.locator("input[name='queryDate']").press("Enter")

        # 等待「日期XXXX/XX/XX」文字出現，確認載入完成
        page.wait_for_function(f"""
            () => {{
                const t = (document.body.innerText || '').replace(/\\s+/g,' ');
                return t.includes('日期{TARGET_DATE}');
            }}
        """, timeout=15000)

        # 小等待，確保表格穩定
        time.sleep(1.2)

        # 解析兩張表格
        # 表1：交易口數與契約金額
        table1 = extract_table_array(page, table_index=0)
        # 表2：未平倉口數與契約金額
        table2 = extract_table_array(page, table_index=1)

        # 輸出 CSV（加 BOM，Excel 開檔不亂碼）
        file1 = "taifex_20251124_trading.csv"
        file2 = "taifex_20251124_openinterest.csv"
        save_csv(file1, table1)
        save_csv(file2, table2)

        # 擷取畫面方便你核對
        page.screenshot(path="taifex_20251124_screen.png", full_page=True)

        print(f"✅ 已輸出：{file1}")
        print(f"✅ 已輸出：{file2}")
        print("🖼 已擷取畫面：taifex_20251124_screen.png")

        browser.close()

if __name__ == "__main__":
    main()