
import sys
import os
import unittest
from datetime import datetime, timedelta

# Add module path
sys.path.append(os.path.join(os.getcwd(), 'dev', 'f07_package'))
import f07_fetcher

class TestF07Fetcher(unittest.TestCase):
    def test_today(self):
        # 測試今日 (2025-12-10 應該有資料)
        date = "2025-12-10"
        print(f"\nTesting {date}...")
        result = f07_fetcher.fetch(date)
        print(result)
        self.assertIn("F07:", result)
        self.assertIn("%", result)
        self.assertIn("[TAIFEX]", result)

    def test_future_limit(self):
        # 測試未來日期 (API 會回傳最新資料，而非錯誤)
        # 這是 API 特性，需在 Spec 中註明
        future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        print(f"\nTesting Future {future} (Expect Latest Data)...")
        result = f07_fetcher.fetch(future)
        print(result)
        # 由於 API 無視日期，這裡會由成功抓取最新資料取代錯誤
        self.assertIn("F07:", result)
        self.assertIn("%", result)

if __name__ == '__main__':
    unittest.main()
