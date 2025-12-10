
import requests

URL = "https://www.taifex.com.tw/cht/7/getVixData?filesname=20251210"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36'
}

print(f"Downloading {URL}...")
try:
    resp = requests.get(URL, headers=headers, timeout=10)
    resp.encoding = 'big5' 
    
    lines = resp.text.strip().split('\n')
    print(f"Total lines: {len(lines)}")
    print("Last 10 lines:")
    for line in lines[-10:]:
        print(f"[{line.strip()}]")
        parts = line.strip().split()
        if len(parts) >= 3:
            print(f"  Parsed parts: {parts}")
            print(f"  Value candidate: {parts[2]}")
        else:
            print("  Cannot parse line")

except Exception as e:
    print(f"Error: {e}")
