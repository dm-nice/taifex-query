import re
import time
from utils.date_utils import get_current_taiwan_date

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

def query_wantgoo_nighttime(date_str=None):
    """
    F21-F25: Wantgoo 全球市場數據 (美股及台指期盤後)
    使用 Playwright 反偵測技巧擷取頁面數據
    - F21: NASDAQ指數
    - F22: 費城半導體指數
    - F23: EM-ND期指數
    - F24: 台積電ADR
    - F25: 台指期盤後
    """
    if date_str is None:
        date_str = get_current_taiwan_date()

    if not PLAYWRIGHT_AVAILABLE:
        print("Playwright not available. Cannot fetch Wantgoo data.")
        return None

    # 指標對應表（搜尋文本 → F代碼, 名稱）
    indicator_map = {
        'NASDAQ': ('F21', 'NASDAQ指數'),
        '費城半導體': ('F22', '費城半導體指數'),
        'EM-ND': ('F23', 'EM-ND期指數'),
        'ADR': ('F24', '台積電ADR'),
        '台指期盤後': ('F25', '台指期盤後'),
    }

    results = []

    try:
        with sync_playwright() as p:
            # 使用反偵測設置
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )

            # 設置真實的 User-Agent
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            page = context.new_page()

            # 隱藏 webdriver 屬性
            page.add_init_script('''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false
                });
            ''')

            try:
                # 先訪問首頁建立 session
                page.goto('https://www.wantgoo.com/', wait_until='networkidle', timeout=30000)
                time.sleep(1)

                # 再訪問目標頁面
                page.goto('https://www.wantgoo.com/global', wait_until='networkidle', timeout=30000)

                # 等待 JavaScript 完全加載數據
                time.sleep(5)

                # 從頁面文本中提取數據
                page_text = page.evaluate('() => document.body.innerText')

                # 逐行解析文本尋找指標
                lines = page_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line or len(line) < 5:
                        continue

                    # 檢查是否包含我們的指標
                    for search_key, (f_code, display_name) in indicator_map.items():
                        if search_key in line and f_code not in {r['f_code'] for r in results}:
                            # 解析該行，尋找漲跌值
                            # 格式: "NASDAQ	23530.02	△58.27	0.25	04:59"
                            parts = line.split('\t')
                            if len(parts) >= 3:
                                change_text = parts[2].strip()
                                # 提取數值
                                match = re.search(r'([▲△▼▽\+\-])([0-9.]+)', change_text)
                                if match:
                                    sign_char = match.group(1)
                                    value_num = match.group(2)

                                    # 標準化符號
                                    if sign_char in ('▲', '△', '+'):
                                        change_value = f"+{value_num}"
                                    else:
                                        change_value = f"-{value_num}"

                                    results.append({
                                        'f_code': f_code,
                                        'name': display_name,
                                        'field': '漲跌幅',
                                        'value': change_value,
                                        'unit': ''
                                    })

            finally:
                context.close()
                browser.close()

        return results if results else None

    except Exception as e:
        print(f"Wantgoo Nighttime Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def query_nighttime_data(date_str=None):
    """
    查詢夜盤數據 (F21-F25)
    """
    results = []

    # Get Wantgoo Nighttime Data (F21-F25)
    r1 = query_wantgoo_nighttime(date_str)
    if r1:
        results.extend(r1)

    # Sort by F-code
    results.sort(key=lambda x: x['f_code'])
    return results
