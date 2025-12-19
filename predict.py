import json
import os
import re
from datetime import datetime

# 1. 路徑設定
BASE_DIR = r"C:\Taifex"
DATA_DIR = os.path.join(BASE_DIR, "data")
README_FILE = os.path.join(BASE_DIR, "README.md")

def get_stock_details(text):
    """強化版解析：提取 (絕對點位, 漲跌點數, 漲跌百分比)"""
    text = str(text).replace(',', '').strip()
    pct_matches = re.findall(r"([-+]?\d*\.\d+|\d+)%", text)
    pct = float(pct_matches[-1]) if pct_matches else 0.0
    clean_text = re.sub(r'https?://\S+', '', text)
    num_matches = re.findall(r"([-+]?\d*\.\d+|\d+)", clean_text)
    val = float(num_matches[0]) if len(num_matches) > 0 else 0.0
    diff = float(num_matches[1]) if len(num_matches) > 1 else 0.0
    return val, diff, pct

def load_data():
    data = {}
    if not os.path.exists(DATA_DIR): return data, 0
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]
    for filename in files:
        tag_match = re.search(r'F\d{2}', filename.upper())
        if tag_match:
            key = tag_match.group()
            try:
                with open(os.path.join(DATA_DIR, filename), 'r', encoding='utf-8') as f:
                    data[key] = f.read().strip()
            except: data[key] = "0"
    return data, len(files)

# --- 核心執行流程 ---
raw_data, total_factors = load_data()

# 2. 解析關鍵指標 (依據你的因子配置)
f01_oi, _, _ = get_stock_details(raw_data.get('F01', '0'))      # 外資淨OI: -28731
_, f25_diff, f25_pct = get_stock_details(raw_data.get('F25', '0')) # 夜盤漲跌: +217
_, _, f24_pct = get_stock_details(raw_data.get('F24', '0'))      # ADR漲跌: +2.79%
f17_val, _, _ = get_stock_details(raw_data.get('F17', '0'))      # 外資買超: -270.05

# --- 3. 雙時間預測邏輯 ---

# A. 08:45 預測 (夜盤位階 90% + 籌碼 5% + 其他 5%)
# 將點數轉化為得分，+217點是非常強勢的表現
score_0845 = 50 + (f25_diff * 0.4 * 0.9) + (f01_oi / 1000 * 0.05) + (5 if f24_pct > 0 else -5)
res_0845 = "強勢高開" if f25_diff > 150 else ("看漲" if score_0845 > 55 else "盤整")

# B. 09:00 預測 (法人籌碼 70% + 技術/其他 30%)
# 以 F01 (-28731) 為核心壓制力
score_0900 = 50 + (f01_oi / 500 * 0.7) + (f25_diff / 10 * 0.3)
res_0900 = "高檔震盪(防拉回)" if (f01_oi < -25000 and f25_diff > 100) else ("看漲" if score_0900 > 55 else "偏空")

# 4. 封裝 JSON
result = {
    "更新時間": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    "因子總數": f"{total_factors} 項",
    "數據偵測": {
        "ADR漲跌": f"{f24_pct:+.2f}%",
        "夜盤位階": f"{f25_diff:+.0f}",
        "外資淨OI": f"{int(f01_oi)}口"
    },
    "預測結果": {
        "0845_開盤階段": res_0845,
        "0900_盤中走勢": res_0900
    },
    "分析總結": f"開盤由夜盤帶動{f25_diff:+.0f}點 | 盤中留意法人空單{int(f01_oi)}口壓力"
}

# 5. 寫入 README
CB = "```" 
json_string = json.dumps(result, indent=4, ensure_ascii=False)
readme_content = f"""# 台指期預測系統
![Action](https://github.com/dm-nice/taifex-query/actions/workflows/ci.yml/badge.svg)

## 雙階段動態分析 (依據 {total_factors} 項因子)

{CB}json
{json_string}
{CB}
"""
with open(README_FILE, "w", encoding="utf-8") as f:
    f.write(readme_content)

print(f"✅ 雙時間預測 README 更新完成！")