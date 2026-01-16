import os
import re
from datetime import datetime
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
    
    lines = []
    for item in data_list:
        f_code = item.get('f_code', 'F00')
        name = item.get('name', '未知項目')
        value = item.get('value', '查詢失敗')
        unit = item.get('unit', '')
        
        # 格式化每行: 2026.01.15 F01 台指期貨-外資 [ 未平倉 多空淨額: -181389口 ]
        if value == "保留項目":
            line = f"{date_str} {f_code} [保留項目]"
        elif value == "查詢失敗":
            line = f"{date_str} {f_code} {name} [ 查詢失敗 ]"
        else:
            # 判斷是否需要單位
            unit_str = f"{unit}" if unit else ""
            line = f"{date_str} {f_code} {name} [ {item.get('field', '')}: {value}{unit_str} ]"
        
        lines.append(line)
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
        
    return file_path
