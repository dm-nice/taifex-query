import os
from scrapers.daytime import query_daytime_data
from utils.helpers import save_to_markdown
from utils.date_utils import get_current_taiwan_date

def main():
    # 確保 output 目錄存在
    os.makedirs("output", exist_ok=True)

    print(f"🚀 開始執行日盤資料抓取... ({get_current_taiwan_date()})")
    
    # 執行抓取
    data = query_daytime_data()
    
    if data:
        # 顯示結果摘要
        current_date = get_current_taiwan_date()
        print(f"\n{current_date}")
        print("📊 抓取結果摘要:")
        for item in data:
            f_code = item.get('f_code', 'F00')
            name = item.get('name', '')
            field = item.get('field', '')
            value = item.get('value', 'N/A')

            if 'field2' in item and 'value2' in item:
                # 多欄位格式 (F04/F11/F14)
                field2 = item.get('field2', '')
                value2 = item.get('value2', '')
                print(f"  - {f_code} {name}  [{field}: {value}]  [{field2}: {value2}]")
            else:
                print(f"  - {f_code} {name}  [{field}: {value}]")
            
        # 存檔
        filepath = save_to_markdown(data)
        if filepath:
            print(f"\n✅ 報告已儲存: {filepath}")
        else:
            print("\n⚠️ 存檔失敗")
    else:
        print("\n❌ 抓取失敗或無資料")

if __name__ == "__main__":
    main()
