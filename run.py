"""
主程式骨架 (run.py)
統一呼叫 F1–F20 模組，整合結果並處理錯誤
"""

# 匯入 F1–F20 模組
from fetchers.f01_fetcher import fetch as f01
from fetchers.f02_fetcher import fetch as f02
from fetchers.f03_fetcher import fetch as f03
from fetchers.f04_fetcher import fetch as f04
from fetchers.f05_fetcher import fetch as f05
from fetchers.f06_fetcher import fetch as f06
from fetchers.f07_fetcher import fetch as f07
from fetchers.f08_fetcher import fetch as f08
from fetchers.f09_fetcher import fetch as f09
from fetchers.f10_fetcher import fetch as f10
from fetchers.f11_fetcher import fetch as f11
from fetchers.f12_fetcher import fetch as f12
from fetchers.f13_fetcher import fetch as f13
from fetchers.f14_fetcher import fetch as f14
from fetchers.f15_fetcher import fetch as f15
from fetchers.f16_fetcher import fetch as f16
from fetchers.f17_fetcher import fetch as f17
from fetchers.f18_fetcher import fetch as f18
from fetchers.f19_fetcher import fetch as f19
from fetchers.f20_fetcher import fetch as f20

# 工具模組 (錯誤回報)
from utils.debug_pipeline import report_error


def main(date: str):
    modules = [
        ("F01", f01),
        ("F02", f02),
        ("F03", f03),
        ("F04", f04),
        ("F05", f05),
        ("F06", f06),
        ("F07", f07),
        ("F08", f08),
        ("F09", f09),
        ("F10", f10),
        ("F11", f11),
        ("F12", f12),
        ("F13", f13),
        ("F14", f14),
        ("F15", f15),
        ("F16", f16),
        ("F17", f17),
        ("F18", f18),
        ("F19", f19),
        ("F20", f20),
    ]

    results = []

    for name, module in modules:
        try:
            result = module(date)
            results.append(result)
        except Exception as e:
            # 呼叫錯誤回報流程
            report_error(module=name, date=date, error=str(e))

    return results


if __name__ == "__main__":
    # 範例：執行 2025-11-29 的資料抓取
    data = main("2025-11-29")
    print(data)
