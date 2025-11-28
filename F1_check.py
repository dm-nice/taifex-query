import requests
from datetime import datetime, timedelta

def check_institutional_list(date_str: str = None, debug_mode: bool = True):
    """
    檢查指定日期的三大法人資料是否包含外資
    - date_str: 格式 YYYYMMDD，若為 None 則使用今天日期
    """
    # 日期處理
    if date_str is None:
        date_str = datetime.today().strftime("%Y%m%d")

    # API 查詢網址（加上 ?date=YYYYMMDD）
    url = f"https://openapi.taifex.com.tw/v1/MarketDataOfMajorInstitutionalTradersGeneralBytheDate?date={date_str}"

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        print(f"📅 查詢日期：{date_str}")
        print(f"📦 回傳筆數：{len(data)}")
        found = False

        for row in data:
            name = row.get("InstitutionalInvestor") or row.get("Item")
            futures_net = row.get("FuturesNet") or row.get("OpenInterest(Net)")
            print(f"法人：{name}，期貨淨額：{futures_net}")
            if name == "外資":
                found = True

        if not found:
            print("⚠️ 沒有找到『外資』資料，可能該日尚未更新或非交易日")

    except Exception as e:
        print("❌ API 抓取失敗：", e)

# 測試入口：查今天與前一天
if __name__ == "__main__":
    today = datetime.today()
    yesterday = today - timedelta(days=1)

    check_institutional_list(date_str=today.strftime("%Y%m%d"))
    print("\n--- 改查前一天 ---\n")
    check_institutional_list(date_str=yesterday.strftime("%Y%m%d"))