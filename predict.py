import json
import os
from datetime import datetime

# 1. 數據與歷史檔案路徑
BASE_DIR = r"C:\Taifex"
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")

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

def calculate_logic(factors):
    # 讀取當前數值
    f11_now = float(factors.get('F11', 0)) # 加權指數
    f14_now = float(factors.get('F14', 0)) # 台積電
    f01 = float(factors.get('F01', 0))    # 外資淨OI
    
    # 讀取歷史紀錄
    history = {"win_count": 0, "total_count": 0, "last_prediction": "", "last_f11": 0, "last_f14": 0}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history.update(json.load(f))

    # --- A. 勝率計算 ---
    if history["last_prediction"] and history["last_f11"] > 0:
        actual_move = "上漲" if f11_now > history["last_f11"] else "下跌"
        history["total_count"] += 1
        if actual_move == history["last_prediction"]:
            history["win_count"] += 1
    
    win_rate = (history["win_count"] / history["total_count"] * 100) if history["total_count"] > 0 else 0

    # --- B. 技術面斜率評分 ---
    score = 50
    reasons = []
    
    # 台積電斜率判斷 (F14)
    if history["last_f14"] > 0:
        slope = f14_now - history["last_f14"]
        if slope > 5:
            score += 15; reasons.append(f"台積電斜率向上(+{slope})")
        elif slope < -5:
            score -= 15; reasons.append(f"台積電斜率向下({slope})")

    # 籌碼面權重 (F01)
    if f01 < -25000: score -= 20; reasons.append("期貨空單壓力")

    # 判定最終結果
    res = "上漲" if score > 55 else ("下跌" if score < 45 else "盤整")
    
    # 更新歷史紀錄
    history.update({
        "last_prediction": res,
        "last_f11": f11_now,
        "last_f14": f14_now
    })
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4)

    return res, f"{win_rate:.1f}%", " | ".join(reasons) if reasons else "指標中性"

# 執行並更新 README
factors = get_latest_factors()
res, win_rate_str, summary = calculate_logic(factors)

prediction = {
    "數據日期": datetime.now().strftime('%Y/%m/%d'),
    "隔日預測結果": res,
    "系統歷史勝率": win_rate_str,
    "關鍵驅動因子": {
        "技術面因子": "F11(大盤): " + factors.get('F11', '0') + " / F14(台積電): " + factors.get('F14', '0'),
        "籌碼面因子": "F01(外資淨OI): " + factors.get('F01', '0')
    },
    "推理總結": summary
}

# 寫入 README.md
full_content = "# 台指期預測系統 (TAIEX Prediction)\n" + \
               "![My First Action](https://github.com/dm-nice/taifex-query/actions/workflows/ci.yml/badge.svg)\n\n" + \
               "## 最後自動更新時間: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n" + \
               "```json\n" + json.dumps(prediction, indent=4, ensure_ascii=False) + "\n```\n"

with open(os.path.join(BASE_DIR, "README.md"), "w", encoding="utf-8") as f:
    f.write(full_content)

print(f"系統已更新。歷史檔案路徑: {HISTORY_FILE}")