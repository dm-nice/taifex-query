"""
計算台指期 5 日平均收盤價 (5-Day Moving Average)
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
import json


def fetch_taifex_futures_data(days=30):
    """
    從 TAIFEX 開放 API 取得台指期交易資料
    
    Args:
        days: 要取得過去幾天的資料，預設 30 天
    
    Returns:
        DataFrame 包含日期和收盤價
    """
    try:
        # 使用 TAIFEX 開放 API - 期貨基本行情
        url = "https://openapi.taifex.com.tw/v1/DailyFuturesClosed"
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            'startDate': start_date.strftime('%Y%m%d'),
            'endDate': end_date.strftime('%Y%m%d'),
            'productID': 'TX'  # TX = 台指期
        }
        
        print(f"正在從 TAIFEX API 取得台指期資料...")
        response = requests.get(url, params=params, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                # 轉換為 DataFrame
                records = []
                for row in data:
                    try:
                        records.append({
                            'date': row.get('Date') or row.get('date'),
                            'close': float(row.get('Close') or row.get('close') or 0)
                        })
                    except (ValueError, TypeError, KeyError):
                        continue
                
                if records:
                    df = pd.DataFrame(records)
                    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d', errors='coerce')
                    df = df.dropna(subset=['date'])
                    df = df.sort_values('date').reset_index(drop=True)
                    return df
        
        print("API 回應無資料")
        return None
        
    except Exception as e:
        print(f"取得 TAIFEX API 資料失敗: {e}")
        return None


def create_sample_data():
    """
    建立範例資料（如果沒有真實資料）
    
    Returns:
        DataFrame 包含台指期範例資料
    """
    import random
    print("正在建立範例資料...")
    
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    
    # 生成台指期模擬價格 (約 16000~17000 的範圍)
    base_price = 16500
    prices = []
    for i in range(len(dates)):
        change = random.uniform(-100, 100)
        base_price += change
        prices.append(base_price)
    
    df = pd.DataFrame({
        'date': dates,
        'close': prices
    })
    
    return df


def calculate_5day_ma(df):
    """
    計算 5 日平均收盤價
    
    Args:
        df: DataFrame 包含 date 和 close 欄位
    
    Returns:
        DataFrame 包含原資料和 5 日移動平均
    """
    if df is None or len(df) < 5:
        print("資料不足，需要至少 5 天的資料")
        return None
    
    df = df.copy()
    df['MA5'] = df['close'].rolling(window=5, min_periods=1).mean()
    
    return df


def display_results(df):
    """
    顯示結果
    
    Args:
        df: DataFrame 包含計算結果
    """
    print("\n" + "="*70)
    print("台指期 5 日平均收盤價")
    print("="*70)
    
    # 只顯示最近 10 筆資料
    display_df = df.tail(10).copy()
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    display_df['close'] = display_df['close'].apply(lambda x: f"{x:,.0f}")
    display_df['MA5'] = display_df['MA5'].apply(lambda x: f"{x:,.2f}")
    
    print(display_df.to_string(index=False))
    print("="*70)
    
    # 顯示最新資料
    latest = df.iloc[-1]
    print(f"\n最新收盤價: {latest['close']:,.0f}")
    print(f"5 日平均價: {latest['MA5']:,.2f}")
    
    if len(df) >= 2:
        prev_ma5 = df.iloc[-2]['MA5']
        change = latest['MA5'] - prev_ma5
        print(f"平均價變化: {change:+,.2f}")


def save_results(df, output_path="data/taifex_5day_ma.csv"):
    """
    儲存結果到 CSV 檔案
    
    Args:
        df: DataFrame 計算結果
        output_path: 輸出檔案路徑
    """
    try:
        df_save = df.copy()
        df_save['date'] = df_save['date'].dt.strftime('%Y-%m-%d')
        df_save.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\n結果已儲存到: {output_path}")
    except Exception as e:
        print(f"儲存檔案失敗: {e}")


def main():
    """
    主程式
    """
    print("台指期 5 日平均收盤價計算程式")
    print("-" * 70)
    
    # 方式 1: 從 TAIFEX API 取得資料
    print("\n1. 嘗試從 TAIFEX API 取得台指期資料...")
    df = fetch_taifex_futures_data(days=30)
    
    # 如果 API 失敗或無資料，使用範例資料
    if df is None or len(df) == 0:
        print("\n2. API 無法取得資料，使用範例資料進行演示...")
        df = create_sample_data()
    
    if df is None:
        print("\n無法取得資料")
        return
    
    # 確保有 close 欄位
    if 'close' not in df.columns:
        print("資料缺少收盤價欄位 (close)")
        return
    
    # 計算 5 日平均
    result_df = calculate_5day_ma(df)
    
    if result_df is not None:
        # 顯示結果
        display_results(result_df)
        
        # 儲存結果
        save_results(result_df)


if __name__ == "__main__":
    main()
