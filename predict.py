import json
import os
from datetime import datetime

# 1. 數據目錄
DATA_DIR = r"C:\Taifex\data"

def get_latest_factors():
    factors = {}
    if not os.path.exists(DATA_DIR): return factors
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            factor_key = filename.split('.')[0]
            with open(os.path.join(DATA_DIR, filename), 'r', encoding='utf-8') as f:
                val = f.read().strip().replace(',', '')
                factors[factor_key] = val
    return factors

# 2. 自動判斷與評分邏輯
def analyze(factors):
    f01 = float(factors.get('F01', 0))
    f17 = float(factors.get('F17', 0))
    
    # 範例邏輯：若外資期貨空單 > 2.5萬口 且 現貨賣超
    if f01 < -25000 and f17 < 0:
        return "下跌", "-200 至 -350", "90", "外資期現貨同步偏空布局，空方力道強勁。"
    elif f01 > 10000:
        return "上漲", "+150 至 +250", "80", "外資多單回補，支撐轉強。"
    else:
        return "盤整", "-100 至 +100", "65", "籌碼面不明顯，預期區間震盪。"

# 3. 產出 JSON 並更新 README
factors_data = get_latest_factors()
res, rng, conf, summary = analyze(factors_data)

prediction = {
    "數據日期": datetime.now().strftime('%Y/%m/%d'),
    "隔日預測結果": res,
    "預測漲跌點數範圍": rng,
    "信心分數": conf,
    "關鍵驅動因子": {
        "強度因子一": "F01(外資淨OI): " + factors_data.get('F01', '0') + " 口",
        "強度因子二": "F17(外資現貨買賣超): " + factors_data.get('F17', '0') + " 億元"
    },
    "推理總結": summary
}

full_readme = "# 台指期預測系統 (TAIEX Prediction)\n" + \
              "![My First Action](https://github.com/dm-nice/taifex-query/actions/workflows/ci.yml/badge.svg)\n\n" + \
              "## 最後自動更新時間: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n" + \
              "```json\n" + json.dumps(prediction, indent=4, ensure_ascii=False) + "\n```\n"

with open("README.md", "w", encoding="utf-8") as f:
    f.write(full_readme)

print("README.md 更新成功！數值已自動導入。")