# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image
import pytesseract

# 如果 tesseract.exe 沒在 PATH，請取消註解並改成你的實際路徑
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preview_lines(text: str, n: int = 30):
    lines = [ln for ln in text.splitlines() if ln.strip()]
    for i, ln in enumerate(lines[:n], 1):
        print(f"{i:02d}: {ln}")

def main():
    # 指向你的截圖檔案（可改成你要測試的檔名）
    img_path = Path(r"C:\Yuanta\QAPI\screenshots\screenshot_2025-11-03.png")

    if not img_path.exists():
        print(f"找不到檔案：{img_path}")
        print("請確認檔名或改成實際存在的截圖路徑。")
        return

    print(f"讀取圖片：{img_path}")
    img = Image.open(img_path)

    # OCR（繁體中文）
    print("開始 OCR（lang=chi_tra）...")
    text = pytesseract.image_to_string(img, lang="chi_tra")

    print("\n=== OCR 前 30 行預覽 ===")
    preview_lines(text, n=30)

    # 可選：將完整結果存到文字檔
    out_txt = img_path.with_suffix(".txt")
    out_txt.write_text(text, encoding="utf-8")
    print(f"\n已輸出完整 OCR 結果：{out_txt}")

if __name__ == "__main__":
    main()