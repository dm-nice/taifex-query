import datetime
import pytz

def get_taiwan_now():
    """獲取台灣目前的 datetime 物件"""
    tz = pytz.timezone('Asia/Taipei')
    return datetime.datetime.now(tz)

def get_current_taiwan_date(fmt="%Y.%m.%d"):
    """
    獲取台灣當前的日期字串
    格式預設為: YYYY.MM.DD
    """
    return get_taiwan_now().strftime(fmt)

def is_trading_day(date_obj=None):
    """
    判斷是否為交易日
    1. 排除週六、週日
    2. 排除國定假日 (待擴充假日清單)
    """
    if date_obj is None:
        date_obj = get_taiwan_now()
    
    # 轉換為 date 物件（如果是 datetime）
    if isinstance(date_obj, datetime.datetime):
        date_obj = date_obj.date()
    
    # 週六(5), 週日(6)
    if date_obj.weekday() >= 5:
        return False
        
    # 台灣 2026 基本國定假日表 (範例，需定期更新)
    # 這裡可以根據需要讀取外部 JSON 或硬編碼
    holidays = [
        datetime.date(2026, 1, 1),   # 元旦
        datetime.date(2026, 2, 16),  # 春節連假開始 (推測)
        datetime.date(2026, 2, 17),
        datetime.date(2026, 2, 18),
        datetime.date(2026, 2, 19),
        datetime.date(2026, 2, 20),
        datetime.date(2026, 2, 23),
        datetime.date(2026, 2, 27),  # 228
        datetime.date(2026, 4, 3),   # 清明/兒童節
        datetime.date(2026, 4, 6),   # 補假
        datetime.date(2026, 6, 19),  # 端午節
        datetime.date(2026, 9, 25),  # 中秋節
        datetime.date(2026, 10, 9),  # 國慶連假
    ]
    
    if date_obj in holidays:
        return False
        
    return True

def get_previous_trading_day(date_obj=None):
    """
    獲取指定日期之前的最近一個交易日
    """
    if date_obj is None:
        date_obj = get_taiwan_now()
        
    if isinstance(date_obj, datetime.datetime):
        date_obj = date_obj.date()
        
    # 往回推算，直到找到交易日
    temp_date = date_obj - datetime.timedelta(days=1)
    while not is_trading_day(temp_date):
        temp_date -= datetime.timedelta(days=1)
        
    return temp_date

if __name__ == "__main__":
    # 簡單測試
    print(f"目前台灣日期: {get_current_taiwan_date()}")
    print(f"今天是否交易日: {is_trading_day()}")
    print(f"前一個交易日: {get_previous_trading_day()}")
