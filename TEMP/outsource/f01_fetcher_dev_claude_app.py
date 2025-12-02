#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
f01_fetcher_dev.py
抓取台指期貨外資的未平倉淨口數 (OI)
"""

import sys
import json
import requests
import pandas as pd
from datetime import datetime


def fetch_taifex_oi(date_str):
    """
    抓取指定日期的台指期貨外資未平倉資料
    
    Args:
        date_str: 日期字串，格式 YYYY-MM-DD
        
    Returns:
        dict: 包含狀態、資料等資訊的字典
    """
    try:
        # 轉換日期格式: YYYY-MM-DD -> YYYY/MM/DD
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        url_date = date_obj.strftime("%Y/%m/%d")
        
        # 建立 URL
        url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryType=1&marketCode=0&date={url_date}"
        
        # 發送請求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 使用 pandas 讀取 HTML 表格
        tables = pd.read_html(response.text)
        
        if not tables:
            return {
                "模組": "f01",
                "日期": date_str,
                "狀態": "失敗",
                "錯誤": "該日無交易資料"
            }
        
        # 找到包含「身份別」欄位的表格
        target_table = None
        for table in tables:
            if '身份別' in table.columns or ('身份別' in str(table.iloc[0].values)):
                target_table = table
                break
        
        if target_table is None:
            return {
                "模組": "f01",
                "日期": date_str,
                "狀態": "失敗",
                "錯誤": "無法找到預期欄位"
            }
        
        # 處理 MultiIndex 表頭
        if isinstance(target_table.columns, pd.MultiIndex):
            df = target_table
        else:
            # 如果不是 MultiIndex，嘗試將第一行作為表頭
            df = target_table
            if '身份別' not in df.columns:
                df.columns = df.iloc[0]
                df = df[1:]
        
        # 尋找「外資」行
        foreign_row = None
        for idx, row in df.iterrows():
            if '外資' in str(row.iloc[0]):
                foreign_row = row
                break
        
        if foreign_row is None:
            return {
                "模組": "f01",
                "日期": date_str,
                "狀態": "失敗",
                "錯誤": "無法找到外資資料"
            }
        
        # 提取未平倉口數資料
        # 根據表格結構，找到「未平倉餘額」下的「多方」和「空方」口數
        long_oi = None
        short_oi = None
        
        # 遍歷欄位尋找未平倉資料
        for col_idx, col_name in enumerate(df.columns):
            col_str = str(col_name)
            # 尋找包含「未平倉」、「多方」、「口數」的欄位
            if '未平倉' in col_str and '多方' in col_str and '口數' in col_str:
                try:
                    long_oi = int(str(foreign_row.iloc[col_idx]).replace(',', ''))
                except:
                    pass
            # 尋找包含「未平倉」、「空方」、「口數」的欄位
            if '未平倉' in col_str and '空方' in col_str and '口數' in col_str:
                try:
                    short_oi = int(str(foreign_row.iloc[col_idx]).replace(',', ''))
                except:
                    pass
        
        # 如果上述方法失敗，嘗試用欄位索引直接取值
        if long_oi is None or short_oi is None:
            try:
                # 通常多方口數在較前面的欄位，空方在後面
                values = [str(v).replace(',', '') for v in foreign_row.values[1:]]
                numeric_values = []
                for v in values:
                    try:
                        numeric_values.append(int(v))
                    except:
                        continue
                
                if len(numeric_values) >= 2:
                    long_oi = numeric_values[0]
                    short_oi = numeric_values[1]
            except:
                pass
        
        if long_oi is None or short_oi is None:
            return {
                "模組": "f01",
                "日期": date_str,
                "狀態": "失敗",
                "錯誤": "無法解析未平倉口數"
            }
        
        # 計算淨額
        net_oi = long_oi - short_oi
        
        # 組成摘要
        summary = f"F1: 台指期外資淨額：{net_oi}（多：{long_oi}，空：{short_oi}）"
        
        return {
            "模組": "f01",
            "日期": date_str,
            "狀態": "成功",
            "摘要": summary,
            "資料": {
                "外資多單口數": long_oi,
                "外資空單口數": short_oi,
                "外資多空淨額": net_oi
            },
            "來源": "TAIFEX"
        }
        
    except requests.Timeout:
        return {
            "模組": "f01",
            "日期": date_str,
            "狀態": "失敗",
            "錯誤": "連線逾時 (timeout)"
        }
    except requests.RequestException as e:
        return {
            "模組": "f01",
            "日期": date_str,
            "狀態": "失敗",
            "錯誤": f"網路請求錯誤: {str(e)}"
        }
    except Exception as e:
        return {
            "模組": "f01",
            "日期": date_str,
            "狀態": "失敗",
            "錯誤": f"處理錯誤: {str(e)}"
        }


def main():
    """主程式進入點"""
    if len(sys.argv) < 2:
        print("使用方式: python f01_fetcher_dev.py YYYY-MM-DD")
        sys.exit(1)
    
    date_str = sys.argv[1]
    
    # 驗證日期格式
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print(json.dumps({
            "模組": "f01",
            "日期": date_str,
            "狀態": "失敗",
            "錯誤": "日期格式錯誤，請使用 YYYY-MM-DD"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    # 執行抓取
    result = fetch_taifex_oi(date_str)
    
    # 輸出 JSON 結果
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 根據狀態設定退出碼
    sys.exit(0 if result["狀態"] == "成功" else 1)


if __name__ == "__main__":
    main()
