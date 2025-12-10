
import requests
from datetime import datetime

URL = "https://www.taifex.com.tw/cht/7/vixMinNew"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36'
}

try:
    print(f"Fetching {URL}...")
    resp = requests.get(URL, headers=headers, timeout=10)
    resp.encoding = 'utf-8'
    print(f"Status: {resp.status_code}")
    
    # Dump relevant part of HTML
    if "2025/12/10" in resp.text:
        print("Found date '2025/12/10' in response!")
        lines = resp.text.split('\n')
        for i, line in enumerate(lines):
            if "2025/12/10" in line:
                print(f"Context around line {i}:")
                for j in range(max(0, i-5), min(len(lines), i+10)):
                    print(f"{j}: {lines[j].strip()}")
    else:
        print("Date '2025/12/10' NOT found in response.")
        
except Exception as e:
    print(f"Error: {e}")
