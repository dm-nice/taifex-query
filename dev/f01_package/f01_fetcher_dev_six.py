import sys
import json
import requests
import pandas as pd
from datetime import datetime

def fetch_taifex_data(date_str: str):
    """
    Fetches and processes TAIFEX foreign open interest data for a given date.

    Args:
        date_str: The date in 'YYYY-MM-DD' format.

    Returns:
        A JSON string with the structured data or an error message.
    """
    try:
        # Validate and format the date
        query_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y/%m/%d")
    except ValueError:
        return json.dumps({
            "模組": "f01",
            "日期": date_str,
            "狀態": "失敗",
            "錯誤": "日期格式錯誤，請使用 YYYY-MM-DD"
        }, ensure_ascii=False, indent=2)

    url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={query_date}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Check if the response content indicates no data
        if "查詢日期無交易資訊" in response.text:
            return json.dumps({
                "模組": "f01",
                "日期": date_str,
                "狀態": "失敗",
                "錯誤": "該日無交易資料"
            }, ensure_ascii=False, indent=2)

        # Use pandas to read HTML tables
        tables = pd.read_html(response.text)
        
        # Find the correct table by looking for '外資' in the table content
        df = None
        for table in tables:
            if '外資' in table.to_string():
                df = table
                break
        
        if df is None:
            raise ValueError("找不到包含'外資'的資料表")

        # --- Robust Column Handling ---
        # Handle potential multi-index or single-index columns by creating clean, predictable names
        new_cols = []
        for col in df.columns.values:
            if isinstance(col, tuple):
                # Join multi-level column names
                new_cols.append('_'.join(map(str, col)).strip())
            else:
                new_cols.append(str(col).strip())
        df.columns = new_cols

        # Dynamically find the required column names
        identity_col = next((c for c in df.columns if '身份別' in c), None)
        long_col = next((c for c in df.columns if '未平倉餘額' in c and '多方' in c and '口數' in c), None)
        short_col = next((c for c in df.columns if '未平倉餘額' in c and '空方' in c and '口數' in c), None)

        if not all([identity_col, long_col, short_col]):
            raise ValueError("無法找到所有必要的欄位 (身份別, 多方口數, 空方口數)")

        # Find the row for '外資'
        foreign_investor_row = df[df[identity_col].str.strip() == '外資']

        if foreign_investor_row.empty:
            raise ValueError("在資料表中找不到'外資'的資料")

        # Extract data using the dynamically found column names
        long_contracts = int(foreign_investor_row[long_col].iloc[0])
        short_contracts = int(foreign_investor_row[short_col].iloc[0])
        net_contracts = long_contracts - short_contracts

        # Prepare success output
        result = {
            "模組": "f01",
            "日期": date_str,
            "狀態": "成功",
            "摘要": f"F1: 台指期外資淨額：{net_contracts}（多：{long_contracts}，空：{short_contracts}）",
            "資料": {
                "外資多單口數": long_contracts,
                "外資空單口數": short_contracts,
                "外資多空淨額": net_contracts
            },
            "來源": "TAIFEX"
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    except requests.exceptions.Timeout:
        return json.dumps({
            "模組": "f01",
            "日期": date_str,
            "狀態": "失敗",
            "錯誤": "連線逾時 (timeout)"
        }, ensure_ascii=False, indent=2)
    except (requests.exceptions.RequestException, ValueError, IndexError, KeyError) as e:
        return json.dumps({
            "模組": "f01",
            "日期": date_str,
            "狀態": "失敗",
            "錯誤": f"該日無交易資料或網頁結構異常: {str(e)}"
        }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python f01_fetcher_dev.py YYYY-MM-DD", file=sys.stderr)
        sys.exit(1)
    
    date_argument = sys.argv[1]
    json_output = fetch_taifex_data(date_argument)
    print(json_output)
