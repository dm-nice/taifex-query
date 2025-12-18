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
                val = f.read().strip().replace(',', '').replace('%', '')
                factors[factor_key] = val
    return factors

def multi_weight_analyze(factors):
    # 轉換數值並設定初始分數 (50為中性)
    f01 = float(factors.get('F01', 0))  # 外資期貨淨OI
    f06 = float(factors.get('F06', 20)) # 波動率 (基準值20)
    f07 = float(factors.get('F07', 100))# P/C Ratio (基準100%)
    f17 = float(factors.get('F17', 0))  # 外資現貨買賣超
    
    score = 50
    reasons = []

    # 權重 1: 外資期貨 (最重要)
    if f01 < -30000: score -= 25; reasons.append("期貨極度偏空")
    elif f01 > 10000: score += 15; reasons.append("期貨多單支撐")

    # 權重 2: 外資現貨
    if f17 < -300: score -= 15; reasons.append("外資提款現貨")
    elif f17 > 200: score += 10; reasons.append("外資回補現貨")

    # 權重 3: P/C Ratio (選擇權情緒)
    if f07 < 90: score -= 10; reasons.append("選擇權籌碼偏空")
    elif f07 > 110: score += 10; reasons.append("選擇權籌碼看多")

    # 權重 4: 波動率 (恐慌指數)
    if f06 > 22: score -= 10; reasons.append("市場恐慌情緒升溫")

    # 判定結果
    if score <= 30: res, rng, conf = "下跌", "-200 至 -400", 92
    elif score < 48: res, rng, conf = "盤整偏空", "-50 至 -150", 75
    elif score <= 55: res, rng, conf = "盤整", "-50 至 +50", 60
    elif score < 70: res, rng, conf = "盤整偏多", "+50 至 +150", 75
    else: res, rng, conf = "上漲", "+200 至 +350", 90

    return res, rng, str(conf), " | ".join(reasons) if reasons else "指標趨於中性"

# --- 執行流程 ---
factors = get_latest_factors()
res, rng, conf, summary = multi_weight_analyze(factors)

prediction = {
    "數據日期": datetime.now().strftime('%Y/%m/%d'),
    "隔日預測結果": res,
    "預測漲跌點數範圍": rng,
    "信心分數": conf,
    "關鍵驅動因子": {
        "強度因子一": "F01(外資淨OI): " + factors.get('F01', '0') + " 口",
        "強度因子二": "F07(P/C Ratio): " + factors.get('F07', '0') + "%"
    },
    "推理總結": summary
}

# 寫入 README.md
full_content = "# 台指期預測系統 (TAIEX Prediction)\n" + \
               "![My First Action](https://github.com/dm-nice/taifex-query/actions/workflows/ci.yml/badge.svg)\n\n" + \
               "## 最後自動更新時間: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n" + \
               "```json\n" + json.dumps(prediction, indent=4, ensure_ascii=False) + "\n```\n"

with open("README.md", "w", encoding="utf-8") as f:
    f.write(full_content)

print("多權重模型預測成功並已更新 README.md")