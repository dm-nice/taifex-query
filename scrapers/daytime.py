import requests
from bs4 import BeautifulSoup
from utils.date_utils import get_current_taiwan_date, get_previous_trading_day

def query_taifex_foreign_holdings(date_str=None):
    """F01-F03: 台指期貨外資持倉"""
    if date_str is None:
        date_str = get_current_taiwan_date()
    query_date = date_str.replace('.', '/')
    url = "https://www.taifex.com.tw/cht/3/totalTableDate"
    payload = {"queryDate": query_date, "queryType": "", "goDay": "", "doQuery": "", "dateaddcnt": ""}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.taifex.com.tw/cht/3/totalTableDate",
        "Origin": "https://www.taifex.com.tw"
    }
    try:
        session = requests.Session()
        session.get(url, headers=headers, timeout=10)
        response = session.post(url, data=payload, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        target_table = None
        for t in soup.find_all('table', class_='table_f'):
            if "未平倉" in t.get_text():
                target_table = t
        if not target_table: return None
        rows = target_table.find_all('tr')
        foreign_row = None
        for row in rows:
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

def query_taifex_settlement(date_str=None):
    """F04: 臺指期貨收盤價"""
    if date_str is None:
        date_str = get_current_taiwan_date()
    query_date = date_str.replace('.', '/')
    url = "https://www.taifex.com.tw/cht/3/futDailyMarketReport"
    payload = {"queryType": "2", "marketCode": "0", "commodity_id": "TX", "queryDate": query_date}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='table_f')
        if not table: return None
        for row in table.find_all('tr'):
            tds = row.find_all('td')
            if len(tds) > 5 and "TX" in tds[0].get_text(strip=True):
                price = tds[5].get_text(strip=True)
                if price != "-":
                    return [{"f_code": "F04", "name": "台指期貨-當日收盤", "field": "最後成交價", "value": price, "unit": ""}]
        return None
    except Exception as e:
        print(f"F04 Error: {e}"); return None

def query_taifex_options_volume(date_str=None):
    """F05: 臺指選擇權總成交量 (純日盤)"""
    if date_str is None:
        date_str = get_current_taiwan_date()
    query_date = date_str.replace('.', '/')
    url = "https://www.taifex.com.tw/cht/3/optDailyMarketReport"
    payload = {"queryType": "2", "marketCode": "0", "commodity_id": "TXO", "queryDate": query_date}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='table_f')
        if not table: return None
        for row in reversed(table.find_all('tr')):
            if "小計" in row.get_text():
                cols = row.find_all('td')
                # 遍歷格子，找第一個純數字的（排除商品代號和 "-"）
                for td in cols:
                    text = td.get_text(strip=True).replace(',', '')
                    if text.isdigit():
                        return [{"f_code": "F05", "name": "台指選擇權-當日", "field": "選擇權總成交量", "value": text, "unit": ""}]
        return None
    except Exception as e:
        print(f"F05 Error: {e}"); return None

def query_taifex_pc_ratio(date_str=None):
    """F07: 臺指選擇權 Put/Call Ratio"""
    if date_str is None:
        date_str = get_current_taiwan_date()
    
    # 格式化日期：pcRatio 表格中使用 YYYY/M/D 或 YYYY/MM/DD
    # 例如 2026/1/15
    d_parts = date_str.split('.')
    query_date_short = f"{d_parts[0]}/{int(d_parts[1])}/{int(d_parts[2])}"
    
    url = f"https://www.taifex.com.tw/cht/3/pcRatio?queryDate={date_str.replace('.','/')}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='table_f')
        if not table: return None
        for row in table.find_all('tr'):
            row_text = row.get_text()
            # 必須精確匹配日期
            if query_date_short in row_text:
                cols = row.find_all('td')
                if len(cols) >= 7:
                    return [{"f_code": "F07", "name": "臺指選擇權Put/Call", "field": "買賣權未平倉量比率%", "value": cols[6].get_text(strip=True), "unit": ""}]
        return None
    except Exception as e:
        print(f"F07 Error: {e}"); return None

def query_twse_market_data(date_str=None):
    """
    爬取 F11: 加權股價指數(收盤) 與 F12: 大盤成交金額
    """
    import time, random
    if date_str is None:
        date_str = get_current_taiwan_date()
    
    query_date = date_str.replace('.', '')
    base_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
    }
    
    results = []
    session = requests.Session()
    
    try:
        # 先訪問首頁獲取環境基礎
        session.get("https://www.twse.com.tw/zh/index.html", headers=base_headers, timeout=10)
        time.sleep(random.uniform(0.5, 1.0))
        
        # 1. 抓取 F11 (MI_5MINS_HIST) - 指數歷史
        f11_url = f"https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST?response=json&date={query_date}"
        f11_headers = base_headers.copy()
        f11_headers["Referer"] = "https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html"
        
        f11_resp = session.get(f11_url, headers=f11_headers, timeout=15).json()
        if f11_resp.get('stat') == 'OK' and 'data' in f11_resp:
            y, m, d = date_str.split('.')
            minguo_date = f"{int(y)-1911}/{m}/{d}"
            for row in f11_resp['data']:
                if minguo_date in row[0]:
                    results.append({"f_code": "F11", "name": "加權股價", "field": "指數收盤", "value": row[4].replace(',', ''), "unit": ""})
                    break

        time.sleep(random.uniform(0.5, 1.0))

        # 2. 抓取 F12 (MI_INDEX Type: MS) - 大盤統計
        f12_url = f"https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?response=json&date={query_date}&type=MS"
        f12_headers = base_headers.copy()
        f12_headers["Referer"] = "https://www.twse.com.tw/zh/trading/historical/mi-index.html"
        
        f12_resp = session.get(f12_url, headers=f12_headers, timeout=15).json()
        if f12_resp.get('stat') == 'OK' and 'tables' in f12_resp:
            for table in f12_resp['tables']:
                if "大盤統計資訊" in table.get('title', ''):
                    for row in table.get('data', []):
                        if "總計(1~15)" in row[0]:
                            results.append({"f_code": "F12", "name": "大盤統計資訊", "field": "總計成交金額", "value": row[1].replace(',', ''), "unit": ""})
                            break
                    break

        return results if results else None
    except Exception as e:
        print(f"F11/F12 Error: {e}")
        return None

def query_twse_stock_day(session, date_str, stock_no="2330"):
    """
    爬取 F14-F16: 個股日成交資訊 (預設台積電)
    """
    import time, random
    time.sleep(random.uniform(0.5, 1.0))
    
    query_date = date_str.replace('.', '')
    # 民國年月日轉換 (用於匹配)
    y, m, d = date_str.split('.')
    minguo_date = f"{int(y)-1911}/{m}/{d}"
    
    url = f"https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY?date={query_date}&stockNo={stock_no}&response=json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.twse.com.tw/zh/trading/historical/stock-day.html",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        resp = session.get(url, headers=headers, timeout=15).json()
        if resp.get('stat') == 'OK' and 'data' in resp:
            for row in resp['data']:
                if row[0] == minguo_date:
                    # [日期, 成交股數, 成交金額, 開盤, 最高, 最低, 收盤, 漲跌價差, 成交筆數]
                    # F14: 收盤價 (row[6])
                    # F15: 漲跌價差 (row[7]) 注意網頁有時會有 HTML tag (+-), 但 JSON 通常是純文字
                    # F16: 成交張數 (row[1] 是股數，要除以 1000)
                    close = row[6].replace(',', '')
                    change = row[7].replace(',', '').replace('+', '').replace('X', '') # X代表除權息
                    # 處理漲跌符號：如果是紅色(漲)在 JSON 裡可能只是正數，綠色(跌)是負數，若有特殊符號需清洗
                    # TWSE JSON 通常漲跌是: "+1.00", "-1.00", "0.00"
                    
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

def query_twse_foreign_buy(session, date_str):
    """
    爬取 F17: 外資及陸資買賣超
    API: BFI82U
    """
    import time, random
    time.sleep(random.uniform(0.5, 1.0))
    
    query_date = date_str.replace('.', '')
    url = f"https://www.twse.com.tw/rwd/zh/fund/BFI82U?date={query_date}&response=json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.twse.com.tw/zh/fund/BFI82U.html",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        resp = session.get(url, headers=headers, timeout=15).json()
        if resp.get('stat') == 'OK' and 'data' in resp:
            # 尋找 "外資及陸資(不含外資自營商)"
            for row in resp['data']:
                if "外資及陸資" in row[0]: # 包含即可
                    # [單位, 買進金額, 賣出金額, 買賣差額]
                    net_buy = row[3].replace(',', '')
                    return [{"f_code": "F17", "name": "台灣股票外資及陸資", "field": "買賣差額", "value": net_buy, "unit": ""}]
        return None
    except Exception as e:
        print(f"F17 Error: {e}")
        return None

def calculate_f13_ma20(session, date_str, current_close):
    """
    計算 F13: 20日均線距離
    邏輯：抓取最近一個月的 MI_5MINS_HIST，如果不足 20 筆，抓上個月補齊
    """
    if not current_close:
        return None
        
    try:
        # 當前日期
        y, m, d = map(int, date_str.split('.'))
        
        # 取得本月數據
        # 注意：MI_5MINS_HIST 給的是該月的完整日線
        # 我們已經在 query_twse_market_data 做過一次了，但為了獨立性這裡可能重做，
        # 或者是優化架構傳遞 data。但為了簡單，這裡重新請求，有 cache 更好。
        # 為了避嫌，我們這裡假設調用頻率不高。
        
        # 獲取本月
        def get_month_data(year, month):
            import time, random
            time.sleep(random.uniform(0.5, 1.0))
            q_date = f"{year}{month:02d}01"
            url = f"https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST?response=json&date={q_date}"
            h = {
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", 
               "Referer": "https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html",
               "X-Requested-With": "XMLHttpRequest"
            }
            res = session.get(url, headers=h, timeout=15).json()
            closes = []
            if res.get('stat') == 'OK':
                for row in res['data']:
                    # row[0] 是日期 (115/01/15), row[4] 是收盤價
                    # 我們只需要數值
                    val = float(row[4].replace(',', ''))
                    closes.append(val)
                return closes # 按日期升序排列
            return []

        # 獲取本月數據
        this_month_closes = get_month_data(y, m)
        
        # 找到當日在本月數據中的位置
        # 因為 this_month_closes 包含整個月（包含未來幾天如果有的話？不，歷史數據只會有到今天）
        # 但如果是補抓舊資料，this_month_closes 可能包含目標日之後的日子，所以要截斷
        # 不過簡單做法：我們只需要取「包含目標日」在內的最後 N 筆
        
        # 這裡有個小問題：我們需要準確知道哪一筆是 date_str
        # 重新實作一個帶日期的版本比較穩
        def get_month_data_map(year, month):
             # 同上，但回傳 dict { '115/01/15': 30810.58 }
            import time, random
            time.sleep(random.uniform(0.5, 1.0))
            q_date = f"{year}{month:02d}01"
            url = f"https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST?response=json&date={q_date}"
            h = { "User-Agent": "...", "X-Requested-With": "XMLHttpRequest" } # 簡化寫
            # 實際使用傳入的 session
            return [] # 佔位，下面用邏輯整合
            
        # 簡單策略：抓取本月 + 上個月的所有收盤價，串接起來
        # 然後找到 target_date 的 index，往前取 19 筆 + 自己 = 20 筆
        
        history_closes = []
        
        # 上個月
        last_m = m - 1
        last_y = y
        if last_m < 1:
            last_m = 12
            last_y -= 1
        
        history_closes.extend(get_month_data(last_y, last_m))
        history_closes.extend(get_month_data(y, m))
        
        # 目標收盤價 (float)
        target_price = float(current_close.replace(',', ''))
        
        # 在 history_closes 中找到 target_price (且是最後一次出現，假設不會重複太頻繁，或是比較日期)
        # 為了精確，我們其實應該用日期匹配。
        # 但既然我們有了 current_close (F11)，我們可以直接倒推。
        
        # 修正策略：只用純數值陣列可能會有重複值風險。
        # 我們相信 get_month_data 回傳的是按日期排序的。
        # 所以當天收盤價應該在 history_closes 的末端附近。
        
        # 找到 index
        try:
             # 從後面找，匹配 F11 的值
             idx = -1
             found = False
             # 允許微小誤差或字串轉換差異，先精確比對
             for i in range(len(history_closes) - 1, -1, -1):
                 if abs(history_closes[i] - target_price) < 0.01:
                     idx = i
                     found = True
                     break
             
             if found and idx >= 19:
                 ma20_slice = history_closes[idx-19 : idx+1]
                 ma20 = sum(ma20_slice) / 20
                 # F13: 均線距離 = 收盤 - MA20
                 dist = target_price - ma20
                 return [{"f_code": "F13", "name": "台灣加權股價指數 20日均線", "field": "均線距離", "value": f"{dist:.2f}", "unit": ""}]
             
        except Exception as e:
            print(f"MA20 Calc Error: {e}")
            return None
            
        return None

    except Exception as e:
        print(f"F13 Error: {e}")
        return None

def query_daytime_data(date_str=None):
    if date_str is None:
        date_str = get_current_taiwan_date()
        
    def fetch_all(d):
        res = []
        # TWSE 需要共用 session 以維持 cookies
        import requests
        session_twse = requests.Session()
        # 預熱
        try:
            session_twse.get("https://www.twse.com.tw/zh/index.html", 
                headers={"User-Agent": "Mozilla/5.0 ..."}, timeout=5)
        except: pass
        
        r1 = query_taifex_foreign_holdings(d); (res.extend(r1) if r1 else None)
        r2 = query_taifex_settlement(d); (res.extend(r2) if r2 else None)
        r3 = query_taifex_options_volume(d); (res.extend(r3) if r3 else None)
        r4 = query_taifex_pc_ratio(d); (res.extend(r4) if r4 else None)
        
        # TWSE 群組
        # F11, F12 舊函式需要微調接收 session 參數嗎？
        # 為了兼容性，先保留舊的 query_twse_market_data 獨立運作(它自己建 session)
        # 但新的 F14-F17 我們傳入 session_twse 比較好
        
        # 為避免混亂，這裡 F11/F12 繼續用舊的，F14-F17 用新的 shared session
        r5 = query_twse_market_data(d); (res.extend(r5) if r5 else None)
        
        # 抓取台積電與外資
        r6 = query_twse_stock_day(session_twse, d); (res.extend(r6) if r6 else None)
        r7 = query_twse_foreign_buy(session_twse, d); (res.extend(r7) if r7 else None)
        
        # 計算 F13 (依賴 F11)
        # 先找出 F11 的值
        f11_val = next((item['value'] for item in res if item['f_code'] == 'F11'), None)
        if f11_val:
            r8 = calculate_f13_ma20(session_twse, d, f11_val); (res.extend(r8) if r8 else None)
            
        return res

    results = fetch_all(date_str)
    
    # 預期包含的 F 碼
    expected_codes = {'F01', 'F02', 'F03', 'F04', 'F05', 'F07', 'F11', 'F12', 'F13', 'F14', 'F15', 'F16', 'F17'}
    actual_codes = {item['f_code'] for item in results}
    
    # 只要有缺失就回溯補齊
    if expected_codes - actual_codes:
        prev_date = get_previous_trading_day().strftime("%Y.%m.%d")
        print(f"當日 ({date_str}) 資料不完整 ({actual_codes})，嘗試補齊前一交易日: {prev_date}")
        results_prev = fetch_all(prev_date)
        
        existing_codes = {item['f_code'] for item in results}
        for item in results_prev:
            if item['f_code'] not in existing_codes:
                results.append(item)
    
    results.sort(key=lambda x: x['f_code'])
    return results
