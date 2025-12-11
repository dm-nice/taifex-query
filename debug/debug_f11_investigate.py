
import requests
import json

# Target URL: TWSE Daily Index
# date=YYYYMMDD, type=IND for indices
URL = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date=20251210&type=IND&response=json"

print(f"Fetching {URL}...")
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36'
    }
    response = requests.get(URL, headers=headers, timeout=15)
    
    if response.status_code == 200:
        data = response.json()
        print("Stat:", data.get('stat'))
        print("Date:", data.get('date'))
        
        # Check tables
        tables = data.get('tables', [])
        print(f"Total tables: {len(tables)}")
        
        for idx, tbl in enumerate(tables):
            title = tbl.get('title', '')
            fields = tbl.get('fields', [])
            print(f"Table {idx}: {title}")
            print(f"  Fields: {fields}")
            
            # Inspect first 3 rows
            rows = tbl.get('data', [])
            for row in rows[:5]:
                print(f"  Row: {row}")
                # Looking for "發行量加權股價指數"
                if "發行量加權股價指數" in str(row) or "TAIEX" in str(row):
                    print("  Found Target Row:", row)
    else:
        print(f"HTTP Error: {response.status_code}")

except Exception as e:
    print(f"Error: {e}")
