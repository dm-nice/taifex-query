import requests
import time
import random
from bs4 import BeautifulSoup

def diagnose_all():
    # Setup headers mimicking a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
    }
    
    session = requests.Session()
    
    # 1. Test TSMC (F14-F16)
    print("\n🚀 Testing TSMC (STOCK_DAY) for 20260115...")
    try:
        # Visit home first
        session.get("https://www.twse.com.tw/zh/index.html", headers=headers, timeout=10)
        time.sleep(1)
        
        url = "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY?date=20260115&stockNo=2330&response=json"
        h = headers.copy()
        h["Referer"] = "https://www.twse.com.tw/zh/trading/historical/stock-day.html"
        
        resp = session.get(url, headers=h, timeout=15)
        data = resp.json()
        
        if data.get('stat') == 'OK':
            # Looking for 115/01/15
            target_date = "115/01/15"
            for row in data['data']:
                if row[0] == target_date:
                    # [日期, 成交股數, 成交金額, 開盤, 最高, 最低, 收盤, 漲跌價差, 成交筆數]
                    print(f"✅ Found TSMC Data: Date={row[0]}, Vol={row[1]}, Close={row[6]}, Change={row[7]}")
                    break
        else:
            print(f"❌ TSMC Stat: {data.get('stat')}")
            
    except Exception as e:
        print(f"💥 TSMC Error: {e}")

    # 2. Test Foreign Buy (F17)
    print("\n🚀 Testing Foreign Buy (BFI82U) for 20260115...")
    try:
        time.sleep(1)
        url = "https://www.twse.com.tw/rwd/zh/fund/BFI82U?date=20260115&response=json"
        h = headers.copy()
        h["Referer"] = "https://www.twse.com.tw/zh/fund/BFI82U.html"
        
        resp = session.get(url, headers=h, timeout=15)
        data = resp.json()
        
        if data.get('stat') == 'OK':
            # Looking for "外資及陸資(不含外資自營商)"
            found = False
            for row in data['data']:
                if "外資及陸資" in row[0]:
                    # [單位, 買進, 賣出, 買賣差額]
                    print(f"✅ Found Foreign Data: {row[0]}, Net={row[3]}")
                    found = True
                    break
            if not found:
                print("❌ '外資及陸資' row not found.")
        else:
            print(f"❌ BFI82U Stat: {data.get('stat')}")

    except Exception as e:
        print(f"💥 BFI82U Error: {e}")

    # 3. Test Wantgoo (F13)
    print("\n🚀 Testing Wantgoo (F13)...")
    try:
        url = "https://www.wantgoo.com/index/0000"
        h = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=h, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Try to find Moving Average info
        # This part is tricky without browser inspection, guessing structure or searching text
        print(f"Request Status: {resp.status_code}")
        # print(resp.text[:500]) # debug
        
        # Wantgoo usually has a table or list for MAs
        # Let's search for "20日" or "MA20"
        if "20日" in resp.text:
            print("✅ Found '20日' text in HTML")
        elif "MA20" in resp.text:
             print("✅ Found 'MA20' text in HTML")
        else:
             print("❌ Keywords not found. HTML structure might be complex.")

    except Exception as e:
        print(f"💥 Wantgoo Error: {e}")

if __name__ == "__main__":
    diagnose_all()
