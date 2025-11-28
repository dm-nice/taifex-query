from factors.f1_api import get_f1_foreign_oi_by_date, save_f1_line

target_date = "20251126"  # 你只要改這一行

f1_oi = get_f1_foreign_oi_by_date(target_date, debug_mode=True)
if f1_oi is not None:
    save_f1_line(target_date, f1_oi)
else:
    print("⚠️ F1 抓取失敗，未寫入")