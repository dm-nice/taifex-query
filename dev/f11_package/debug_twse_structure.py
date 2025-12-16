"""
Debug script: Inspect TWSE page structure
"""

import requests
from bs4 import BeautifulSoup
import json

url = "https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html"

try:
    response = requests.get(url, timeout=10)
    response.encoding = 'utf-8'
    
    print(f"Status Code: {response.status_code}")
    print(f"Content Size: {len(response.content)} bytes")
    print("\n" + "="*60)
    print("HTML Content (first 2000 chars):")
    print("="*60)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all tables
    tables = soup.find_all('table')
    print(f"\nFound {len(tables)} table(s)")
    
    for i, table in enumerate(tables):
        print(f"\n--- Table {i} ---")
        rows = table.find_all('tr')
        print(f"Rows: {len(rows)}")
        
        if rows:
            # Print first row (header)
            header_cells = rows[0].find_all(['th', 'td'])
            headers = [cell.get_text(strip=True) for cell in header_cells]
            print(f"Headers: {headers}")
            
            # Print last row (data)
            if len(rows) > 1:
                data_cells = rows[-1].find_all(['th', 'td'])
                data = [cell.get_text(strip=True) for cell in data_cells]
                print(f"Last Row Data: {data}")
    
    # Look for divs or other structures with data
    print("\n" + "="*60)
    print("Alternative data structures:")
    print("="*60)
    
    # Look for script tags with JSON data
    scripts = soup.find_all('script')
    for i, script in enumerate(scripts):
        if script.string and ('taiex' in script.string.lower() or 'index' in script.string.lower()):
            print(f"\nScript {i} (first 500 chars):")
            print(script.string[:500])
    
    # Check for divs with data
    divs = soup.find_all('div', class_=True)
    print(f"\nFound {len(divs)} divs with class attribute")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
