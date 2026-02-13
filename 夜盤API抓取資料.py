"""
夜盤 API 抓取資料 (F21-F25)
使用 Wantgoo REST API 直接抓取，無需 Playwright 瀏覽器

API 端點:
  - global/all-quote-info: 國際股市 (NASDAQ, 費城半導體, 台積電ADR)
  - investrue/all-quote-info: 台灣期貨 (台指期盤後, EM-ND期)

優點: 執行速度快 (~1秒)，無需安裝瀏覽器
"""

import os
import requests
from utils.helpers import save_to_markdown
from utils.date_utils import get_current_taiwan_date

# Wantgoo API 設定
WANTGOO_GLOBAL_API = 'https://www.wantgoo.com/global/all-quote-info'
WANTGOO_INVESTRUE_API = 'https://www.wantgoo.com/investrue/all-quote-info'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Referer': 'https://www.wantgoo.com/global',
}

# 指標對應表: API ID -> (F代碼, 顯示名稱, API來源)
# API來源: 'global' 或 'investrue'
INDICATOR_MAP = {
    'NAS': ('F21', 'NASDAQ指數', 'global'),
    'SOX': ('F22', '費城半導體指數', 'global'),
    'M1NQ&': ('F23', 'EM-ND期指數', 'global'),
    'TSM': ('F24', '台積電ADR', 'global'),
    'WTXP&': ('F25', '台指期盤後', 'investrue'),
}


def fetch_api_data(url):
    """
    呼叫指定的 Wantgoo API
    回傳: List[Dict] 或 None
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API 請求失敗 ({url}): {e}")
        return None
    except ValueError as e:
        print(f"JSON 解析失敗: {e}")
        return None


def query_wantgoo_apis():
    """
    呼叫兩個 Wantgoo API 並合併資料
    回傳: Dict[api_id -> item] 或空字典
    """
    combined_data = {}

    # 抓取 global API (NASDAQ, 費城半導體, 台積電ADR, EM-ND)
    print(f"  呼叫 global API...")
    global_data = fetch_api_data(WANTGOO_GLOBAL_API)
    if global_data:
        print(f"    取得 {len(global_data)} 筆")
        for item in global_data:
            combined_data[item.get('id')] = item

    # 抓取 investrue API (台指期盤後)
    print(f"  呼叫 investrue API...")
    investrue_data = fetch_api_data(WANTGOO_INVESTRUE_API)
    if investrue_data:
        print(f"    取得 {len(investrue_data)} 筆")
        for item in investrue_data:
            item_id = item.get('id')
            # 只加入需要的指標，避免覆蓋
            if item_id in ['WTXP&']:
                combined_data[item_id] = item

    return combined_data


def parse_nighttime_data(id_map):
    """
    從 API 回應中解析夜盤指標 (F21-F25)

    id_map: Dict[api_id -> item]
    回傳: List[Dict] 格式符合 save_to_markdown 需求
    """
    if not id_map:
        return []

    results = []

    for api_id, (f_code, display_name, api_source) in INDICATOR_MAP.items():
        if api_id not in id_map:
            # 找不到該指標
            results.append({
                'f_code': f_code,
                'name': display_name,
                'value': '查詢失敗',
                'unit': ''
            })
            continue

        item = id_map[api_id]
        close_price = item.get('close', 0)
        prev_close = item.get('previousClose', 0)

        # 計算漲跌
        change = close_price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0

        # 格式化符號
        sign = '+' if change >= 0 else ''
        change_str = f"{sign}{change:.2f}"
        pct_str = f"{sign}{change_pct:.2f}%"

        results.append({
            'f_code': f_code,
            'name': display_name,
            'field': '',
            'price': str(close_price),
            'change': change_str,
            'percent': pct_str,
            'value': f"{close_price} [{change_str} , {pct_str}]",
            'unit': ''
        })

    # 依 F 代碼排序
    results.sort(key=lambda x: x['f_code'])
    return results


def query_nighttime_data():
    """
    查詢夜盤數據 (F21-F25) - 主入口函式
    回傳: List[Dict] 或空列表
    """
    print("正在呼叫 Wantgoo API...")
    id_map = query_wantgoo_apis()

    if not id_map:
        print("API 回應為空")
        return []

    results = parse_nighttime_data(id_map)
    return results


def main():
    # 確保 output 目錄存在
    os.makedirs("output", exist_ok=True)

    date_str = get_current_taiwan_date()
    print(f"夜盤 API 抓取資料... ({date_str})")
    print(f"API 端點:")
    print(f"  - {WANTGOO_GLOBAL_API}")
    print(f"  - {WANTGOO_INVESTRUE_API}")
    print("-" * 50)

    data = query_nighttime_data()

    if data:
        print("\n抓取結果:")
        for item in data:
            print(f"  {item['f_code']} {item['name']}: {item['value']}")

        # 存檔 (使用 taifex_night_ 前綴)
        filepath = save_to_markdown(data, filename_prefix="taifex_night_")

        if filepath:
            print(f"\n檔案已儲存: {filepath}")
        else:
            print("\n儲存檔案失敗")
    else:
        print("\n抓取失敗或無資料")


if __name__ == "__main__":
    main()
