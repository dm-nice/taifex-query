# C:\Taifex\run.py
from factors_taifex import get_f1_foreign_oi

if __name__ == "__main__":
    test_date = "20251125"  # 可改為最近交易日
    print("F1 外資期貨 OI：", get_f1_foreign_oi(test_date, debug_mode=True))