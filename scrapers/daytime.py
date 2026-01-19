import requests
import time
import random
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
from utils.date_utils import get_current_taiwan_date, get_previous_trading_day

# --- Constants ---
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

BASE_HEADERS_TAIFEX = {
    "User-Agent": USER_AGENT,
    "Origin": "https://www.taifex.com.tw"
}

BASE_HEADERS_TWSE = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
}

def _get_session(existing_session: Optional[requests.Session] = None) -> requests.Session:
    """Helper to get an existing session or create a new one."""
    if existing_session:
        return existing_session
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s

def _random_sleep():
    """Sleep for a short random duration to be polite."""
    time.sleep(random.uniform(0.5, 1.0))

# --- Taifex Scrapers ---

def query_taifex_foreign_holdings(date_str: Optional[str] = None, session: Optional[requests.Session] = None) -> Optional[List[Dict[str, Any]]]:
    """F01-F03: 台指期貨外資持倉"""
    if date_str is None:
        date_str = get_current_taiwan_date()
        
    query_date = date_str.replace('.', '/')
    url = "https://www.taifex.com.tw/cht/3/totalTableDate"
    payload = {"queryDate": query_date, "queryType": "", "goDay": "", "doQuery": "", "dateaddcnt": ""}
    
    headers = BASE_HEADERS_TAIFEX.copy()
    headers["Referer"] = url
    
    sess = _get_session(session)
    try:
        # Visit page first to set cookies if needed (though API might not strictly require it, it's safer)
        if not session: # Only if we created a new session, or just do it once? 
            # To be safe and mimic browser, GET then POST
            sess.get(url, headers=headers, timeout=10)
            
        response = sess.post(url, data=payload, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Parse logic
        target_table = None
        for t in soup.find_all('table', class_='table_f'):
            if "未平倉" in t.get_text():
                target_table = t
                break
                
        if not target_table: return None
        
        foreign_row = None
        for row in target_table.find_all('tr'):
            if "外資" in row.get_text():
                foreign_row = row
                break
                
        if not foreign_row: return None
        
        cols = foreign_row.find_all(['td', 'th'])
        if len(cols) < 7: return None
        
        f02_val = cols[1].get_text(strip=True).replace(',', '')
        f03_val = cols[3].get_text(strip=True).replace(',', '')
        f01_val = cols[5].get_text(strip=True).replace(',', '')
        
        return [
            {"f_code": "F01", "name": "台指期貨-外資", "field": "未平倉 多空淨額", "value": f01_val, "unit": "口"},
            {"f_code": "F02", "name": "台指期貨-外資", "field": "未平倉 多方", "value": f02_val, "unit": "口"},
            {"f_code": "F03", "name": "台指期貨-外資", "field": "未平倉 空方", "value": f03_val, "unit": "口"},
        ]
    except Exception as e:
        print(f"F01-F03 Error: {e}")
        return None

def query_taifex_settlement(date_str: Optional[str] = None, session: Optional[requests.Session] = None) -> Optional[List[Dict[str, Any]]]:
    """F04: 臺指期貨收盤價"""
    if date_str is None:
        date_str = get_current_taiwan_date()
    query_date = date_str.replace('.', '/')
    url = "https://www.taifex.com.tw/cht/3/futDailyMarketReport"
    payload = {"queryType": "2", "marketCode": "0", "commodity_id": "TX", "queryDate": query_date}
    
    sess = _get_session(session)
    try:
        response = sess.post(url, data=payload, headers=BASE_HEADERS_TAIFEX, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='table_f')
        
        if not table: return None
        
        for row in table.find_all('tr'):
            tds = row.find_all('td')
            # Check row for "TX" (but not MTX) and ensure enough columns
            if len(tds) > 5 and "TX" in tds[0].get_text(strip=True):
                price = tds[5].get_text(strip=True)
                if price != "-":
                    return [{"f_code": "F04", "name": "台指期貨-當日收盤", "field": "最後成交價", "value": price, "unit": ""}]
        return None
    except Exception as e:
        print(f"F04 Error: {e}")
        return None

def query_taifex_options_volume(date_str: Optional[str] = None, session: Optional[requests.Session] = None) -> Optional[List[Dict[str, Any]]]:
    """F05: 臺指選擇權總成交量 (純日盤)"""
    if date_str is None:
        date_str = get_current_taiwan_date()
    query_date = date_str.replace('.', '/')
    url = "https://www.taifex.com.tw/cht/3/optDailyMarketReport"
    payload = {"queryType": "2", "marketCode": "0", "commodity_id": "TXO", "queryDate": query_date}
    
    sess = _get_session(session)
    try:
        response = sess.post(url, data=payload, headers=BASE_HEADERS_TAIFEX, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='table_f')
        
        if not table: return None
        
        # Optimize: Search for "小計" from bottom up
        for row in reversed(table.find_all('tr')):
            if "小計" in row.get_text():
                cols = row.find_all('td')
                for td in cols:
                    text = td.get_text(strip=True).replace(',', '')
                    if text.isdigit():
                        return [{"f_code": "F05", "name": "台指選擇權-當日", "field": "選擇權總成交量", "value": text, "unit": ""}]
        return None
    except Exception as e:
        print(f"F05 Error: {e}")
        return None

def query_taifex_pc_ratio(date_str: Optional[str] = None, session: Optional[requests.Session] = None) -> Optional[List[Dict[str, Any]]]:
    """F07: 臺指選擇權 Put/Call Ratio"""
    if date_str is None:
        date_str = get_current_taiwan_date()
    
    d_parts = date_str.split('.')
    query_date_short = f"{d_parts[0]}/{int(d_parts[1])}/{int(d_parts[2])}"
    
    url = f"https://www.taifex.com.tw/cht/3/pcRatio?queryDate={date_str.replace('.','/')}"
    
    sess = _get_session(session)
    try:
        response = sess.get(url, headers=BASE_HEADERS_TAIFEX, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='table_f')
        
        if not table: return None
        
        for row in table.find_all('tr'):
            if query_date_short in row.get_text():
                cols = row.find_all('td')
                if len(cols) >= 7:
                    return [{"f_code": "F07", "name": "臺指選擇權Put/Call", "field": "買賣權未平倉量比率%", "value": cols[6].get_text(strip=True), "unit": ""}]
        return None
    except Exception as e:
        print(f"F07 Error: {e}")
        return None

# --- TWSE Scrapers ---

def query_twse_market_data(date_str: Optional[str] = None, session: Optional[requests.Session] = None) -> Optional[List[Dict[str, Any]]]:
    """爬取 F11: 加權股價指數(收盤) 與 F12: 大盤成交金額"""
    if date_str is None:
        date_str = get_current_taiwan_date()
    
    query_date = date_str.replace('.', '')
    sess = _get_session(session)
    results = []
    
    try:
        # Pre-flight check (if not visited, maybe good to visit home once)
        # But assuming session passed from main usually has cookies ready
        _random_sleep()
        
        # 1. F11 (MI_5MINS_HIST)
        f11_url = f"https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST?response=json&date={query_date}"
        f11_headers = BASE_HEADERS_TWSE.copy()
        f11_headers["Referer"] = "https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html"
        
        f11_resp = sess.get(f11_url, headers=f11_headers, timeout=15).json()
        if f11_resp.get('stat') == 'OK' and 'data' in f11_resp:
            y, m, d = date_str.split('.')
            minguo_date = f"{int(y)-1911}/{m}/{d}"
            for row in f11_resp['data']:
                if minguo_date in row[0]:
                    # row[4] is Closing Index
                    results.append({"f_code": "F11", "name": "加權股價", "field": "指數收盤", "value": row[4].replace(',', ''), "unit": ""})
                    break

        _random_sleep()

        # 2. F12 (MI_INDEX Type: MS)
        f12_url = f"https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?response=json&date={query_date}&type=MS"
        f12_headers = BASE_HEADERS_TWSE.copy()
        f12_headers["Referer"] = "https://www.twse.com.tw/zh/trading/historical/mi-index.html"
        
        f12_resp = sess.get(f12_url, headers=f12_headers, timeout=15).json()
        if f12_resp.get('stat') == 'OK' and 'tables' in f12_resp:
            for table in f12_resp['tables']:
                if "大盤統計資訊" in table.get('title', ''):
                    for row in table.get('data', []):
                        if "總計(1~15)" in row[0]: # Total Turnover
                            # row[1] is Transaction Amount
                            results.append({"f_code": "F12", "name": "大盤統計資訊", "field": "總計成交金額", "value": row[1].replace(',', ''), "unit": ""})
                            break
                    break

        return results if results else None
    except Exception as e:
        print(f"F11/F12 Error: {e}")
        return None

def query_twse_stock_day(session: requests.Session, date_str: str, stock_no: str = "2330") -> Optional[List[Dict[str, Any]]]:
    """爬取 F14-F16: 個股日成交資訊 (預設台積電)"""
    _random_sleep()
    query_date = date_str.replace('.', '')
    y, m, d = date_str.split('.')
    minguo_date = f"{int(y)-1911}/{m}/{d}"
    
    url = f"https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY?date={query_date}&stockNo={stock_no}&response=json"
    headers = BASE_HEADERS_TWSE.copy()
    headers["Referer"] = "https://www.twse.com.tw/zh/trading/historical/stock-day.html"
    
    try:
        resp = session.get(url, headers=headers, timeout=15).json()
        if resp.get('stat') == 'OK' and 'data' in resp:
            for row in resp['data']:
                if row[0] == minguo_date:
                    close = row[6].replace(',', '')
                    change = row[7].replace(',', '').replace('+', '').replace('X', '') 
                    vol_shares = int(row[1].replace(',', ''))
                    vol_lots = vol_shares // 1000
                    
                    return [
                        {"f_code": "F14", "name": f"{stock_no}台積電-當日", "field": "收盤價", "value": close, "unit": ""},
                        {"f_code": "F15", "name": f"{stock_no}台積電-當日", "field": "漲跌價差", "value": change, "unit": ""},
                        {"f_code": "F16", "name": f"{stock_no}台積電-當日", "field": "成交張數", "value": str(vol_lots), "unit": "張"},
                    ]
        return None
    except Exception as e:
        print(f"F14-F16 Error: {e}")
        return None

def query_twse_foreign_buy(session: requests.Session, date_str: str) -> Optional[List[Dict[str, Any]]]:
    """爬取 F17: 外資及陸資買賣超"""
    _random_sleep()
    query_date = date_str.replace('.', '')
    url = f"https://www.twse.com.tw/rwd/zh/fund/BFI82U?date={query_date}&response=json"
    headers = BASE_HEADERS_TWSE.copy()
    headers["Referer"] = "https://www.twse.com.tw/zh/fund/BFI82U.html"
    
    try:
        resp = session.get(url, headers=headers, timeout=15).json()
        if resp.get('stat') == 'OK' and 'data' in resp:
            for row in resp['data']:
                if "外資及陸資" in row[0]:
                    net_buy = row[3].replace(',', '')
                    return [{"f_code": "F17", "name": "台灣股票外資及陸資", "field": "買賣差額", "value": net_buy, "unit": ""}]
        return None
    except Exception as e:
        print(f"F17 Error: {e}")
        return None

def query_daytime_data(date_str: Optional[str] = None) -> List[Dict[str, Any]]:
    """Main aggregation function for Daytime Data"""
    if date_str is None:
        date_str = get_current_taiwan_date()
        
    def fetch_all_with_fallback(d):
        res = []
        
        # 1. Create a Shared Session for Taifex
        session_taifex = _get_session()
        
        # 2. Create a Shared Session for TWSE (with keep-alive)
        session_twse = _get_session()
        # Warm-up TWSE session to get cookies
        try:
             session_twse.get("https://www.twse.com.tw/zh/index.html", headers=BASE_HEADERS_TWSE, timeout=5)
        except: pass

        # --- Taifex Queries ---
        r1 = query_taifex_foreign_holdings(d, session_taifex); (res.extend(r1) if r1 else None)
        r2 = query_taifex_settlement(d, session_taifex); (res.extend(r2) if r2 else None)
        r3 = query_taifex_options_volume(d, session_taifex); (res.extend(r3) if r3 else None)
        r4 = query_taifex_pc_ratio(d, session_taifex); (res.extend(r4) if r4 else None)
        
        # --- TWSE Queries ---
        r5 = query_twse_market_data(d, session_twse); (res.extend(r5) if r5 else None)
        r6 = query_twse_stock_day(session_twse, d); (res.extend(r6) if r6 else None)
        r7 = query_twse_foreign_buy(session_twse, d); (res.extend(r7) if r7 else None)

        return res

    results = fetch_all_with_fallback(date_str)
    
    # Check for missing critical codes and fallback if necessary
    expected_codes = {'F01', 'F02', 'F03', 'F04', 'F05', 'F07', 'F11', 'F12', 'F14', 'F15', 'F16', 'F17'}
    actual_codes = {item['f_code'] for item in results}
    
    if expected_codes - actual_codes:
        prev_date = get_previous_trading_day().strftime("%Y.%m.%d")
        print(f"當日 ({date_str}) 資料不完整 ({actual_codes})，嘗試補齊前一交易日: {prev_date}")
        results_prev = fetch_all_with_fallback(prev_date)
        
        existing_codes = {item['f_code'] for item in results}
        for item in results_prev:
            if item['f_code'] not in existing_codes:
                results.append(item)
    
    results.sort(key=lambda x: x['f_code'])
    return results
