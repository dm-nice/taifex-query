# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import time

TARGET_DATE = "2025/11/24"  # 你要測試的日期

def main():
    print(f"📅 查詢頁面自動化測試：{TARGET_DATE}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1600, "height": 900},
            device_scale_factor=1.25,
        )
        page = context.new_page()

        # ✅ 開啟「查詢頁」而非 Excel 頁
        page.goto("https://www.taifex.com.tw/cht/3/totalTableDate", wait_until="domcontentloaded")

        # ✅ 等待日期欄位出現
        page.wait_for_selector("input[name='queryDate']", timeout=15000)

        # ✅ 強制填入日期並觸發 input/change
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

        # ✅ 按 Enter 觸發查詢（這是你人工確認有效的方式）
        page.locator("input[name='queryDate']").press("Enter")

        # ✅ 等待內容變更：以頁面上「日期XXXX/XX/XX」文字為依據
        try:
            page.wait_for_function(f"""
                () => {{
                    const bodyText = (document.body.innerText || '').replace(/\\s+/g, ' ');
                    return bodyText.includes('日期{TARGET_DATE}');
                }}
            """, timeout=15000)
            print("✅ 日期文字已更新，查詢應已成功")
        except:
            print("⚠️ 未在期限內看到日期文字更新，可能仍是最新資料或載入較慢")

        # 也等待表格載入（雙保險）
        try:
            page.wait_for_selector("table", timeout=10000)
        except:
            pass

        # ✅ 擷取畫面
        page.screenshot(path="taifex_totalTable_20251124.png", full_page=True)
        print("🖼 已擷取畫面 taifex_totalTable_20251124.png")

        browser.close()

if __name__ == "__main__":
    main()