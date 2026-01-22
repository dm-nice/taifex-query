import os
from scrapers.nighttime import query_nighttime_data
from utils.helpers import save_to_markdown
from utils.date_utils import get_current_taiwan_date

def main():
    # 確保 output 目錄存在
    os.makedirs("output", exist_ok=True)

    print(f"Nighttime data scraper... ({get_current_taiwan_date()})")

    data = query_nighttime_data()

    if data:
        print("\nFetch Summary:")
        for item in data:
            print(f"  - {item['f_code']} {item['name']}: {item['value']} {item.get('unit', '')}")

        # 存檔 (使用 taifex_night_ 前綴區分夜盤數據)
        filepath = save_to_markdown(data, filename_prefix="taifex_night_")

        if filepath:
            print(f"\nFile saved: {filepath}")
        else:
            print("\nFailed to save file")
    else:
        print("\nFetch failed or no data")

if __name__ == "__main__":
    main()
