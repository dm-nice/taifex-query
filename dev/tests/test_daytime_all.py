from scrapers.daytime import query_daytime_data
from utils.helpers import save_to_markdown
from utils.date_utils import get_current_taiwan_date

def test_run():
    print("🚀 測試日盤資料抓取 (F01-F04)...")
    data = query_daytime_data()
    
    if data:
        print("✅ 獲取成功:")
        for item in data:
            print(f"{item['f_code']} {item['name']}: {item['value']} {item.get('unit', '')}")
        
        path = save_to_markdown(data)
        print(f"📄 測試結果存檔: {path}")
    else:
        print("❌ 抓取失敗")

if __name__ == "__main__":
    test_run()
