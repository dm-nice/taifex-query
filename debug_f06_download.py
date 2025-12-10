
import requests

URL = "https://www.taifex.com.tw/cht/7/getVixData?filesname=20251210"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36'
}

print(f"Downloading {URL}...")
try:
    resp = requests.get(URL, headers=headers, timeout=10)
    # The file is likely big5 or utf-8 text locally, typically Big5 for CSVs in TW
    resp.encoding = 'big5' 
    print(f"Status: {resp.status_code}")
    print("Content Preview:")
    print(resp.text[:500])
except Exception as e:
    print(f"Error: {e}")
