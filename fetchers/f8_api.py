# f2_api.py
import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List

import requests
import pandas as pd

# --- 路徑設定 ---
LOG_DIR = Path("logs/f2")
RAW_DIR = Path("raw/f2")
OUT_DIR = Path("data/f2")
for d in (LOG_DIR, RAW_DIR, OUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "f2_api.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# --- API 設定（請依實際 API 修改）---
F2_ENDPOINT = "https://www.taifex.com.tw/api/f2"  # ← 請替換為真實 API
DATE_PARAM = "date"
HEADERS = {
    "User-Agent": "DM-F2Fetcher/1.0",
    "Accept": "application/json, text/csv;q=0.9, */*;q=0.8",
}
DEFAULT_TIMEOUT = 15
RETRY = 3
BACKOFF = 2

# --- 工具函式 ---
def _normalize_date_str(date_str: str) -> str:
    dt = pd.to_datetime(date_str)
    return dt.strftime("%Y-%m-%d")

def _safe_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

# --- 抓取原始資料 ---
def fetch_f2_raw(date_str: str) -> Tuple[Optional[str], Dict[str, Any]]:
    date_norm = _normalize_date_str(date_str)
    params = {DATE_PARAM: date_norm}
    meta = {"endpoint": F2_ENDPOINT, "params": params, "headers": HEADERS, "retry": 0}
    last_err = None
    for i in range(1, RETRY + 1):
        try:
            meta["retry"] = i
            logging.info(f"[F2] GET {F2_ENDPOINT} params={params} retry={i}")
            resp = requests.get(F2_ENDPOINT, params=params, headers=HEADERS, timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()
            for enc in [resp.encoding, "utf-8", "big5", "cp950"]:
                try:
                    if enc:
                        resp.encoding = enc
                    text = resp.text
                    if text.strip():
                        _safe_write_text(RAW_DIR / f"f2_{date_norm}_retry{i}.txt", text)
                        _write_json(RAW_DIR / f"f2_{date_norm}_meta_retry{i}.json", meta)
                        return text, meta
                except Exception as e:
                    last_err = e
                    logging.warning(f"[F2] decode failed with {enc}: {e}")
        except Exception as e:
            last_err = e
            logging.error(f"[F2] request error: {e}")
            time.sleep(BACKOFF * i)
    _write_json(RAW_DIR / f"f2_{date_norm}_meta_failed.json", meta)
    return None, meta

# --- 解析資料 ---
def parse_f2(text: str) -> pd.DataFrame:
    text_strip = text.strip()
    try:
        if text_strip.startswith("{") or text_strip.startswith("["):
            data = json.loads(text_strip)
            df = pd.json_normalize(data)
            logging.info(f"[F2] parsed as JSON rows={len(df)}")
            return df
    except Exception as e:
        logging.warning(f"[F2] JSON parse failed: {e}")
    try:
        from io import StringIO
        df = pd.read_csv(StringIO(text_strip))
        logging.info(f"[F2] parsed as CSV rows={len(df)}")
        return df
    except Exception as e:
        logging.warning(f"[F2] CSV parse failed: {e}")
    try:
        dfs = pd.read_html(text_strip)
        df = dfs[0]
        logging.info(f"[F2] parsed as HTML rows={len(df)}")
        return df
    except Exception as e:
        logging.error(f"[F2] HTML parse failed: {e}")
        raise ValueError("F2 parse failed: unknown format")

# --- 驗證資料 ---
def validate_f2(df: pd.DataFrame, date_str: str) -> List[str]:
    warnings = []
    date_norm = _normalize_date_str(date_str)
    required_cols = ["date", "instrument", "foreign_net_position"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        warnings.append(f"missing_cols={missing}")
    if "date" in df.columns:
        if date_norm not in set(pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")):
            warnings.append(f"date_mismatch target={date_norm}")
    def _to_num(x):
        s = str(x).strip().replace(",", "")
        if s.startswith("(") and s.endswith(")"):
            s = "-" + s[1:-1]
        try:
            return float(s)
        except:
            return None
    if "foreign_net_position" in df.columns:
        vals = df["foreign_net_position"].map(_to_num)
        if vals.isna().sum() > 0:
            warnings.append("foreign_net_position_invalid")
        elif (vals.abs() > 2_000_000).any():
            warnings.append("foreign_net_position_outlier")
    if len(df) == 0:
        warnings.append("empty_df")
    if "date" in df.columns and "instrument" in df.columns:
        if df.duplicated(subset=["date", "instrument"]).any():
            warnings.append("duplicates_detected")
    return warnings

# --- 主流程 ---
def get_f2(date_str: str) -> Dict[str, Any]:
    raw, meta = fetch_f2_raw(date_str)
    if raw is None:
        return {"ok": False, "error": "fetch_failed", "meta": meta}
    try:
        df = parse_f2(raw)
    except Exception as e:
        return {"ok": False, "error": f"parse_error:{e}", "meta": meta}
    warns = validate_f2(df, date_str)
    date_norm = _normalize_date_str(date_str)
    out_csv = OUT_DIR / f"f2_{date_norm}.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    if warns:
        _write_json(OUT_DIR / f"f2_{date_norm}_warnings.json", {"warnings": warns, "meta": meta})
        logging.warning(f"[F2] warnings: {warns}")
    else:
        logging.info("[F2] validation passed")
    return {"ok": True, "warnings": warns, "rows": len(df), "meta": meta, "out": str(out_csv)}

# --- 測試執行 ---
if __name__ == "__main__":
    result = get_f2("2025-11-27")
    print(result)





