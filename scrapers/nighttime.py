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
    使用 Playwright JavaScript 評估擷取頁面數據
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
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                # 導航到頁面
                page.goto('https://www.wantgoo.com/global', wait_until='networkidle', timeout=30000)

                # 等待 JavaScript 加載表格數據
                time.sleep(2)

                # 使用 JavaScript 從表格中提取數據
                table_data = page.evaluate('''() => {
                    const results = [];
                    const tables = document.querySelectorAll('table.global-tb');
                    tables.forEach(table => {
                        table.querySelectorAll('tr').forEach(row => {
                            const cells = row.querySelectorAll('td');
                            if (cells.length >= 3) {
                                const name = cells[0]?.innerText?.trim() || '';
                                const change = cells[2]?.innerText?.trim() || '';
                                if (name && change) {
                                    results.push({name: name, change: change});
                                }
                            }
                        });
                    });
                    return results;
                }''')

                # 處理結果並去重
                seen_f_codes = set()
                for row_data in table_data:
                    name = row_data.get('name', '')
                    change_text = row_data.get('change', '')

                    # 對比每個指標
                    for search_key, (f_code, display_name) in indicator_map.items():
                        if search_key in name and f_code not in seen_f_codes:
                            # 提取數值：從 "▲123.45" 或 "▼123.45" 中提取
                            # change_text 格式: "▲58.27" 或 "▼45.89"
                            match = re.search(r'([▲▼\+\-])([0-9.]+)', change_text)
                            if match:
                                sign_char = match.group(1)
                                value_num = match.group(2)

                                # 標準化符號
                                if sign_char in ('▲', '+'):
                                    change_value = f"+{value_num}"
                                else:  # ▼ or -
                                    change_value = f"-{value_num}"

                                results.append({
                                    'f_code': f_code,
                                    'name': display_name,
                                    'field': '漲跌幅',
                                    'value': change_value,
                                    'unit': ''
                                })
                                seen_f_codes.add(f_code)  # 標記已處理
                            break  # 找到匹配就跳出

            finally:
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
