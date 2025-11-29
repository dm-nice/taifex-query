# f10_fetcher.py
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple

import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

# ---- 路徑設定 ----
LOG_DIR = Path("logs/f10")
RAW_DIR = Path("raw/f10")
OUT_DIR = Path("data/f10")
for d in (LOG_DIR, RAW_DIR, OUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "f10_fetcher.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

F10_URL = "https://www.taifex.com.tw/cht/3/optDailyMarketSummary"

def normalize_date(date_str: Optional[str]) -> str:
    if not date_str:
        return datetime.today().strftime("%Y/%m/%d")
    dt = pd.to_datetime(date_str)
    return dt.strftime("%Y/%m/%d")

def list_all_selects(page) -> List[Tuple[str, str]]:
    """列出頁面上所有 select 的 (value,label) 供 debug。"""
    try:
        selects = page.eval_on_selector_all(
            "select",
            "sels => sels.map(sel => Array.from(sel.querySelectorAll('option')).map(o => [o.value, o.textContent.trim()]))"
        )
        options = []
        for idx, opts in enumerate(selects):
            logging.info(f"[F10][DEBUG] 第 {idx+1} 個 <select> 有 {len(opts)} 個 option")
            for v, l in opts:
                logging.info(f"[F10][DEBUG]  option value='{v}' label='{l}'")
                options.append((v, l))
        return options
    except Exception as e:
        logging.warning(f"[F10][DEBUG] 列出 select 失敗：{e}")
        return []

def set_select_value_js(page, prefer_value="TXO") -> bool:
    """用 JS 在所有 select 中尋找匹配 TXO 的 option，設定 value 並觸發 change。"""
    js = """
    (prefer) => {
      const sels = Array.from(document.querySelectorAll('select'));
      for (const sel of sels) {
        const opts = Array.from(sel.querySelectorAll('option'));
        // 先用 value 精準選
        for (const o of opts) {
          if (o.value.trim() === prefer) {
            sel.value = o.value;
            sel.dispatchEvent(new Event('change', {bubbles: true}));
            return true;
          }
        }
        // 再用 label 包含字串
        for (const o of opts) {
          const label = (o.textContent || '').trim();
          if (label.includes('TXO') || label.includes('臺指選擇權') || label.includes('台指選擇權')) {
            sel.value = o.value;
            sel.dispatchEvent(new Event('change', {bubbles: true}));
            return true;
          }
        }
      }
      return false;
    }
    """
    try:
        ok = page.evaluate(js, prefer_value)
        logging.info(f"[F10] JS 設定 select 值結果：{ok}")
        return bool(ok)
    except Exception as e:
        logging.warning(f"[F10] JS 設定 select 值失敗：{e}")
        return False

def fill_query_date(page, query_date: str) -> bool:
    inputs = ["input#queryDate", "input[name='queryDate']",
              "input#date", "input[name='date']"]
    for sel in inputs:
        try:
            page.wait_for_selector(sel, timeout=8000)
            page.fill(sel, "")
            page.fill(sel, query_date)
            logging.info(f"[F10] 日期填入成功：{sel} = {query_date}")
            return True
        except Exception:
            continue
    logging.warning("[F10][DEBUG] 找不到日期輸入欄位；嘗試用鍵盤操作")
    try:
        # 備援：嘗試把焦點移到可能的日期欄位並輸入
        page.keyboard.type(query_date)
        return True
    except Exception:
        return False

def click_query(page) -> bool:
    buttons = ["#queryBtn", "button#queryBtn", "button:has-text('查詢')", "text=查詢"]
    for sel in buttons:
        try:
            page.wait_for_selector(sel, timeout=8000)
            page.click(sel)
            logging.info(f"[F10] 查詢按鈕點擊成功：{sel}")
            return True
        except Exception:
            continue
    logging.warning("[F10][DEBUG] 查詢按鈕未找到，改用按 Enter")
    try:
        page.keyboard.press("Enter")
        return True
    except Exception:
        return False

def wait_for_table(page, timeout_ms: int) -> bool:
    for sel in ["table", "table.table", ".table-responsive table"]:
        try:
            page.wait_for_selector(sel, timeout=timeout_ms)
            logging.info(f"[F10] 表格載入成功：{sel}")
            return True
        except PWTimeoutError:
            continue
    logging.warning("[F10][DEBUG] 表格未在期限內載入")
    return False

def sum_total_volume_from_html(html: str) -> int:
    dfs = pd.read_html(html)
    target = None
    for df in dfs:
        cols = [str(c).strip() for c in df.columns]
        if "成交量" in cols or "成交量(口)" in cols or "Volume" in cols:
            target = df
            break
    if target is None:
        raise ValueError("未找到包含「成交量」欄位的表格")
    target.columns = [str(c).strip() for c in target.columns]
    vol_col = None
    for cand in ["成交量", "成交量(口)", "Volume"]:
        if cand in target.columns:
            vol_col = cand
            break
    if vol_col is None:
        raise ValueError("表格中沒有可辨識的成交量欄位")
    ser = target[vol_col].astype(str).str.replace(",", "").str.strip()
    ser = pd.to_numeric(ser, errors="coerce")
    return int(ser.fillna(0).sum())

def fetch_f10_txo_total(date_str: Optional[str] = None, headless: bool = True, timeout_ms: int = 25000, debug: bool = True) -> dict:
    query_date = normalize_date(date_str)
    logging.info(f"[F10] 開始抓取 TXO 成交量 | 日期={query_date}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        try:
            page.goto(F10_URL, timeout=timeout_ms)
            page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)

            # 初始快照（debug）
            if debug:
                html0 = page.content()
                (RAW_DIR / f"f10_init_{query_date.replace('/','-')}.html").write_text(html0, encoding="utf-8")
                try:
                    page.screenshot(path=str(RAW_DIR / f"f10_init_{query_date.replace('/','-')}.png"))
                except Exception:
                    pass
                list_all_selects(page)

            # 試圖設定 TXO；若找不到任何 select，略過商品選擇
            set_ok = set_select_value_js(page, prefer_value="TXO")
            if not set_ok:
                logging.warning("[F10][DEBUG] 未能設定 TXO；可能預設已是 TXO，先繼續填日期")

            # 填日期
            if not fill_query_date(page, query_date):
                raise RuntimeError("無法填入日期，請檢查日期輸入欄位 DOM")

            # 送出查詢
            if not click_query(page):
                raise RuntimeError("查詢動作失敗，請檢查按鈕 DOM")

            # 等待表格與網路閒置
            ok_table = wait_for_table(page, timeout_ms=timeout_ms)
            page.wait_for_load_state("networkidle", timeout=timeout_ms)

            # 查詢後快照（debug）
            html = page.content()
            (RAW_DIR / f"f10_txo_{query_date.replace('/','-')}.html").write_text(html, encoding="utf-8")
            if debug:
                try:
                    page.screenshot(path=str(RAW_DIR / f"f10_after_{query_date.replace('/','-')}.png"))
                except Exception:
                    pass

            # 解析與加總成交量
            total = sum_total_volume_from_html(html)

            # 存檔（CSV 與 TXT）
            date_for_file = query_date.replace("/", "-")
            out_csv = OUT_DIR / f"f10_totalVolume_{date_for_file}.csv"
            out_txt = OUT_DIR / f"f10_totalVolume_{date_for_file}.txt"

            df = pd.DataFrame([{"日期": query_date, "TXO_總成交量": total}])
            df.to_csv(out_csv, index=False, encoding="utf-8-sig")
            out_txt.write_text(f"{query_date}\t{total}\n", encoding="utf-8")

            logging.info(f"[F10] 成功 | 日期={query_date} | TXO_總成交量={total} | 檔案={out_csv.name}")
            return {"ok": True, "date": query_date, "total_volume": total, "out_csv": str(out_csv), "out_txt": str(out_txt)}
        except Exception as e:
            # 例外時輸出 debug 快照
            try:
                html_err = page.content()
                (RAW_DIR / f"f10_error_{query_date.replace('/','-')}.html").write_text(html_err, encoding="utf-8")
                page.screenshot(path=str(RAW_DIR / f"f10_error_{query_date.replace('/','-')}.png"))
            except Exception:
                pass
            logging.error(f"[F10] 失敗: {e}")
            return {"ok": False, "error": str(e)}
        finally:
            browser.close()

if __name__ == "__main__":
    # 用法：
    # python f10_fetcher.py                -> 預設今天日期
    # python f10_fetcher.py 2025-11-27     -> 指定日期
    # python f10_fetcher.py 20251127       -> 指定日期，無分隔符也可
    inp = sys.argv[1] if len(sys.argv) > 1 else None
    result = fetch_f10_txo_total(inp, headless=True, timeout_ms=30000, debug=True)
    print(result)