import requests
import time

# 這是玩股網真正用來更新畫面上「跳動數字」的 API
# mids 分別代表：F25(台指期盤後), F23(EM-ND期), F21(NASDAQ)
API_URL = "https://www.wantgoo.com/investor/api/market-realtime?mids=F25,F23,F21"

def get_data():
    # 建立一個模擬度極高的標頭
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.wantgoo.com/global?c=0', # 加上精確的來源參數
        'Accept': 'application/json, text/plain, */*',
        'X-Requested-With': 'XMLHttpRequest' # 標註這是一個異步請求
    }
    
    try:
        # 在 Windows 上，我們先建一個 session
        session = requests.Session()
        # 先「路過」一下首頁，拿到基本門票
        session.get("https://www.wantgoo.com/global", headers=headers, timeout=10)
        
        # 正式請求 API
        response = session.get(API_URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ 抓取成功! 執行時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 50)
            
            for item in data:
                # 注意：market-realtime API 的欄位名稱與 getstockdata 不同
                name = item.get('name')          # 指標名稱
                price = item.get('dealPrice')    # 最新成交價
                change = item.get('changeValue') # 漲跌點數
                p_time = item.get('time')        # 資料更新時間 (例如 21:30)
                
                print(f"[{p_time}] {name:15} | 價格: {price:10} | 漲跌: {change}")
            print("-" * 50)
        else:
            print(f"❌ 抓取失敗，狀態碼: {response.status_code}")
            if response.status_code == 404:
                print("提示：玩股網 API 地址可能已變更，或對本機 IP 進行了限制。")
                
    except Exception as e:
        print(f"⚠️ 程式出錯: {e}")

if __name__ == "__main__":
    while True:
        get_data()
        print("等待 1 分鐘後更新...")
        time.sleep(60)