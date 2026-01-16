import requests
import time
import random

def query_twse_market_data(date_str=None):
    from utils.date_utils import get_current_taiwan_date
    if date_str is None:
        date_str = get_current_taiwan_date()
    
    query_date = date_str.replace('.', '')
    base_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
    }
    
    results = []
    session = requests.Session()
    
    try:
        # Step 0: Visit Home
        print(f"DEBUG: Visiting TWSE Home for {date_str}...")
        session.get("https://www.twse.com.tw/zh/index.html", headers=base_headers, timeout=10)
        time.sleep(random.uniform(1, 2))
        
        # 1. 抓取 F11 (MI_5MIN_HISTORY)
        f11_url = f"https://www.twse.com.tw/rwd/zh/afterTrading/MI_5MIN_HISTORY?response=json&date={query_date}"
        headers_f11 = base_headers.copy()
        headers_f11["Referer"] = "https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html"
        
        print("DEBUG: Fetching F11...")
        resp1 = session.get(f11_url, headers=headers_f11, timeout=15)
        if resp1.status_code != 200:
            print(f"DEBUG: F11 Error. Status: {resp1.status_code}")
        else:
            f11_resp = resp1.json()
            if f11_resp.get('stat') == 'OK' and 'data' in f11_resp:
                y, m, d = date_str.split('.')
                minguo_date = f"{int(y)-1911}/{m}/{d}"
                for row in f11_resp['data']:
                    if minguo_date in row[0]:
                        results.append({"f_code": "F11", "name": "加權股價", "field": "指數收盤", "value": row[4].replace(',', ''), "unit": ""})
                        break
        
        time.sleep(random.uniform(1, 2))

        # 2. 抓取 F12 (MI_INDEX Type: MS)
        f12_url = f"https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?response=json&date={query_date}&type=MS"
        headers_f12 = base_headers.copy()
        headers_f12["Referer"] = "https://www.twse.com.tw/zh/trading/historical/mi-index.html"
        
        print("DEBUG: Fetching F12...")
        resp2 = session.get(f12_url, headers=headers_f12, timeout=15)
        if resp2.status_code != 200:
            print(f"DEBUG: F12 Error. Status: {resp2.status_code}")
        else:
            f12_resp = resp2.json()
            if f12_resp.get('stat') == 'OK' and 'tables' in f12_resp:
                for table in f12_resp['tables']:
                    if "大盤統計資訊" in table.get('title', ''):
                        for row in table.get('data', []):
                            if "總計(1~15)" in row[0]:
                                results.append({"f_code": "F12", "name": "大盤統計資訊", "field": "總計成交金額", "value": row[1].replace(',', ''), "unit": ""})
                                break
                        break
        
        return results if results else None
        
    except Exception as e:
        print(f"DEBUG: TWSE Data Error: {e}")
        return None

if __name__ == "__main__":
    print("--- Testing 2026.01.15 ---")
    print(query_twse_market_data("2026.01.15"))
