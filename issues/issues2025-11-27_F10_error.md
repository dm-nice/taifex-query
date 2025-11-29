範例輸出：issues/2025-11-27_F10_error.md
markdown
# 錯誤紀錄：F10 模組

## 日期
2025-11-27

## 模組
F10 - 台指選擇權每日交易行情

## 錯誤摘要
AttributeError: 'NoneType' object has no attribute 'find'

## 錯誤訊息 (Traceback)
Traceback (most recent call last): File "f10_fetcher.py", line 42, in <module> table = soup.find("table", {"id": "daily-options"}) AttributeError: 'NoneType' object has no attribute 'find'

程式碼

## 對應快照
- raw/f10/f10_init_2025-11-27.html
- raw/f10/f10_after_2025-11-27.html
- raw/f10/f10_error_2025-11-27.html
- raw/f10/f10_error_2025-11-27.png

---

## DOM 抽取結果：raw/f10/f10_after_2025-11-27.html

### <select> 區塊
<select id="contract"> <option value="TXO">臺指選擇權</option> <option value="TEO">電子選擇權</option> </select>

程式碼

### <table> 區塊
<table id="daily-options"> <tr><th>履約價</th><th>成交量</th><th>未平倉</th></tr> <tr><td>18000</td><td>1523</td><td>8421</td></tr> </table>

程式碼

---

## 錯誤 Log 片段 (logs/f10_fetcher.log)
2025-11-27 13:00:12 ERROR 無法找到 daily-options 表格 2025-11-27 13:00:12 Traceback (most recent call last): File "f10_fetcher.py", line 42, in <module> table = soup.find("table", {"id": "daily-options"}) AttributeError: 'NoneType' object has no attribute 'find'

程式碼

---

## 分析建議
- 確認 TXO `<select>` 是否正確選中  
- 檢查表格 ID 是否改版  
- 若 DOM 結構改版，需更新 parser selector  
✅ 效果
這份 .md 就是 debug_pipeline.py 自動生成的完整錯誤紀錄：

有 錯誤摘要 + Traceback

有 DOM <select> / <table> 區塊

有 log 錯誤訊息

最後還附上 分析建議








