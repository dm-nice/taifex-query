# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
from pathlib import Path
from PIL import Image
import pytesseract

# 要查詢的日期
dates = ["2025/11/03", "2025/11/04"]

# 螢幕截圖輸出資料夾
out_dir = Path(r"C:\Yuanta\QAPI\screenshots")
out_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 先用非 headless 方便目視
    context = browser.new_context(
        viewport={"width": 1600, "height": 900},
        device_scale_factor=1.5
    )
    page = context.new_page()

    for d in dates:
        url = "https://www.taifex.com.tw/cht/3/totalTableDate"
        print(f"\n開啟：{url}，設定日期：{d}")
        page.goto(url, wait_until="domcontentloaded")

        # 填入日期
        try:
            page.wait_for_selector("input[name='queryDate']", timeout=5000)
            page.fill("input[name='queryDate']", d)
            print("日期填入成功")
        except:
            print("日期輸入框未找到")

        # 點擊查詢按鈕
        try:
            page.wait_for_selector("input[type=button][value='查詢']", timeout=5000)
            page.click("input[type=button][value='查詢']")
            print("查詢按鈕已點擊")
        except:
            print("查詢按鈕未找到，改用 Enter")
            page.keyboard.press("Enter")

        # 等待表格渲染
        try:
            page.wait_for_selector(".table_f", timeout=10000)
            print("表格已出現")
        except:
            print("未等到表格，改等 networkidle")
            page.wait_for_load_state("networkidle")

        # 截整頁
        fname = out_dir / f"screenshot_{d.replace('/', '-')}.png"
        page.screenshot(path=str(fname), full_page=True)
        print(f"已儲存截圖：{fname}")

        # OCR 辨識
        img = Image.open(fname)
        text = pytesseract.image_to_string(img, lang="chi_tra")
        print(f"=== {d} OCR 結果 ===")
        print(text)

    browser.close()