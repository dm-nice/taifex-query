# -*- coding: utf-8 -*-
import re
from pathlib import Path
import csv

# OCR 結果檔案（你可以改成其它日期）
txt_path = Path(r"C:\Yuanta\QAPI\screenshots\screenshot_2025-11-03.txt")
csv_path = txt_path.with_suffix(".csv")

def extract_foreign_line(text: str):
    lines = text.splitlines()
    candidates = []
    for line in lines:
        if "外資" in line and re.search(r"\d", line):
            candidates.append(line)
    return candidates[0] if candidates else None

def parse_numbers(line: str):
    # 抽出所有連續數字（含千分位）
    nums = re.findall(r"\d{1,3}(?:,\d{3})*", line)
    # 去掉千分位逗號並轉成 int
    return [int(n.replace(",", "")) for n in nums]

def main():
    if not txt_path.exists():
        print(f"找不到 OCR 結果檔：{txt_path}")
        return

    text = txt_path.read_text(encoding="utf-8")
    line = extract_foreign_line(text)

    if not line:
        print("❌ 找不到包含『外資』的資料列")
        return

    print(f"✅ 找到外資資料列：\n{line}")
    nums = parse_numbers(line)

    if len(nums) < 3:
        print(f"❌ 數字不足三個，實際找到：{nums}")
        return

    # 假設順序為：多單、空單、淨額
    long, short, net = nums[:3]
    date = txt_path.stem.replace("screenshot_", "").replace("-", "/")

    print(f"\n✅ 外資未平倉口數解析成功：")
    print(f"日期：{date}")
    print(f"多單：{long}")
    print(f"空單：{short}")
    print(f"淨額：{net}")

    # 儲存成 CSV
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["日期", "多單", "空單", "外資未平倉淨額"])
        writer.writerow([date, long, short, net])

    print(f"\n📄 已儲存 CSV：{csv_path}")

if __name__ == "__main__":
    main()