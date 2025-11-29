"""
依照 interface_spec.md 規範設計

import os

def fetch(date: str) -> dict:
    """
    輸入:
        date (str): 日期字串，格式 YYYY-MM-DD
    輸出:
        dict: 統一格式 (成功或失敗)
    """
    

    # 資料檔案路徑
    data_file_path = r"c:\Taifex\data\F1_foreign_oi.txt"
    # 將輸入日期 YYYY-MM-DD 轉為 YYYYMMDD 以便比對
    date_to_find = date.replace('-', '')

    try:
        with open(data_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith(date_to_find):
                    # 找到對應日期的行，解析數值
                    # 預期格式: 20251126     F1: ...:  -318652
                    parts = line.split(':')
                    value_str = parts[-1].strip()
                    net_oi = int(value_str)
                    
                    data = {
                        "foreign_net_oi": net_oi
                    }
                    break
            else:
                # 如果迴圈正常結束 (沒有被 break)，表示沒找到資料
                raise FileNotFoundError(f"在 {os.path.basename(data_file_path)} 中找不到日期 {date} 的資料")

        return {
            "module": "f01",
            "date": date,
            "status": "success",
            "data": data,
        }
    except Exception as e:
        # 若失敗，回傳錯誤格式
        return {
            "module": "f01",
            "date": date,
            "status": "fail",
            "error": str(e),
        }

# 測試用：模組可獨立執行
if __name__ == "__main__":
    result = fetch("2025-11-26")
    print(result)
