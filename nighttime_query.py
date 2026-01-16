import os
from scrapers.nighttime import query_nighttime_data
from utils.helpers import save_to_markdown
from utils.date_utils import get_current_taiwan_date

def main():
    print(f"🌙 開始執行盤後資料抓取... ({get_current_taiwan_date()})")
    
    data = query_nighttime_data()
    
    if data:
        print("\n📊 抓取結果摘要:")
        for item in data:
            print(f"  - {item['f_code']} {item['name']}: {item['value']} {item.get('unit', '')}")
            
        # 存檔 (檔案名稱可能需要區分日盤/夜盤? save_to_markdown logic?)
        # utils/helpers.py logic: save_to_markdown(data, prefix="taifex_")
        # Let's check save_to_markdown signature or default behavior.
        # Ideally, we pass a filename prefix.
        
        filepath = save_to_markdown(data, filename_prefix="taifex_night_")
        # Assuming save_to_markdown accepts filename_prefix?
        # I'll check utils/helpers.py content next.
        # But if not, it defaults to 'taifex_YYYY...'. It might overwrite.
        # I should check helpers.py.
        
        print(f"\n✅ 報告已儲存: {filepath}")
    else:
        print("\n❌ 抓取失敗或無資料")

if __name__ == "__main__":
    main()
