import os
from scrapers.daytime import query_daytime_data
from utils.helpers import save_to_markdown
from utils.date_utils import get_current_taiwan_date

def main():
    print(f"🚀 開始執行日盤資料抓取... ({get_current_taiwan_date()})")
    
    # 執行抓取
    data = query_daytime_data()
    
    if data:
        # 顯示結果摘要
        print("\n📊 抓取結果摘要:")
        for item in data:
            val = item.get('value', 'N/A')
            unit = item.get('unit', '')
            print(f"  - {item['f_code']} {item['name']}: {val} {unit}")
            
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
