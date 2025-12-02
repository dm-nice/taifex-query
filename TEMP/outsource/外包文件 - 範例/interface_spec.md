# 模組介面規範 (interface_spec.md)

本文件定義所有模組 (F01–F20) 的統一輸入 / 輸出介面規範。

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
成功回傳格式
json
{
    "module": "fXX",
    "date": "2025-11-28",
    "status": "success",
    "data": {...}   // 抓取到的資料 (dict 或 DataFrame)
}
失敗回傳格式
json
{
    "module": "fXX",
    "date": "2025-11-28",
    "status": "fail",
    "error": "錯誤訊息"
}
測試規範
模組需能獨立執行：

python
if __name__ == "__main__":
    result = fetch("2025-11-28")
    print(result)
程式碼

---