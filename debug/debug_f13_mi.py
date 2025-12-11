"""Debug script for F13 TWSE MI_INDEX checks"""

from datetime import datetime

import requests

URL = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX"
TARGET_FIELDS = ["發行量加權股價指數", "TAIEX"]


def main(date: str) -> None:
    params = {"response": "json", "type": "IND", "date": date.replace("-", "")}
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; F13 Debug)"
    }

    print(f"Querying {date} -> {URL} ...")
    response = requests.get(URL, params=params, headers=headers, timeout=20)
    response.raise_for_status()
    payload = response.json()

    print("stat:", payload.get("stat"))
    print("date:", payload.get("date"))

    tables = payload.get("tables") or []
    print("tables:", len(tables))
    for idx, table in enumerate(tables):
        print(f"[Table {idx}] title: {table.get('title')}" )
        fields = table.get("fields") or []
        print(" fields:", fields)
        for row in (table.get("data") or [])[:3]:
            if any(keyword in str(row) for keyword in TARGET_FIELDS):
                print(" target row:", row)
        print("  total rows:", len(table.get("data") or []))


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else datetime.today().strftime("%Y-%m-%d")
    main(target)