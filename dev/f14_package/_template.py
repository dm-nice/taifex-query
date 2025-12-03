"""
_template.py
這是給外包人員的「標準模具」範本。
請複製此檔案，並將檔名修改為指定的模組名稱（例如 f02_options.py）。

開發規範：
1. 檔名必須與 MODULE 變數一致。
2. 必須繼承 BaseFetcher 並實作 fetch 方法。
3. 必須回傳 FetchResult 物件（或符合格式的字典）。
"""

from modules.base import BaseFetcher, FetchResult

# [重要] 請將此變數修改為與檔名一致 (不含 .py)
MODULE = "_template"

class Fetcher(BaseFetcher):
    def fetch(self, date: str) -> dict:
        """
        執行抓取邏輯
        :param date: 查詢日期 (YYYY-MM-DD)
        :return: FetchResult (或是 dict)
        """
        try:
            # 1. 在這裡寫你的爬蟲邏輯
            # url = ...
            # data = ...
            
            # 模擬抓取到的資料
            data = {
                "外資多方口數": 100,
                "外資空方口數": 50,
                "外資多空淨額": 50
            }
            
            summary = f"測試模組：{date} 執行成功"

            # 2. 回傳結果
            # 建議使用 FetchResult 物件確保格式正確
            return FetchResult(
                module=MODULE,
                date=date,
                status="success",
                summary=summary,
                data=data,
                source="TAIFEX"
            ).model_dump()

        except Exception as e:
            # 錯誤處理
            return FetchResult(
                module=MODULE,
                date=date,
                status="error",
                error=str(e)
            ).model_dump()

# 為了讓 run.py 能直接呼叫 fetch 函式，我們需要實例化或是包裝一下
# 但根據目前的 run.py 設計，它是直接呼叫 module.fetch(date)
# 所以我們需要把上面的 Class 轉成 module level function，或是調整 run.py
# 
# 修正：目前的 run.py 是呼叫 `mod.fetch(date)`。
# 為了保持簡單，外包人員可以直接寫一個 fetch 函式，不一定要用 Class，
# 但為了 Type Hint，我們保留 BaseFetcher 的概念作為參考。
# 
# 下面這是符合目前 run.py 的寫法（函式版）：

def fetch(date: str) -> dict:
    # 實作內容同上
    return Fetcher().fetch(date)
