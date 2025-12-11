
import requests
import json

URL = "https://mis.taifex.com.tw/futures/VolatilityQuotes/"
API_URL = "https://mis.taifex.com.tw/futures/api/getQuoteList"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

print(f"1. Checking Main Page: {URL}")
try:
    resp = requests.get(URL, headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    if "20.15" in resp.text:  # Try to find the value seen in screenshot
        print("FOUND data in HTML!")
    else:
        print("Data NOT found in HTML (likely CSR).")
except Exception as e:
    print(f"Error fetching page: {e}")

print(f"\n2. Checking API: {API_URL}")
# MIS API usually requires specific payload. 
# Typical payload for Quotes usually involves MarketType and Symbol info.
# For Volatility, let's try a generic or sniffed payload guess.
# Based on typical Mis Taifex structure:
payload = {
    "MarketType": "0",  # Futures/Options
    "SymbolType": "F"   # Just a guess, might be different for VIX
}

# However, MIS usually uses a specific 'CID' or 'SymbolID' list.
# Let's try to get all quotes or commonly used list.
# Actually, for VIX, the symbol is usually 'RTVI'. 
# Let's try to fetch quote for 'RTVI'.
payload_vix = {
    "MarketType": "2", # 0:Fut, 1:Opt, 2:?
    "SymbolCode": "RTVI" 
}

# Another common endpoint is getQuoteList with CID
payload_cid = {
    "CID": "", # Empty likely returns nothing?
}

# Let's try a POST with empty body first to see if it complains
try:
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=10)
    print(f"API Status: {resp.status_code}")
    print(f"API Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error fetching API: {e}")
