import os
import re
from utils.date_utils import get_current_taiwan_date

def get_next_version(date_str=None, filename_prefix="taifex_"):
    """
    掃描 output 目錄，根據當日日期決定下一個版本號 (v1, v2, ...)
    """
    if date_str is None:
        date_str = get_current_taiwan_date()
        
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Escape prefix for regex
    safe_prefix = re.escape(filename_prefix)
    pattern = re.compile(rf"{safe_prefix}{date_str}_v(\d+)\.md")
    max_version = 0
    
    for filename in os.listdir(output_dir):
        match = pattern.match(filename)
        if match:
            version = int(match.group(1))
            if version > max_version:
                max_version = version
                
    return max_version + 1

def save_to_markdown(data_list, date_str=None, version=None, filename_prefix="taifex_"):
    """
    將資料列表保存為 Markdown 檔案
    data_list: 包含字典的列表，例如 [{'f_code': 'F01', 'name': '...', 'value': '...', 'unit': '...'}]
    """
    if date_str is None:
        date_str = get_current_taiwan_date()
    
    if version is None:
        version = get_next_version(date_str, filename_prefix)
        
    file_path = os.path.join("output", f"{filename_prefix}{date_str}_v{version}.md")
    
    # 第1行加上執行日期和交易時段
    if "night" in filename_prefix:
        lines = [f"{date_str} 夜盤交易"]
    else:
        lines = [f"{date_str} 日盤交易"]
    for item in data_list:
        f_code = item.get('f_code', 'F00')
        name = item.get('name', '未知項目')
        value = item.get('value', '查詢失敗')
        field = item.get('field', '')
        if value == "保留項目":
            line = f"{f_code} [保留項目]"
        elif value == "查詢失敗":
            line = f"{f_code} {name}  [查詢失敗]"
        elif 'price' in item:
            # 夜盤格式 (F21-F25): F25 台指期盤後 : 23456.78 [+36 , +0.15%]
            line = f"{f_code} {name}  : {value}"
        elif 'field2' in item and 'value2' in item:
            # 多欄位格式 (F04/F11/F14): F04 臺股期貨-當日收盤價  [最後成交價: 32777]  [漲跌價差: -148]
            field2 = item.get('field2', '')
            value2 = item.get('value2', '')
            line = f"{f_code} {name}  [{field}: {value}]  [{field2}: {value2}]"
        else:
            # 日盤格式: F01 臺股期貨-外資 多空淨額口數  [請填入:未平倉口數]
            line = f"{f_code} {name}  [{field}: {value}]"
        
        lines.append(line)
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(lines) + "\n")
        
    return file_path
