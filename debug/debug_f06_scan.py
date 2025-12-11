
import requests
import json
import time

API_URL = "https://mis.taifex.com.tw/futures/api/getQuoteList"
TARGET_VALUES = ["20.15", "VIX", "臺指選擇權波動率指數", "Vol"]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json'
}

def scan():
    # Try different market types
    # 0: Futures? 1: Options? 2: ?
    for mt in range(0, 5):
        payload = {
            "MarketType": str(mt),
            "SymbolType": "F" # Try F first
        }
        test_payload(payload)
        
        payload["SymbolType"] = "O" # Try Options
        test_payload(payload)
        
        # Try without SymbolType
        payload = {"MarketType": str(mt)}
        test_payload(payload)

    # Try specific CIDs if known?
    payload = {"CID": "VIX"}
    test_payload(payload)
    
    payload = {"SymbolCode": "VIX"}
    test_payload(payload)

def test_payload(payload):
    try:
        print(f"Testing Payload: {payload}")
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=5)
        text = resp.text
        
        found = False
        for target in TARGET_VALUES:
            if target in text:
                print(f"!!! FOUND MATCH for '{target}' !!!")
                print(f"Response snippet: {text[:200]}")
                found = True
        
        if found:
            print("-" * 50)
            
        time.sleep(0.5)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scan()
