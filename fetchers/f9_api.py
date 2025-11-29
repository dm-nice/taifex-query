# f9_api.py
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
import json

# --- 路徑設定 ---
LOG_DIR = Path("logs/f9")
RAW_DIR = Path("raw/f9")
OUT_DIR = Path("data/f9")
for d in (LOG_DIR, RAW_DIR, OUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "f9_api.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# --- API URL ---
F9_URL = "https://www.taifex.com.tw/cht/3/pcRatio"

def fetch_f9_raw() -> str:
    logging.info(f"[F9] GET {F9_URL}")
    resp = requests.get(F9_URL, timeout=15)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    raw_html = resp.text
    (RAW_DIR / f"f9_raw_{datetime.today().strftime('%Y%m%d')}.html").write_text(raw_html, encoding="utf-8")
    return raw_html

def parse_f9(raw_html: str) -> pd.DataFrame:
    dfs = pd.read_html(raw_html)
    df = dfs[0]  # 第一個表格就是 P/C Ratio
    df.columns = ["日期","賣權成交量","買權成交量","成交量比率%","賣權未平倉量","買權未平倉量","未平倉比率%"]
    df["日期"] = pd.to_datetime(df["日期"], format="%Y/%m/%d")
    df["未平倉比率%"] = pd.to_numeric(df["未平倉比率%"], errors="coerce")
    # 只取最新一筆
    df = df.head(1)
    return df

def get_f9() -> dict:
    raw = fetch_f9_raw()
    df = parse_f9(raw)
    date_str = datetime.today().strftime("%Y-%m-%d")
    out_csv = OUT_DIR / f"f9_pcRatio_{date_str}.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    logging.info(f"[F9] saved {out_csv}")
    return {"ok": True, "rows": len(df), "out": str(out_csv)}

if __name__ == "__main__":
    result = get_f9()
    print(result)