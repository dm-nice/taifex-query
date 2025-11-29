"""
計算台指期 20 日平均收盤價 (20-Day Moving Average)
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
import json
import os


def fetch_taifex_futures_data(product_id='TX', days=60):
    """
    從 TAIFEX 開放 API 取得台指期交易資料
    
    Args:
        product_id: 商品代碼，預設為 'TX' (台指期)
        days: 要取得過去幾天的資料，預設 60 天
    
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
            'productID': product_id
        }
        
        print(f"正在從 TAIFEX API 取得 {product_id} 資料 (最近 {days} 天)...")
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
        
        print("API 回應無資料或格式錯誤")
        return None
        
    except Exception as e:
        print(f"取得 TAIFEX API 資料失敗: {e}")
        return None


def create_sample_data(days=60):
    """
    建立範例資料（如果 API 呼叫失敗）
    
    Args:
        days: 要建立幾天的資料
        
    Returns:
        DataFrame 包含台指期範例資料
    """
    import random
    print(f"正在建立 {days} 天的範例資料...")
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # 生成台指期模擬價格 (約 20000~22000 的範圍)
    base_price = 21000
    prices = [base_price + random.uniform(-200, 200) for _ in range(len(dates))]
    
    df = pd.DataFrame({
        'date': dates,
        'close': prices
    })
    
    return df


def calculate_20day_ma(df):
    """
    計算 20 日平均收盤價
    
    Args:
        df: DataFrame 包含 date 和 close 欄位
    
    Returns:
        DataFrame 包含原資料和 20 日移動平均
    """
    if df is None or len(df) < 20:
        print("資料不足，需要至少 20 天的資料才能進行有意義的計算")
        return df # 即使不足也回傳，以便顯示原始資料
    
    df = df.copy()
    df['MA20'] = df['close'].rolling(window=20, min_periods=1).mean()
    
    return df


def display_results(df):
    """
    顯示結果
    
    Args:
        df: DataFrame 包含計算結果
    """
    print("\n" + "="*70)
    print("台指期 20 日平均收盤價 (MA20)")
    print("="*70)
    
    if 'MA20' not in df.columns:
        print("無法計算 20 日均線，僅顯示原始資料。")
        print(df.tail(10).to_string(index=False))
        return

    # 只顯示最近 15 筆資料
    display_df = df.tail(15).copy()
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    display_df['close'] = display_df['close'].apply(lambda x: f"{x:,.0f}")
    display_df['MA20'] = display_df['MA20'].apply(lambda x: f"{x:,.2f}")
    
    print(display_df.to_string(index=False))
    print("="*70)
    
    # 顯示最新資料
    latest = df.iloc[-1]
    print(f"\n最新收盤價: {latest['close']:,.0f}")
    print(f"20 日平均價: {latest['MA20']:,.2f}")
    
    if len(df) >= 2:
        prev_ma20 = df.iloc[-2]['MA20']
        change = latest['MA20'] - prev_ma20
        print(f"平均價單日變化: {change:+,.2f}")


def save_results(df, output_path="data/taifex_20day_ma.csv"):
    """
    儲存結果到 CSV 檔案
    
    Args:
        df: DataFrame 計算結果
        output_path: 輸出檔案路徑
    """
    try:
        # 確保資料夾存在
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"已建立資料夾: {output_dir}")

        df_save = df.copy()
        df_save['date'] = df_save['date'].dt.strftime('%Y-%m-%d')
        df_save.to_csv(output_path, index=False, encoding='utf-8-sig') # 使用 utf-8-sig 讓 Excel 正確顯示中文
        print(f"\n結果已儲存到: {output_path}")
    except Exception as e:
        print(f"儲存檔案失敗: {e}")


def main():
    """
    主程式
    """
    print("台指期 20 日平均收盤價計算程式")
    print("-" * 70)
    
    # 1. 嘗試從 TAIFEX API 取得資料
    df = fetch_taifex_futures_data(product_id='TX', days=60)
    
    # 2. 如果 API 失敗或無資料，使用範例資料
    if df is None or len(df) == 0:
        print("\nAPI 無法取得資料，將使用範例資料進行演示...")
        df = create_sample_data(days=60)
    
    if df is None:
        print("\n錯誤：無法取得任何資料。")
        return
    
    # 3. 確保有 close 欄位
    if 'close' not in df.columns:
        print("錯誤：資料缺少 'close' (收盤價) 欄位。")
        return
    
    # 4. 計算 20 日移動平均
    result_df = calculate_20day_ma(df)
    
    if result_df is not None:
        # 5. 顯示結果
        display_results(result_df)
        
        # 6. 儲存結果
        save_results(result_df)


if __name__ == "__main__":
    main()
