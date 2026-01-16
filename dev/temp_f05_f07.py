import requests
from bs4 import BeautifulSoup
from utils.date_utils import get_current_taiwan_date, get_previous_trading_day

def query_taifex_options_volume(date_str=None):
    """
    爬取 F05: 臺指選擇權總成交量 (純日盤)
    URL: https://www.taifex.com.tw/cht/3/optDailyMarketReport
    """
    if date_str is None:
        date_str = get_current_taiwan_date()
    
    query_date = date_str.replace('.', '/')
    url = "https://www.taifex.com.tw/cht/3/optDailyMarketReport"
    
    # 參數設定：一般交易時段 (MarketCode=0), 臺指選擇權 (commodity_id=TXO)
    payload = {
        "queryType": "2",
        "marketCode": "0",
        "commodity_id": "TXO",
        "queryDate": query_date,
        "MarketCode": "0",
        "commodity_idd": "TXO"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', class_='table_f')
        if not table:
            return None
            
        rows = table.find_all('tr')
        # 尋找包含「小計」的最後一行
        # 在 TXO 頁面，「小計」行會統計該產品的成交量
        target_row = None
        for row in reversed(rows):
            if "小計" in row.get_text():
                target_row = row
                break
        
        if not target_row:
            return None
            
        cols = target_row.find_all('td')
        # 根據 Chrome DevTools 偵查：
        # 日盤成交量通常在 Index 13 (如果「小計」是在 td[0])
        # 我們來確認一下數據格式
        # 結構: [小計, ..., 成交量-一般, 成交量-盤後, 成交量-合計]
        # 在最後幾欄：倒數第 3 欄通常是「一般交易時段成交量」
        if len(cols) >= 14:
            volume = cols[-3].get_text(strip=True).replace(',', '')
            return [
                {"f_code": "F05", "name": "台指選擇權-當日", "field": "選擇權總成交量", "value": volume, "unit": ""}
            ]
        return None
        
    except Exception as e:
        print(f"F05 Error on {date_str}: {e}")
        return None

def query_taifex_pc_ratio(date_str=None):
    """
    爬取 F07: 臺指選擇權 Put/Call Ratio
    URL: https://www.taifex.com.tw/cht/3/pcRatio
    """
    if date_str is None:
        date_str = get_current_taiwan_date()
    
    query_date = date_str.replace('.', '/')
    url = f"https://www.taifex.com.tw/cht/3/pcRatio?queryDate={query_date}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', class_='table_f')
        if not table:
            return None
            
        # 這裡會有多行日期，找匹配的那一行
        rows = table.find_all('tr')
        target_row = None
        for row in rows:
            if query_date in row.get_text():
                target_row = row
                break
        
        if not target_row:
            return None
            
        cols = target_row.find_all('td')
        # 結構: 日期, 賣權未平倉, 買權未平倉, PC Ratio
        pc_ratio = cols[6].get_text(strip=True) # 第 7 欄是比例
        
        return [
            {"f_code": "F07", "name": "臺指選擇權Put/Call", "field": "買賣權未平倉量比率%", "value": pc_ratio, "unit": ""}
        ]
        
    except Exception as e:
        print(f"F07 Error on {date_str}: {e}")
        return None

# 原有的 F01-F03, F04 ... (略，下面會整合)
