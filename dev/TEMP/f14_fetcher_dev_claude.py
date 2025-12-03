"""
F14 Fetcher 開發模組

此模組負責抓取台指期貨 (TX) 當日收盤價。
"""

from modules.base import BaseFetcher, FetchResult

MODULE = "f14_fetcher_dev"

class TXFuturesFetcher(BaseFetcher):
    def fetch(self, date: str) -> dict:
        """
        執行抓取邏輯
        :param date: 查詢日期 (YYYY-MM-DD)
        :return: FetchResult (或是 dict)
        """
        try:
            # 模擬抓取到的數據
            data = {
                "台指期貨收盤價": 27758.0
            }

            summary = f"F14 模組：{date} 執行成功"

            # 返回結果
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
                error=str(e),
                source="TAIFEX"
            ).model_dump()