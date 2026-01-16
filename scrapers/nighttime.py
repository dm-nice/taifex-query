import requests
from bs4 import BeautifulSoup
from utils.date_utils import get_current_taiwan_date

def query_taifex_night_tx(date_str=None):
    """
    F21: 盤後台指期-收盤價
    F22: 盤後台指期-成交量
    From futDailyMarketReport with marketCode=1
    """
    if date_str is None:
        date_str = get_current_taiwan_date()
        
    query_date = date_str.replace('.', '/')
    url = "https://www.taifex.com.tw/cht/3/futDailyMarketReport"
    
    # queryType=2, marketCode=1 (Night)
    payload = {
        "queryType": "2", 
        "marketCode": "1", 
        "commodity_id": "TX", 
        "queryDate": query_date
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='table_f')
        
        results = []
        if table:
            for row in table.find_all('tr'):
                col_text = row.get_text(strip=True)
                # 排除小台 (MTX) ? 網頁選 TX 通常只有 TX
                # 確認第一欄包含 TX 且年份 (避免標題)
                tds = row.find_all('td')
                if len(tds) > 10 and "TX" in tds[0].get_text():
                    # Columns usually:
                    # 0: Contract (TX 202601)
                    # 1: Open
                    # 2: High
                    # 3: Low
                    # 4: Close (成交價 of Night)
                    # 5: Change
                    # 6: Change%
                    # 7: Volume (成交量)
                    # 8: Settlement
                    # 9: OI
                    # ...
                    
                    # Check diagnose output structure or F04 logic.
                    # F04: price = tds[5] in day report?
                    # Let's count generic taifex columns:
                    # 商品, 開盤, 最高, 最低, 收盤(成交), 漲跌, %, 量, 結算, OI...
                    # Count: 0, 1, 2, 3, 4?
                    
                    # Safer: Check header? No, just use index 5 (Close) and 8 (Vol)?
                    # Wait, diagnose output: "30940 30990 30657 30841"
                    # Open(1), High(2), Low(3), Close(4)?
                    
                    close = tds[5].get_text(strip=True) # Usually index 5 is consistent with Day?
                    # Let's verify F04 logic in daytime.py
                    # "if len(tds) > 5 and ... price = tds[5]" from Step 501.
                    # So index 5 is Price.
                    
                    vol = tds[8].get_text(strip=True) # Volume?
                    # If index 5 is Close.
                    # 6 is Change, 7 is %, 8 is Volume?
                    # Diagnose string: "0.45%52310".
                    # Percentage is index 7. Volume is index 8.
                    
                    if close != "-":
                         results.append({"f_code": "F21", "name": "盤後台指期", "field": "收盤價", "value": close, "unit": ""})
                    if vol != "-":
                         results.append({"f_code": "F22", "name": "盤後台指期", "field": "成交量", "value": vol, "unit": "口"})
                    
                    return results
                    
        return None
        
    except Exception as e:
        print(f"Night TX Error: {e}")
        return None

def query_nighttime_data(date_str=None):
    results = []
    
    # Get Night TX
    r1 = query_taifex_night_tx(date_str)
    if r1: results.extend(r1)
    
    # Handle F06 here if needed? No, F06 is VIX (Daytime).
    
    # Sort
    results.sort(key=lambda x: x['f_code'])
    return results
