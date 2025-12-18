import json
import os
from datetime import datetime

# 1. 數據目錄 (請確認此路徑下有 F01.txt, F17.txt 等檔案)
DATA_DIR = r"C:\Taifex\data"

def get_latest_factors():
    factors = {}
    print("正在掃描目錄:", DATA_DIR)
    try:
        if not os.path.exists(DATA_DIR):
            print("【錯誤】找不到數據目錄！")
            return factors
        
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".txt"):
                factor_key = filename.split('.')[0]
                with open(os.path.join(DATA_DIR, filename), 'r', encoding='utf-8') as f:
                    val = f.read().strip().replace(',', '')
                    factors[factor_key] = val
        print("讀取到的因子清單:", list(factors.keys()))
    except Exception as e:
        print("讀取失敗:", e)
    return factors

def analyze_logic(factors):
    # 根據您的截圖數據 F01 與 F17 進行邏輯判斷
    f01 = float(factors.get('F01', 0))
    f17 = float(factors.get('F17', 0))
    
    if f01 < -25000:
        return "下跌", "85", "外資期貨空單水位極高，市場賣壓沉重。"
    elif f01 > 5000:
        return "上漲", "70", "外資期貨多單轉強，支撐力道增加。"
    else:
        return "盤整", "60", "籌碼指標中性，預期區間震盪。"

# 執行主流程
factors_data = get_latest_factors()
res, conf, summary = analyze_logic(factors_data)

# 建立預測 JSON 內容 (符合 輸出格式.md)
prediction = {
    "數據日期": datetime.now().strftime('%Y/%m/%d'),
    "隔日預測結果": res,
    "預測漲跌點數範圍": "-100 至 -250" if res == "下跌" else "+50 至 +150",
    "信心分數": conf,
    "關鍵驅動因子": {
        "強度因子一": "F01(外資淨OI): " + factors_data.get('F01', '0') + " 口",
        "強度因子二": "F17(外資現貨買賣超): " + factors_data.get('F17', '0') + " 億元"
    },
    "推理總結": summary
}

prediction_json = json.dumps(prediction, indent=4, ensure_ascii=False)

# 寫入 README.md (改用字串相加，避開 f-string)
header = "# 台指期預測系統 (TAIEX Prediction)\n"
badge = "![My First Action](https://github.com/dm-nice/taifex-query/actions/workflows/ci.yml/badge.svg)\n\n"
time_line = "## 最後自動更新時間: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n"
json_block = "```json\n" + prediction_json + "\n```\n"

full_readme = header + badge + time_line + json_block

with open("README.md", "w", encoding="utf-8") as f:
    f.write(full_readme)

print("---")
print("README.md 更新成功！")