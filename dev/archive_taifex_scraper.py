import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import csv
import os
from pynput import keyboard
import webbrowser

def scrape_taifex_data(date_str=None):
    """
    抓取台灣期貨交易所三大法人交易資訊

    Parameters:
    -----------
    date_str : str, optional
        日期，格式為 'YYYY/MM/DD'，若不指定則使用今日日期

    Returns:
    --------
    dict : 包含交易資訊的字典
    """

    # 如果沒有指定日期，使用今日日期
    if date_str is None:
        date_str = datetime.now().strftime('%Y/%m/%d')

    # 目標URL
    url = 'https://www.taifex.com.tw/cht/3/totalTableDate'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # 發送請求
    params = {'date': date_str}
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'

    if response.status_code != 200:
        raise Exception(f"請求失敗，狀態碼: {response.status_code}")

    # 解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取資料
    data = {
        'date': date_str,
        'trading_volume': {},      # 交易口數與契約金額
        'open_interest': {}         # 未平倉口數與契約金額
    }

    # 查找所有表格
    tables = soup.find_all('table')

    if len(tables) >= 2:
        # 第二個表格通常是未平倉數據
        open_interest_table = tables[1]

        # 解析未平倉表格
        rows = open_interest_table.find_all('tr')

        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) > 0:
                # 尋找外資行
                row_text = [cell.get_text(strip=True) for cell in cells]

                if any('外資' in text for text in row_text):
                    # 找到外資行
                    # 結構: 身份別 | 口數 | 契約金額 | 口數 | 契約金額 | 口數 | 契約金額
                    #        外資  | 多方口數 | 多方金額 | 空方口數 | 空方金額 | 淨額口數 | 淨額金額

                    data['open_interest']['foreign_investors'] = {
                        'long_position': {
                            'contracts': row_text[1] if len(row_text) > 1 else None,
                            'amount': row_text[2] if len(row_text) > 2 else None
                        },
                        'short_position': {
                            'contracts': row_text[3] if len(row_text) > 3 else None,
                            'amount': row_text[4] if len(row_text) > 4 else None
                        },
                        'net_position': {
                            'contracts': row_text[5] if len(row_text) > 5 else None,
                            'amount': row_text[6] if len(row_text) > 6 else None
                        }
                    }

    return data


def is_trading_day(date_obj):
    """
    判斷是否為交易日（排除周末）

    Parameters:
    -----------
    date_obj : datetime.date
        要檢查的日期

    Returns:
    --------
    bool : True為交易日，False為非交易日
    """
    # 0=Monday, 1=Tuesday, ..., 5=Saturday, 6=Sunday
    return date_obj.weekday() < 5


def get_previous_trading_day(date_str):
    """
    取得前一個交易日

    Parameters:
    -----------
    date_str : str
        日期，格式為 'YYYY/MM/DD'

    Returns:
    --------
    str : 前一個交易日的日期字符串
    """
    date_obj = datetime.strptime(date_str, '%Y/%m/%d').date()

    # 向前查詢，直到找到交易日
    for i in range(1, 10):  # 最多向前查詢10天（避免無限循環）
        prev_date = date_obj - timedelta(days=i)
        if is_trading_day(prev_date):
            return prev_date.strftime('%Y/%m/%d')

    return date_str


def check_data_exists(date_str):
    """
    檢查特定日期是否有資料

    Parameters:
    -----------
    date_str : str
        日期，格式為 'YYYY/MM/DD'

    Returns:
    --------
    bool : True表示有資料，False表示無資料
    """
    url = 'https://www.taifex.com.tw/cht/3/totalTableDate'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            return False

        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')

        if len(tables) < 2:
            return False

        # 查找表格中是否有數據
        open_interest_table = tables[1]
        rows = open_interest_table.find_all('tr')

        # 至少需要有表頭 + 3行數據（自營商、投信、外資）
        return len(rows) > 4

    except Exception as e:
        print(f"[ERROR] 檢查資料失敗: {e}")
        return False


def scrape_taifex_data_advanced(date_str=None, auto_fallback=True):
    """
    進階版本：更準確地解析表格數據

    Parameters:
    -----------
    date_str : str, optional
        日期，格式為 'YYYY/MM/DD'，若不指定則使用今日日期
    auto_fallback : bool, optional
        當日無資料時是否自動查詢前一交易日，預設為True
    """

    if date_str is None:
        date_str = datetime.now().strftime('%Y/%m/%d')

    # 如果啟用自動回退，當日無資料時查詢前一交易日
    if auto_fallback:
        if not check_data_exists(date_str):
            print(f"[INFO] {date_str} 無資料，查詢前一交易日...")
            date_str = get_previous_trading_day(date_str)
            print(f"[INFO] 轉查 {date_str} 的資料")

    url = 'https://www.taifex.com.tw/cht/3/totalTableDate'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'

    if response.status_code != 200:
        raise Exception(f"請求失敗，狀態碼: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # 初始化結果字典
    result = {
        'date': date_str,
        'data': {
            'proprietary_traders': {},
            'investment_trust': {},
            'foreign_investors': {}
        }
    }

    # 查找所有表格
    tables = soup.find_all('table')

    if len(tables) >= 2:
        # 解析未平倉表（通常是第二個表格）
        open_interest_table = tables[1]
        rows = open_interest_table.find_all('tr')

        # 從表頭開始解析
        for i, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue

            row_data = [cell.get_text(strip=True) for cell in cells]

            # 解析自營商、投信、外資三行
            if '自營商' in row_data[0]:
                result['data']['proprietary_traders'] = parse_trader_row(row_data)
            elif '投信' in row_data[0]:
                result['data']['investment_trust'] = parse_trader_row(row_data)
            elif '外資' in row_data[0]:
                result['data']['foreign_investors'] = parse_trader_row(row_data)

    return result


def parse_trader_row(row_data):
    """
    解析交易人行數據

    row_data 結構: [身份別, 多方口數, 多方金額, 空方口數, 空方金額, 淨額口數, 淨額金額]
    """

    def clean_number(text):
        """清理文本，轉換為數字或返回原文本"""
        if not text:
            return None
        try:
            text = text.replace(',', '')
            if text.lstrip('-').isdigit():
                return int(text)
            else:
                return float(text)
        except:
            return text

    return {
        'long_position': {
            'contracts': clean_number(row_data[1]) if len(row_data) > 1 else None,
            'amount': clean_number(row_data[2]) if len(row_data) > 2 else None
        },
        'short_position': {
            'contracts': clean_number(row_data[3]) if len(row_data) > 3 else None,
            'amount': clean_number(row_data[4]) if len(row_data) > 4 else None
        },
        'net_position': {
            'contracts': clean_number(row_data[5]) if len(row_data) > 5 else None,
            'amount': clean_number(row_data[6]) if len(row_data) > 6 else None
        }
    }


def print_foreign_investors_data(data):
    """
    打印外資未平倉數據
    """

    foreign = data['data']['foreign_investors']

    print(f"\n{'='*60}")
    print(f"台指期貨 - 外資未平倉資訊")
    print(f"日期: {data['date']}")
    print(f"{'='*60}")

    print(f"\n多方持倉:")
    print(f"  口數: {foreign['long_position']['contracts']:,}" if isinstance(foreign['long_position']['contracts'], int) else f"  口數: {foreign['long_position']['contracts']}")
    print(f"  契約金額: {foreign['long_position']['amount']:,.0f} 百萬元" if isinstance(foreign['long_position']['amount'], (int, float)) else f"  契約金額: {foreign['long_position']['amount']}")

    print(f"\n空方持倉:")
    print(f"  口數: {foreign['short_position']['contracts']:,}" if isinstance(foreign['short_position']['contracts'], int) else f"  口數: {foreign['short_position']['contracts']}")
    print(f"  契約金額: {foreign['short_position']['amount']:,.0f} 百萬元" if isinstance(foreign['short_position']['amount'], (int, float)) else f"  契約金額: {foreign['short_position']['amount']}")

    print(f"\n多空淨額:")
    print(f"  口數: {foreign['net_position']['contracts']:,}" if isinstance(foreign['net_position']['contracts'], int) else f"  口數: {foreign['net_position']['contracts']}")
    print(f"  契約金額: {foreign['net_position']['amount']:,.0f} 百萬元" if isinstance(foreign['net_position']['amount'], (int, float)) else f"  契約金額: {foreign['net_position']['amount']}")
    print(f"{'='*60}\n")


def get_trading_days(start_days_ago=0, days_count=1):
    """
    取得過去N個交易日的日期

    Parameters:
    -----------
    start_days_ago : int
        從幾天前開始（0=今日）
    days_count : int
        要取得幾個交易日

    Returns:
    --------
    list : 交易日期字符串列表（格式 YYYY/MM/DD）
    """
    trading_dates = []
    current_date = datetime.now().date() - timedelta(days=start_days_ago)

    while len(trading_dates) < days_count:
        if is_trading_day(current_date):
            trading_dates.append(current_date.strftime('%Y/%m/%d'))
        current_date -= timedelta(days=1)

    return trading_dates


def scrape_multiple_dates(dates_list, auto_fallback=True):
    """
    批量抓取多個日期的資料

    Parameters:
    -----------
    dates_list : list
        日期列表（格式 YYYY/MM/DD）
    auto_fallback : bool
        無資料時是否自動查詢前一交易日

    Returns:
    --------
    list : 包含多個date_data的列表
    """
    results = []

    for date_str in dates_list:
        try:
            data = scrape_taifex_data_advanced(date_str, auto_fallback=auto_fallback)
            results.append(data)
            print(f"[OK] {date_str} 資料已抓取")
        except Exception as e:
            print(f"[ERROR] {date_str} 抓取失敗: {e}")

    return results


def save_batch_to_markdown(data_list, format_type='f01', append_mode=False):
    """
    將批量交易資訊保存為固定名稱的Markdown文件（每行一條記錄）

    Parameters:
    -----------
    data_list : list
        包含多個data字典的列表
    format_type : str, optional
        格式類型：'f01', 'f02', 'f03'
    append_mode : bool, optional
        True=追加模式（新資料加到檔案末尾），False=覆蓋模式（新資料覆蓋舊資料）
    """

    if not data_list:
        print("[ERROR] 沒有資料可保存")
        return None

    # 使用固定的檔案名稱
    filename = f"taifex_{format_type.upper()}.md"

    # 收集所有行
    lines = []

    for data in data_list:
        foreign_data = data['data']['foreign_investors']
        date_display = data['date'].replace('/', '.')

        if format_type == 'f01':
            net_amount = foreign_data['net_position']['contracts']
            line = f"{date_display} F01 台指期貨-外資 [ 未平倉 多空淨額: {net_amount:,}口 ]"
        elif format_type == 'f02':
            long_amount = foreign_data['long_position']['contracts']
            line = f"{date_display} F02 台指期貨-外資 [ 未平倉 多方: {long_amount:,}口 ]"
        elif format_type == 'f03':
            short_amount = foreign_data['short_position']['contracts']
            line = f"{date_display} F03 台指期貨-外資 [ 未平倉 空方: {short_amount:,}口 ]"
        else:
            continue

        lines.append(line)

    # 寫入Markdown文件
    try:
        # 選擇寫入模式（追加或覆蓋）
        mode = 'a' if append_mode else 'w'

        with open(filename, mode, encoding='utf-8') as mdfile:
            if append_mode and os.path.exists(filename) and os.path.getsize(filename) > 0:
                # 追加模式且檔案非空，在最後加換行
                mdfile.write('\n')
            mdfile.write('\n'.join(lines))

        print(f"[SUCCESS] {len(lines)} 筆資料已成功{'追加到' if append_mode else '保存到'}: {filename}")
        return filename

    except Exception as e:
        print(f"[ERROR] 保存Markdown失敗: {e}")
        return None


def save_to_markdown(data, filename=None, format_type='f01'):
    """
    將三大法人交易資訊保存為Markdown文件

    Parameters:
    -----------
    data : dict
        抓取的交易資訊字典
    filename : str, optional
        Markdown檔案名稱，若不指定則使用日期作為檔案名
    format_type : str, optional
        格式類型：
        - 'f01': F01 台指期貨-外資 [ 未平倉 多空淨額 ]
        - 'f02': F02 台指期貨-外資 [ 未平倉 多方 ]
        - 'f03': F03 台指期貨-外資 [ 未平倉 空方 ]
    """

    foreign_data = data['data']['foreign_investors']
    date_display = data['date'].replace('/', '.')

    if format_type == 'f01':
        # F01: 未平倉多空淨額口數
        if filename is None:
            filename = f"taifex_{date_display}_F01.md"

        net_amount = foreign_data['net_position']['contracts']
        content = f"{date_display} F01 台指期貨-外資 [ 未平倉 多空淨額: {net_amount:,}口 ]"

    elif format_type == 'f02':
        # F02: 未平倉多方口數
        if filename is None:
            filename = f"taifex_{date_display}_F02.md"

        long_amount = foreign_data['long_position']['contracts']
        content = f"{date_display} F02 台指期貨-外資 [ 未平倉 多方: {long_amount:,}口 ]"

    elif format_type == 'f03':
        # F03: 未平倉空方口數
        if filename is None:
            filename = f"taifex_{date_display}_F03.md"

        short_amount = foreign_data['short_position']['contracts']
        content = f"{date_display} F03 台指期貨-外資 [ 未平倉 空方: {short_amount:,}口 ]"

    else:
        return None

    # 寫入Markdown文件
    try:
        with open(filename, 'w', encoding='utf-8') as mdfile:
            mdfile.write(content)

        print(f"[SUCCESS] 資料已成功存入: {filename}")
        return filename

    except Exception as e:
        print(f"[ERROR] 保存Markdown失敗: {e}")
        return None


def save_to_csv(data, filename=None, format_type='f01'):
    """
    將三大法人交易資訊保存為CSV文件

    Parameters:
    -----------
    data : dict
        抓取的交易資訊字典
    filename : str, optional
        CSV檔案名稱，若不指定則使用日期作為檔案名
    format_type : str, optional
        格式類型：
        - 'f01': F01 台指期貨-外資 [ 未平倉 多空淨額 ]
        - 'f02': F02 台指期貨-外資 [ 未平倉 多方 ]
        - 'f03': F03 台指期貨-外資 [ 未平倉 空方 ]
        - 'full': 完整格式
    """

    # 準備CSV數據
    rows = []
    foreign_data = data['data']['foreign_investors']
    date_display = data['date'].replace('/', '.')

    if format_type == 'f01':
        # F01: 未平倉多空淨額口數
        if filename is None:
            filename = f"taifex_{date_display}_F01.csv"

        net_amount = foreign_data['net_position']['contracts']
        rows.append([
            date_display,
            'F01',
            '台指期貨-外資',
            f'[ 未平倉 多空淨額: {net_amount:,}口 ]'
        ])

    elif format_type == 'f02':
        # F02: 未平倉多方口數
        if filename is None:
            filename = f"taifex_{date_display}_F02.csv"

        long_amount = foreign_data['long_position']['contracts']
        rows.append([
            date_display,
            'F02',
            '台指期貨-外資',
            f'[ 未平倉 多方: {long_amount:,}口 ]'
        ])

    elif format_type == 'f03':
        # F03: 未平倉空方口數
        if filename is None:
            filename = f"taifex_{date_display}_F03.csv"

        short_amount = foreign_data['short_position']['contracts']
        rows.append([
            date_display,
            'F03',
            '台指期貨-外資',
            f'[ 未平倉 空方: {short_amount:,}口 ]'
        ])

    else:  # full format
        # 完整格式：包含所有三大法人資訊
        date_display = data['date'].replace('/', '.')
        if filename is None:
            filename = f"taifex_{date_display}_full.csv"

        traders = {
            '自營商': data['data']['proprietary_traders'],
            '投信': data['data']['investment_trust'],
            '外資': data['data']['foreign_investors']
        }

        for name, trader_data in traders.items():
            f_code = 'F01' if name == '外資' else ''
            rows.append([
                date_display,
                f_code,
                name,
                trader_data['long_position']['contracts'],
                trader_data['long_position']['amount'],
                trader_data['short_position']['contracts'],
                trader_data['short_position']['amount'],
                trader_data['net_position']['contracts'],
                trader_data['net_position']['amount']
            ])

    # 寫入CSV文件
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)

        print(f"[SUCCESS] 資料已成功存入: {filename}")
        return filename

    except Exception as e:
        print(f"[ERROR] 保存CSV失敗: {e}")
        return None


def open_taifex_url(mode='net_position'):
    """
    打開台灣期貨交易所台指期貨-外資頁面

    Parameters:
    -----------
    mode : str
        查詢模式：
        - 'net_position': 未平倉多空淨額口數
        - 'long_position': 未平倉多方口數
        - 'short_position': 未平倉空方口數
    """
    url = 'https://www.taifex.com.tw/cht/3/totalTableDate'

    mode_desc = {
        'net_position': '未平倉多空淨額口數',
        'long_position': '未平倉多方口數',
        'short_position': '未平倉空方口數'
    }

    print(f"[ACTION] 正在打開: 台指期貨-外資 {mode_desc.get(mode, mode)}")
    webbrowser.open(url)


def on_press(key):
    """
    快捷鍵事件處理

    F01: 台指期貨-外資未平倉多空淨額口數
    F02: 台指期貨-外資未平倉多方口數
    F03: 台指期貨-外資未平倉空方口數
    """
    try:
        if key == keyboard.Key.f1:
            open_taifex_url('net_position')
        elif key == keyboard.Key.f2:
            open_taifex_url('long_position')
        elif key == keyboard.Key.f3:
            open_taifex_url('short_position')
        elif key == keyboard.Key.esc:
            # ESC鍵退出快捷鍵監聽
            return False
    except AttributeError:
        pass


def start_hotkey_listener():
    """
    啟動快捷鍵監聽

    使用說明:
    - F1 (F01): 打開台指期貨-外資 - 未平倉多空淨額口數
    - F2 (F02): 打開台指期貨-外資 - 未平倉多方口數
    - F3 (F03): 打開台指期貨-外資 - 未平倉空方口數
    - ESC: 停止快捷鍵監聽
    """

    print("\n" + "="*60)
    print("快捷鍵監聽已啟動")
    print("="*60)
    print("F1: 台指期貨-外資 (未平倉多空淨額口數)")
    print("F2: 台指期貨-外資 (未平倉多方口數)")
    print("F3: 台指期貨-外資 (未平倉空方口數)")
    print("ESC: 停止監聽")
    print("="*60 + "\n")

    with keyboard.Listener(on_press=on_press) as listener:  # type: ignore[arg-type]
        listener.join()


def save_to_csv_pandas(data, filename=None):
    """
    使用pandas將三大法人交易資訊保存為CSV文件（推薦）

    Parameters:
    -----------
    data : dict
        抓取的交易資訊字典
    filename : str, optional
        CSV檔案名稱
    """

    if filename is None:
        date_str = data['date'].replace('/', '-')
        filename = f"taifex_data_{date_str}.csv"

    # 準備DataFrame數據
    rows_list = []

    traders = {
        '自營商': data['data']['proprietary_traders'],
        '投信': data['data']['investment_trust'],
        '外資': data['data']['foreign_investors']
    }

    for name, trader_data in traders.items():
        row = {
            '日期': data['date'],
            '身份別': name,
            '多方_口數': trader_data['long_position']['contracts'],
            '多方_契約金額': trader_data['long_position']['amount'],
            '空方_口數': trader_data['short_position']['contracts'],
            '空方_契約金額': trader_data['short_position']['amount'],
            '淨額_口數': trader_data['net_position']['contracts'],
            '淨額_契約金額': trader_data['net_position']['amount']
        }
        rows_list.append(row)

    df = pd.DataFrame(rows_list)

    try:
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"[SUCCESS] 資料已成功存入: {filename}")
        return filename

    except Exception as e:
        print(f"[ERROR] 保存CSV失敗: {e}")
        return None


def show_menu():
    """
    顯示主菜單
    """
    print("\n" + "="*60)
    print("台灣期貨交易所三大法人交易資訊查詢系統")
    print("="*60)
    print("1. 查詢當日資料 (無資料則自動查前一交易日)")
    print("2. 查詢特定日期資料")
    print("3. 批量查詢 (1-50份資料，輸出到同一個.md檔案)")
    print("4. 啟動快捷鍵監聽 (F1/F2/F3)")
    print("5. 退出")
    print("="*60)
    return input("請選擇功能 (1-5): ").strip()


def show_format_menu():
    """
    顯示檔案格式菜單
    """
    print("\n選擇快捷鍵格式:")
    print("  F01: 未平倉 多空淨額")
    print("  F02: 未平倉 多方")
    print("  F03: 未平倉 空方")
    print("  all: 生成所有三種格式")
    return input("選擇 (F01/F02/F03/all): ").strip().lower()


if __name__ == '__main__':
    try:
        while True:
            choice = show_menu()

            if choice == '1':
                # 查詢當日資料（無資料時自動查前一交易日）
                data = scrape_taifex_data_advanced()
                print_foreign_investors_data(data)

                save_choice = input("\n要保存為Markdown嗎? (y/n): ").strip().lower()
                if save_choice == 'y':
                    format_choice = show_format_menu()

                    if format_choice == 'all':
                        save_to_markdown(data, format_type='f01')
                        save_to_markdown(data, format_type='f02')
                        save_to_markdown(data, format_type='f03')
                    else:
                        fmt = format_choice if format_choice in ['f01', 'f02', 'f03'] else 'f01'
                        save_to_markdown(data, format_type=fmt)

            elif choice == '2':
                # 查詢特定日期
                date_input = input("請輸入日期 (YYYY/MM/DD): ").strip()
                try:
                    data = scrape_taifex_data_advanced(date_input, auto_fallback=False)
                    print_foreign_investors_data(data)

                    save_choice = input("\n要保存為Markdown嗎? (y/n): ").strip().lower()
                    if save_choice == 'y':
                        format_choice = show_format_menu()

                        if format_choice == 'all':
                            save_to_markdown(data, format_type='f01')
                            save_to_markdown(data, format_type='f02')
                            save_to_markdown(data, format_type='f03')
                        else:
                            fmt = format_choice if format_choice in ['f01', 'f02', 'f03'] else 'f01'
                            save_to_markdown(data, format_type=fmt)
                except Exception as e:
                    print(f"[ERROR] 查詢失敗: {e}")

            elif choice == '3':
                # 批量查詢
                print("\n批量查詢選項:")
                print("  1. 查詢過去N個交易日")
                print("  2. 查詢日期範圍")
                batch_choice = input("選擇 (1/2): ").strip()

                if batch_choice == '1':
                    # 查詢過去N個交易日
                    try:
                        days_count = int(input("請輸入交易日天數 (1-50): ").strip())
                        if days_count < 1 or days_count > 50:
                            print("[ERROR] 請輸入1-50之間的數字")
                            continue

                        print(f"\n正在抓取過去{days_count}個交易日的資料...")
                        dates_list = get_trading_days(start_days_ago=0, days_count=days_count)
                        data_list = scrape_multiple_dates(dates_list)

                        if data_list:
                            print(f"\n成功抓取 {len(data_list)} 筆資料")

                            # 選擇是否覆蓋或追加
                            write_mode = input("選擇寫入模式 (o=覆蓋/a=追加): ").strip().lower()
                            append_mode = write_mode == 'a'

                            format_choice = show_format_menu()

                            if format_choice == 'all':
                                save_batch_to_markdown(data_list, format_type='f01', append_mode=append_mode)
                                save_batch_to_markdown(data_list, format_type='f02', append_mode=append_mode)
                                save_batch_to_markdown(data_list, format_type='f03', append_mode=append_mode)
                            else:
                                fmt = format_choice if format_choice in ['f01', 'f02', 'f03'] else 'f01'
                                save_batch_to_markdown(data_list, format_type=fmt, append_mode=append_mode)
                        else:
                            print("[ERROR] 未能成功抓取任何資料")

                    except ValueError:
                        print("[ERROR] 請輸入有效的數字")
                    except Exception as e:
                        print(f"[ERROR] 查詢失敗: {e}")

                elif batch_choice == '2':
                    # 查詢日期範圍
                    try:
                        start_date = input("請輸入開始日期 (YYYY/MM/DD): ").strip()
                        end_date = input("請輸入結束日期 (YYYY/MM/DD): ").strip()

                        start_obj = datetime.strptime(start_date, '%Y/%m/%d').date()
                        end_obj = datetime.strptime(end_date, '%Y/%m/%d').date()

                        if start_obj > end_obj:
                            print("[ERROR] 開始日期應早於結束日期")
                            continue

                        # 計算日期範圍內的交易日
                        dates_list = []
                        current_date = start_obj
                        while current_date <= end_obj:
                            if is_trading_day(current_date):
                                dates_list.append(current_date.strftime('%Y/%m/%d'))
                            current_date += timedelta(days=1)

                        if len(dates_list) > 50:
                            print(f"[WARNING] 日期範圍內包含 {len(dates_list)} 個交易日，已限制為最近50個")
                            dates_list = dates_list[-50:]

                        print(f"\n正在抓取 {len(dates_list)} 個交易日的資料...")
                        data_list = scrape_multiple_dates(dates_list)

                        if data_list:
                            print(f"\n成功抓取 {len(data_list)} 筆資料")

                            # 選擇是否覆蓋或追加
                            write_mode = input("選擇寫入模式 (o=覆蓋/a=追加): ").strip().lower()
                            append_mode = write_mode == 'a'

                            format_choice = show_format_menu()

                            if format_choice == 'all':
                                save_batch_to_markdown(data_list, format_type='f01', append_mode=append_mode)
                                save_batch_to_markdown(data_list, format_type='f02', append_mode=append_mode)
                                save_batch_to_markdown(data_list, format_type='f03', append_mode=append_mode)
                            else:
                                fmt = format_choice if format_choice in ['f01', 'f02', 'f03'] else 'f01'
                                save_batch_to_markdown(data_list, format_type=fmt, append_mode=append_mode)
                        else:
                            print("[ERROR] 未能成功抓取任何資料")

                    except ValueError as e:
                        print(f"[ERROR] 日期格式錯誤: {e}")
                    except Exception as e:
                        print(f"[ERROR] 查詢失敗: {e}")

            elif choice == '4':
                # 啟動快捷鍵監聽
                try:
                    start_hotkey_listener()
                except Exception as e:
                    print(f"[ERROR] 快捷鍵監聽失敗: {e}")
                    print("[INFO] 提示: 可能需要以管理員身份運行程式")

            elif choice == '5':
                print("感謝使用，再見！")
                break

            else:
                print("[ERROR] 無效的選擇，請重試")

    except KeyboardInterrupt:
        print("\n程式已被中斷")
    except Exception as e:
        print(f"[ERROR] 錯誤: {e}")
