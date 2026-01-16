from scrapers.daytime import query_daytime_data
from utils.helpers import save_to_markdown
from utils.date_utils import get_current_taiwan_date

def test_run():
    print("🚀 開始測試 F01-F03 爬取...")
    data = query_daytime_data()
    
    if data:
        print("✅ 成功獲取數據:")
        for item in data:
            print(f"{item['f_code']}: {item['value']} {item['unit']}")
        
        path = save_to_markdown(data)
        print(f"📄 已產出測試檔案: {path}")
    else:
        print("❌ 爬取失敗，請檢查網路或期交所格式是否變動")

if __name__ == "__main__":
    test_run()
