# 模組介面規範 (interface_spec.md)

本文件定義所有模組 (F01–F20) 的統一介面規範，確保主程式能 plug-and-play。

---

## 函式介面
```python
def fetch(date: str) -> dict:
    """
    輸入:
        date (str): 日期字串，格式 YYYY-MM-DD
    輸出:
        dict: 統一格式 (成功或失敗)
    """



輸入格式
date: str，格式 YYYY-MM-DD

回傳格式
成功：
python
{
    "module": "fXX",
    "date": "2025-11-28",
    "status": "success",
    "data": {...}   # 抓取到的資料 (dict 或 DataFrame)
}
失敗：
python
{
    "module": "fXX",
    "date": "2025-11-28",
    "status": "fail",
    "error": "錯誤訊息"
}
錯誤回報
若失敗，必須回傳 status="fail" 並附上 error

主程式會呼叫 utils/debug_pipeline.py，自動產生 issues/YYYY-MM-DD_module_error.md

測試規範
模組需能獨立執行：

python
if __name__ == "__main__":
    result = fetch("2025-11-28")
    print(result)


測試規範
模組需能獨立執行：

python
if __name__ == "__main__":
    result = fetch("2025-11-28")
    print(result)
設計理念
統一介面：所有模組都用 fetch(date)

統一回傳格式：主程式能自動分流

易於維護：失敗自動回報，成功自動存檔

程式碼

---


