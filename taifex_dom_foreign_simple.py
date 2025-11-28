import requests
import pandas as pd
import os
from datetime import datetime, timedelta

def fetch_taifex_foreign_data():
    # 自動抓昨天日期（避免今天還沒更新）
    target_date = (datetime.today() - timedelta(days=1)).strftime("%Y/%m/%d")

    url = "https://openapi.taifex.com.tw/v1/MarketDataOfMajorInstitutionalTradersGeneralBytheDate"
    params = {"date": target_date}

    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        print("✅ API 正常回傳")
        print("資料日期:", target_date)
        print("資料筆數:", len(data))

        # 篩選外資資料（Item 欄位）
        foreign_items = ["外資及陸資", "外資", "外資及陸資法人"]
        filtered = [row for row in data if row.get("Item") in foreign_items]

        if not filtered:
            print("⚠️ 找不到外資資料，可能是 API 尚未更新")
            return

        df = pd.DataFrame(filtered)

        # 建立資料夾
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(data_dir, exist_ok=True)

        # 儲存 CSV
        date_str = target_date.replace("/", "")
        filename = f"taifex_{date_str}_foreign.csv"
        filepath = os.path.join(data_dir, filename)
        df.to_csv(filepath, index=False, encoding="utf-8-sig")

        print(f"✅ 已儲存外資資料至：{filepath}")
        print("📊 儲存筆數:", len(df))

    except Exception as e:
        print("❌ API 呼叫或儲存失敗:", e)

if __name__ == "__main__":
    fetch_taifex_foreign_data()