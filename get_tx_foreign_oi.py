# get_tx_foreign_oi.py
import requests
from bs4 import BeautifulSoup
from typing import Optional
from datetime import datetime, timedelta

def _to_query_date(date_str: str) -> str:
    """
    將 YYYYMMDD 格式的日期字串轉換為 YYYY/MM/DD
    """
    try:
        dt = datetime.strptime(date_str, "%Y%m%d")
        return dt.strftime("%Y/%m/%d")
    except ValueError:
        print(f"錯誤：日期格式不正確 '{date_str}'，應為 YYYYMMDD。")
        return None

def get_tx_foreign_oi(date_str: str) -> Optional[int]:
    """
    從期交所網站抓取指定日期的「台指期貨」外資未平倉淨口數 (OI)。

    Args:
        date_str (str): 查詢日期，格式為 YYYYMMDD。

    Returns:
        Optional[int]: 外資淨口數。如果找不到或發生錯誤，則返回 None。
    """
    query_date = _to_query_date(date_str)
    if not query_date:
        return None

    # 目標網址：依契約類別區分的交易資訊
    url = "https://www.taifex.com.tw/cht/3/futContractsDate"
    params = {"queryDate": query_date}
    
    print(f"正在查詢日期 {query_date} 的台指期貨外資淨口數...")

    try:
        # 使用 headers 模擬瀏覽器行為
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()  # 如果 HTTP 狀態碼不是 200，則引發錯誤
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 找到資料表格 (通常是 class="table_f" 的第三個)
        # 為了增加穩健性，我們遍歷所有可能是目標的表格
        tables = soup.find_all("table", class_="table_f")
        if not tables:
            print("錯誤：在頁面上找不到 class='table_f' 的資料表。")
            return None

        target_table = None
        for table in tables:
            # 判斷是否為目標表格 (表頭應包含 "未平倉餘額")
            if "未平倉餘額" in table.get_text():
                target_table = table
                break
        
        if not target_table:
            print("錯誤：找不到包含「未平倉餘額」的目標表格。")
            return None

        # 遍歷表格的每一行
        rows = target_table.find_all("tr")
        for tr in rows:
            # 取得該行的所有欄位 (td)
            cols = [td.get_text(strip=True) for td in tr.find_all("td")]
            
            # 欄位結構應為：
            # [0]契約, [1]身份別, [2]多方交易口數, [3]空方交易口數, [4]多空交易淨額,
            # [5]多方未平倉口數, [6]空方未平倉口數, [7]多空未平倉淨額
            if len(cols) < 8:
                continue

            contract = cols[0]
            identity = cols[1]

            # 檢查是否為「臺股期貨」且身份為「外資」
            if contract == "臺股期貨" and "外資" in identity:
                net_oi_str = cols[7].replace(",", "")
                try:
                    net_oi = int(net_oi_str)
                    print(f"成功找到資料！")
                    return net_oi
                except (ValueError, IndexError):
                    print(f"錯誤：無法將淨口數 '{net_oi_str}' 轉換為數字。")
                    return None

        print(f"資訊：在 {date_str} 的資料中找不到「臺股期貨」的外資數據。")
        return None

    except requests.exceptions.RequestException as e:
        print(f"錯誤：網路請求失敗 - {e}")
        return None
    except Exception as e:
        print(f"錯誤：處理過程中發生未知錯誤 - {e}")
        return None

def main():
    """
    主執行函式
    """
    # --- 設定查詢日期 ---
    # 預設查詢前一個交易日 (避免當日資料尚未更新)
    # 如果今天是週一，則查詢上週五
    today = datetime.now()
    offset = 1
    if today.weekday() == 0: # 週一
        offset = 3
    elif today.weekday() == 6: # 週日
        offset = 2
    
    target_date = (today - timedelta(days=offset)).strftime("%Y%m%d")
    
    # 你也可以手動指定日期
    # target_date = "20251127"

    print("=" * 50)
    net_oi = get_tx_foreign_oi(target_date)
    print("=" * 50)

    if net_oi is not None:
        print(f"📅 日期: {target_date}")
        print(f"📊 台指期貨外資淨未平倉口數 (OI): {net_oi:+,}")
    else:
        print(f"❌ 在 {target_date} 未能查詢到有效數據。")
        print("   可能原因：非交易日、網站結構變更或網路問題。")

if __name__ == "__main__":
    main()
