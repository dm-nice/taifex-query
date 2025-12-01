import requests
from datetime import datetime, timedelta

def test_taifex_api():
    # 先抓昨天日期（避免今天還沒更新）
    target_date = (datetime.today() - timedelta(days=1)).strftime("%Y/%m/%d")

    url = "https://openapi.taifex.com.tw/v1/MarketDataOfMajorInstitutionalTradersGeneralBytheDate"
    params = {"date": target_date}

    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()  # 如果 API 有錯誤會丟出例外
        data = resp.json()

        print("✅ API 正常回傳")
        print("查詢日期:", target_date)
        print("回傳筆數:", len(data))
        print("前 3 筆資料:", data[:3])  # 只印前幾筆看看

    except Exception as e:
        print("❌ API 呼叫失敗:", e)

if __name__ == "__main__":
    test_taifex_api()