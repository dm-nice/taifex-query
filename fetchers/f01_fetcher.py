"""
fetchers/f01_fetcher.py
正式版 F01 fetcher - 台指期貨外資淨口數

此模組由 outsource/f01_fetcher_dev.py 驗收通過後移入
供 run.py 主程式自動呼叫
"""

import requests
import pandas as pd
import json

MODULE = "f01"


def fetch(date: str) -> dict:
    """
    輸入: date (YYYY-MM-DD)
    輸出: dict，成功時應包含 "module","date","status":"success","data"
    """
    try:
        url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={date.replace('-', '/')}"
        resp = requests.get(url, timeout=10)
        resp.encoding = "utf-8"

        tables = pd.read_html(resp.text)
        if len(tables) == 0:
            return {"module": MODULE, "date": date, "status": "fail", "error": "無法擷取任何表格"}

        df = tables[0]

        # 支援 MultiIndex 與單層欄位
        if isinstance(df.columns, pd.MultiIndex):
            # 找到身份別(或稱身份)欄位
            trader_col = None
            for col in df.columns:
                if '身份別' in str(col) or '身份' in str(col):
                    trader_col = col
                    break
            if trader_col is None:
                return {"module": MODULE, "date": date, "status": "fail", "error": "找不到身份別欄位"}

            # 篩選外資
            foreign_rows = df[df[trader_col] == '外資']
            
            if len(foreign_rows) == 0:
                return {"module": MODULE, "date": date, "status": "fail", "error": "該日無外資交易資料"}

            # 尋找未平倉餘額 > 多方 > 口數 與 未平倉餘額 > 空方 > 口數
            long_col = None
            short_col = None
            for col in df.columns:
                col_s = ''.join(str(x) for x in col)
                if '未平倉餘額' in col_s and '多方' in col_s and '口' in col_s:
                    long_col = col
                if '未平倉餘額' in col_s and '空方' in col_s and '口' in col_s:
                    short_col = col

            if long_col is None or short_col is None:
                return {"module": MODULE, "date": date, "status": "fail", "error": "找不到未平倉餘額的多/空口數欄位"}

            def to_int(v):
                if pd.isna(v):
                    return 0
                return int(str(v).replace(',', '').strip())

            f_long = to_int(foreign_rows[long_col].values[0])
            f_short = to_int(foreign_rows[short_col].values[0])
            f_net = f_long - f_short
            
            data = {
                "外資多單口數": f_long,
                "外資空單口數": f_short,
                "外資多空淨額": f_net
            }
            
            summary = f"F1: 台指期外資淨額：{f_net}（多：{f_long}，空：{f_short}）"

            return {
                "module": MODULE,
                "date": date,
                "status": "success",
                "summary": summary,
                "data": data,
                "source": "TAIFEX"
            }

        else:
            # 單層欄位
            cols = [c for c in df.columns]
            # 嘗試找到身份別欄位的索引
            trader_col = None
            for name in ['身份別', '身份', '交易人', '交易人名稱']:
                if name in cols:
                    trader_col = name
                    break
            if trader_col is None:
                return {"module": MODULE, "date": date, "status": "fail", "error": "找不到身份別欄位"}

            foreign = df[df[trader_col] == '外資']
            
            if len(foreign) == 0:
                return {"module": MODULE, "date": date, "status": "fail", "error": "該日無外資交易資料"}

            # 多方與空方口數欄位
            long_col = None
            short_col = None
            for name in ['未平倉餘額-多方-口數', '多方-口數', '多方', '多單口數', '多方未平倉口數']:
                if name in cols:
                    long_col = name
                    break
            for name in ['未平倉餘額-空方-口數', '空方-口數', '空方', '空單口數', '空方未平倉口數']:
                if name in cols:
                    short_col = name
                    break

            if long_col is None or short_col is None:
                return {"module": MODULE, "date": date, "status": "fail", "error": "找不到多/空口數欄位"}

            def to_int(v):
                if pd.isna(v):
                    return 0
                return int(str(v).replace(',', '').strip())

            f_long = to_int(foreign.iloc[0][long_col])
            f_short = to_int(foreign.iloc[0][short_col])
            f_net = f_long - f_short
            
            data = {
                "外資多單口數": f_long,
                "外資空單口數": f_short,
                "外資多空淨額": f_net
            }
            
            summary = f"F1: 台指期外資淨額：{f_net}（多：{f_long}，空：{f_short}）"

            return {
                "module": MODULE,
                "date": date,
                "status": "success",
                "summary": summary,
                "data": data,
                "source": "TAIFEX"
            }

    except Exception as e:
        return {"module": MODULE, "date": date, "status": "fail", "error": str(e)}


if __name__ == '__main__':
    # 測試入口，使用指定日期並輸出 JSON
    test_date = '2025-11-28'
    res = fetch(test_date)
    print(json.dumps(res, ensure_ascii=False, indent=2))
