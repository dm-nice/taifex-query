
import requests
import json
import os

API_URL = "https://mis.taifex.com.tw/futures/api/getQuoteList"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json'
}

def dump():
    if not os.path.exists("debug_mis"):
        os.makedirs("debug_mis")

    for mt in range(0, 4):
        payload = {"MarketType": str(mt)}
        print(f"Dumping MarketType {mt}...")
        try:
            resp = requests.post(API_URL, json=payload, headers=headers, timeout=10)
            with open(f"debug_mis/mt_{mt}.json", "w", encoding="utf-8") as f:
                f.write(resp.text)
        except Exception as e:
            print(f"Error {mt}: {e}")

if __name__ == "__main__":
    dump()
