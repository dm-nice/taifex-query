# get_tx_foreign_oi_api.py
import requests
from typing import Optional
from datetime import datetime, timedelta

def get_tx_foreign_oi_from_api(date_str: str) -> Optional[int]:
    """
    從期交所 Open API 抓取指定日期的「台指期貨」外資未平倉淨口數 (OI)。
    使用 API 的方法更穩定、更推薦。

    Args:
        date_str (str): 查詢日期，格式為 YYYYMMDD。

    Returns:
        Optional[int]: 外資淨口數。如果找不到或發生錯誤，則返回 None。
    """
    # API 需要 YYYYMMDD 格式
    try:
        datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        print(f"錯誤：日期格式不正確 '{date_str}'，應為 YYYYMMDD。")
        return None

    # 目標 API 端點
    url = "https://openapi.taifex.com.tw/v1/MarketDataOfMajorInstitutionalTradersGeneralBytheDate"
    params = {"date": date_str}
    
    print(f"正在從 TAIFEX Open API 查詢日期 {date_str} 的資料...")

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()  # 如果 HTTP 狀態碼不是 200，則引發錯誤
        
        data = resp.json()

        if not isinstance(data, list):
            print(f"錯誤：API 回應格式非預期的列表。回應: {data}")
            return None

        # 遍歷 API 回傳的所有資料
        for record in data:
            item = record.get("Item")
            investor = record.get("InstitutionalInvestor")

            # 篩選出我們要的目標
            if item == "臺股期貨" and investor == "外資及陸資":
                net_oi_str = record.get("OpenInterest(Net)")
                try:
                    net_oi = int(net_oi_str)
                    print("成功透過 API 找到資料！")
                    return net_oi
                except (ValueError, TypeError):
                    print(f"錯誤：無法將淨口數 '{net_oi_str}' 轉換為數字。")
                    return None

        print(f"資訊：在 API 回應中找不到 {date_str} 的「臺股期貨」外資數據。")
        return None

    except requests.exceptions.RequestException as e:
        print(f"錯誤：API 網路請求失敗 - {e}")
        return None
    except Exception as e:
        print(f"錯誤：處理過程中發生未知錯誤 - {e}")
        return None

def main():
    """
    主執行函式
    """
    # --- 設定查詢日期 ---
    # 預設查詢前一個交易日 (避免當日資料尚未更新)
    today = datetime.now()
    offset = 1
    if today.weekday() == 0: # 週一，查上週五
        offset = 3
    elif today.weekday() == 6: # 週日，查上週五
        offset = 2
    
    target_date = (today - timedelta(days=offset)).strftime("%Y%m%d")
    
    print("=" * 50)
    net_oi = get_tx_foreign_oi_from_api(target_date)
    print("=" * 50)

    if net_oi is not None:
        print(f"📅 日期: {target_date}")
        print(f"📊 台指期貨外資淨未平倉口數 (OI): {net_oi:+,}")
    else:
        print(f"❌ 在 {target_date} 未能查詢到有效數據。")
        print("   可能原因：非交易日、API 尚未更新或網路問題。")

if __name__ == "__main__":
    main()