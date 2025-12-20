"""
台指期預測儀表板生成程式
自動讀取因子數據，生成預測分析並更新 README.md

開發日期: 2025-12-19
版本: 1.0
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from glob import glob


# ========== Phase 1: 資料讀取與解析模組 ==========

def load_latest_factors(data_dir: str = "data") -> Dict:
    """
    從 data/ 目錄讀取最新的因子數據

    Returns:
        dict: {
            "F01": {"value": -28731, "status": "success", "raw": "...", "date": "2025.12.18"},
            "F21": {"value": 23006.36, "change": 313.04, "pct": 1.38, "status": "success", ...},
            ...
        }
    """
    factors = {}

    # 定義所有因子
    all_factors = [
        "F01", "F02", "F03", "F04", "F05", "F06", "F07",
        "F11", "F12", "F13", "F14", "F15", "F16", "F17",
        "F21", "F22", "F23", "F24", "F25"
    ]

    for factor_code in all_factors:
        # 找到該因子的所有檔案（可能有多個日期）
        pattern = os.path.join(data_dir, f"*_{factor_code.lower()}_fetcher.txt")
        files = glob(pattern)

        if not files:
            factors[factor_code] = {"status": "missing", "error": "檔案不存在"}
            continue

        # 取最新的檔案（按檔名排序，因為檔名包含日期時間）
        latest_file = sorted(files)[-1]

        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            # 解析因子數據
            parsed = parse_factor_data(content, factor_code)
            factors[factor_code] = parsed

        except Exception as e:
            factors[factor_code] = {"status": "error", "error": str(e)}

    return factors


def parse_factor_data(text: str, factor_code: str) -> Dict:
    """
    解析因子數據文字

    支援格式：
    1. "2025.12.18  F01: ... : -28,731 口"  → 提取數值
    2. "2025.12.19  F21: ... : 23,006.36 (漲跌 +313.04, +1.38%)"  → 提取價格、漲跌、百分比
    3. "F01 錯誤: ..."  → 標記為失敗
    """
    # 檢查是否為錯誤訊息
    if "錯誤" in text or "失敗" in text or "error" in text.lower():
        return {"status": "failed", "error": text[:100], "raw": text}

    # 提取日期
    date_match = re.search(r'(\d{4}\.\d{2}\.\d{2})', text)
    date = date_match.group(1) if date_match else "unknown"

    # 格式 B: 完整數據（F21-F25 國際市場）
    # 範例: "2025.12.19  F21: NASDAQ指數 : 23,006.36 (漲跌 +313.04, +1.38%)"
    if "漲跌" in text and "%" in text:
        try:
            # 提取主要數值（價格）
            value_match = re.search(r':\s*([-+]?[\d,]+\.?\d*)\s*\(', text)
            if not value_match:
                return {"status": "failed", "error": "無法解析數值", "raw": text}

            value_str = value_match.group(1).replace(',', '')
            value = float(value_str)

            # 提取漲跌
            change_match = re.search(r'漲跌\s*([-+]?[\d,]+\.?\d*)', text)
            change = float(change_match.group(1).replace(',', '')) if change_match else 0

            # 提取漲跌幅
            pct_match = re.search(r'([-+]?[\d,]+\.?\d*)%', text)
            pct = float(pct_match.group(1).replace(',', '')) if pct_match else 0

            return {
                "status": "success",
                "date": date,
                "value": value,
                "change": change,
                "pct": pct,
                "raw": text
            }
        except Exception as e:
            return {"status": "failed", "error": f"解析錯誤: {e}", "raw": text}

    # 格式 A: 簡單數值（F01-F17 早盤資料）
    # 範例: "2025.12.18  F01: 台指期貨外資 [未平倉] [多空淨額] : -28,731 口"
    # 範例: "2025.12.19  F11: 加權股價指數收盤 : 27,696.35  [https://...]"
    else:
        try:
            # 找最後一個冒號後的數值（但在 URL 之前）
            # 先移除 URL 部分
            text_without_url = re.sub(r'\[https?://[^\]]*\]', '', text)

            parts = text_without_url.split(':')
            if len(parts) < 2:
                return {"status": "failed", "error": "無法找到數值", "raw": text}

            # 取最後一部分，移除單位（口、元、張等）
            value_part = parts[-1].strip()
            value_part = value_part.split()[0]  # 取第一個數字部分

            # 移除逗號、百分比符號並轉換
            value_str = value_part.replace(',', '').replace('%', '')
            value = float(value_str)

            return {
                "status": "success",
                "date": date,
                "value": value,
                "raw": text
            }
        except Exception as e:
            return {"status": "failed", "error": f"解析錯誤: {e}", "raw": text}


# ========== Phase 2: 預測邏輯計算 ==========

def predict_opening(factors: Dict) -> Dict:
    """
    預測開盤方向與幅度

    權重：夜盤收盤 90% + 籌碼 10%

    主要依據：
    - F25 (台指期盤後): 漲跌點數 × 0.9
    - F21-F24 (國際市場): 綜合評分 × 0.05
    - F01 (外資籌碼): 壓力評估 × 0.05

    Returns:
        {
            "direction": "高開" / "平開" / "低開",
            "range": (50, 100),  # 點數範圍
            "confidence": 4,  # 1-5 星
            "signals": ["夜盤 +217 點", "美股科技股強勢"],
            "risks": ["外資空單壓力 -28,731 口"],
            "missing_factors": ["F25"],  # 缺失的因子
            "contributions": [("F25", 90), ("F22", 5), ("F01", 5)]  # 貢獻度排序
        }
    """
    score = 50  # 基準分數 (0-100)
    signals = []
    risks = []
    missing_factors = []
    contributions = []  # (因子名稱, 權重百分比, 訊號文字)

    # F25 貢獻 (90%) - 台指期盤後
    if factors.get("F25", {}).get("status") == "success":
        f25_change = factors["F25"]["change"]
        f25_value = factors["F25"]["value"]
        score += f25_change * 0.15  # 放大因子

        if f25_change > 0:
            signal_text = f"夜盤收高 +{f25_change:.0f} 點，動能延續"
            signals.append(signal_text)
            contributions.append(("夜盤收盤", 90, signal_text))
        else:
            risk_text = f"夜盤收低 {f25_change:.0f} 點，開盤承壓"
            risks.append(risk_text)
            contributions.append(("夜盤收盤", 90, risk_text))
    else:
        missing_factors.append("F25")
        score -= 10  # 缺少關鍵因子，降低信心

    # 國際市場貢獻 (5%) - F21, F22, F24
    us_score = calculate_us_market_score(factors)
    score += us_score

    if us_score > 3:
        signal_text = f"美股科技股強勢（費半 {factors.get('F22', {}).get('pct', 0):+.2f}%）"
        signals.append(signal_text)
        contributions.append(("美股市場", 5, signal_text))
    elif us_score < -3:
        risk_text = f"美股科技股走弱（費半 {factors.get('F22', {}).get('pct', 0):+.2f}%）"
        risks.append(risk_text)
        contributions.append(("美股市場", 5, risk_text))

    # 籌碼壓力 (5%) - F01
    if factors.get("F01", {}).get("status") == "success":
        f01_value = factors["F01"]["value"]
        if f01_value < -25000:
            score -= 5
            risk_text = f"外資空單壓力大 ({f01_value:,.0f} 口)"
            risks.append(risk_text)
            contributions.append(("外資籌碼", 5, risk_text))
        elif f01_value > 25000:
            score += 5
            signal_text = f"外資多單支撐 ({f01_value:,.0f} 口)"
            signals.append(signal_text)
            contributions.append(("外資籌碼", 5, signal_text))
    else:
        missing_factors.append("F01")

    # 判斷方向與幅度
    if score > 65:
        direction = "高開"
        range_points = (100, 200)
        confidence = 4
    elif score > 55:
        direction = "小幅高開"
        range_points = (50, 100)
        confidence = 3
    elif score > 48:
        direction = "平開"
        range_points = (-20, 20)
        confidence = 3
    elif score > 40:
        direction = "小幅低開"
        range_points = (-100, -50)
        confidence = 3
    else:
        direction = "低開"
        range_points = (-200, -100)
        confidence = 4

    # 如果缺失關鍵因子，降低信心度
    if missing_factors:
        confidence = max(1, confidence - len(missing_factors))

    # 按權重排序貢獻度
    contributions.sort(key=lambda x: x[1], reverse=True)

    return {
        "direction": direction,
        "range": range_points,
        "confidence": confidence,
        "signals": signals,
        "risks": risks,
        "missing_factors": missing_factors,
        "score": score,
        "contributions": contributions
    }


def calculate_us_market_score(factors: Dict) -> float:
    """計算美股市場綜合評分 (-10 to +10)"""
    score = 0

    # F21: NASDAQ
    if factors.get("F21", {}).get("status") == "success":
        nasdaq_pct = factors["F21"]["pct"]
        score += nasdaq_pct * 2  # 權重 2

    # F22: 費城半導體（最重要）
    if factors.get("F22", {}).get("status") == "success":
        semi_pct = factors["F22"]["pct"]
        score += semi_pct * 3  # 權重 3

    # F24: 台積電 ADR
    if factors.get("F24", {}).get("status") == "success":
        tsm_pct = factors["F24"]["pct"]
        score += tsm_pct * 2  # 權重 2

    return score / 7  # 標準化


def predict_intraday(factors: Dict) -> Dict:
    """
    預測盤中走勢

    權重：籌碼 70% + 技術指標 30%

    主要依據：
    - F01 (外資淨OI): 壓力評估 × 0.5
    - F17 (外資買超): 資金動向 × 0.2
    - F06 (VIX): 波動度 × 0.1
    - F11-F16: 技術面 × 0.2

    Returns:
        {
            "trend": "震盪偏多" / "高檔震盪" / "偏空",
            "key_level": 27700,  # 關鍵價位
            "confidence": 3,
            "signals": [...],
            "risks": [...],
            "contributions": [("F01", 35), ("F17", 35), ("F06", 10)]
        }
    """
    score = 50
    signals = []
    risks = []
    missing_factors = []
    contributions = []  # (因子名稱, 權重百分比, 訊號文字)

    # F01: 外資未平倉淨額 (35%)
    if factors.get("F01", {}).get("status") == "success":
        f01_value = factors["F01"]["value"]
        if f01_value > 30000:
            score += 15
            signal_text = f"外資大量做多 ({f01_value:,.0f} 口)"
            signals.append(signal_text)
            contributions.append(("外資未平倉", 35, signal_text))
        elif f01_value > 10000:
            score += 8
            signal_text = f"外資偏多 ({f01_value:,.0f} 口)"
            signals.append(signal_text)
            contributions.append(("外資未平倉", 35, signal_text))
        elif f01_value < -30000:
            score -= 15
            risk_text = f"外資大量做空 ({f01_value:,.0f} 口)"
            risks.append(risk_text)
            contributions.append(("外資未平倉", 35, risk_text))
        elif f01_value < -10000:
            score -= 8
            risk_text = f"外資偏空 ({f01_value:,.0f} 口)"
            risks.append(risk_text)
            contributions.append(("外資未平倉", 35, risk_text))
    else:
        missing_factors.append("F01")

    # F17: 外資買超金額 (35%)
    if factors.get("F17", {}).get("status") == "success":
        f17_value = factors["F17"]["value"]
        if f17_value > 100:
            score += 15
            signal_text = f"外資現貨大買 ({f17_value:,.0f} 億)"
            signals.append(signal_text)
            contributions.append(("外資買超", 35, signal_text))
        elif f17_value > 30:
            score += 8
            signal_text = f"外資現貨買超 ({f17_value:,.0f} 億)"
            signals.append(signal_text)
            contributions.append(("外資買超", 35, signal_text))
        elif f17_value < -100:
            score -= 15
            risk_text = f"外資現貨大賣 ({f17_value:,.0f} 億)"
            risks.append(risk_text)
            contributions.append(("外資買超", 35, risk_text))
        elif f17_value < -30:
            score -= 8
            risk_text = f"外資現貨賣超 ({f17_value:,.0f} 億)"
            risks.append(risk_text)
            contributions.append(("外資買超", 35, risk_text))
    else:
        missing_factors.append("F17")

    # F06: VIX 波動率 (10%)
    if factors.get("F06", {}).get("status") == "success":
        vix = factors["F06"]["value"]
        if vix > 25:
            score -= 5
            risk_text = f"VIX 高檔 {vix:.2f}，市場不安"
            risks.append(risk_text)
            contributions.append(("VIX波動率", 10, risk_text))
        elif vix < 15:
            score += 3
            signal_text = f"VIX 低檔 {vix:.2f}，市場穩定"
            signals.append(signal_text)
            contributions.append(("VIX波動率", 10, signal_text))

    # F04: 前日收盤價，計算關鍵價位
    key_level = 27700  # 預設值
    if factors.get("F04", {}).get("status") == "success":
        prev_close = factors["F04"]["value"]
        key_level = round(prev_close / 100) * 100  # 整百

    # 判斷趨勢
    if score > 65:
        trend = "強勢偏多"
        confidence = 4
    elif score > 55:
        trend = "震盪偏多"
        confidence = 3
    elif score > 45:
        trend = "高檔震盪"
        confidence = 3
    elif score > 35:
        trend = "震盪偏空"
        confidence = 3
    else:
        trend = "弱勢偏空"
        confidence = 4

    if missing_factors:
        confidence = max(1, confidence - len(missing_factors))

    # 按權重排序貢獻度
    contributions.sort(key=lambda x: x[1], reverse=True)

    return {
        "trend": trend,
        "key_level": key_level,
        "confidence": confidence,
        "signals": signals,
        "risks": risks,
        "missing_factors": missing_factors,
        "score": score,
        "contributions": contributions
    }


# ========== Phase 3: README 生成 ==========

def generate_readme(factors: Dict, opening_pred: Dict, intraday_pred: Dict) -> str:
    """生成 README.md 內容"""

    # 計算資料品質
    total_factors = len(factors)
    success_factors = sum(1 for f in factors.values() if f.get("status") == "success")
    failed_factors = [k for k, v in factors.items() if v.get("status") != "success"]

    # 市場訊號燈
    signal_lights = generate_signal_lights(opening_pred["score"], intraday_pred["score"])

    # 開盤預測價位
    f04_close = factors.get("F04", {}).get("value", 27600)
    open_low = f04_close + opening_pred["range"][0]
    open_high = f04_close + opening_pred["range"][1]

    # 信心度星星
    opening_stars = "⭐" * opening_pred["confidence"] + "☆" * (5 - opening_pred["confidence"])
    intraday_stars = "⭐" * intraday_pred["confidence"] + "☆" * (5 - intraday_pred["confidence"])

    # 取得更新時間
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 判斷是早盤還是夜盤資料
    has_night_data = factors.get("F25", {}).get("status") == "success"
    data_type = "早盤+夜盤數據" if has_night_data else "早盤數據"

    # 計算交易日
    from datetime import timedelta
    today = datetime.now()
    # 取得資料中的日期（從 F04 或其他因子）
    data_date_str = factors.get("F04", {}).get("date", today.strftime("%Y.%m.%d"))
    data_date = datetime.strptime(data_date_str, "%Y.%m.%d")

    # 預測的是下一個交易日
    next_trading_day = data_date + timedelta(days=1)
    # 如果是週六，往後推2天
    if next_trading_day.weekday() == 5:  # Saturday
        next_trading_day += timedelta(days=2)
    # 如果是週日，往後推1天
    elif next_trading_day.weekday() == 6:  # Sunday
        next_trading_day += timedelta(days=1)

    next_next_trading_day = next_trading_day + timedelta(days=1)
    # 處理下下個交易日的週末
    if next_next_trading_day.weekday() == 5:
        next_next_trading_day += timedelta(days=2)
    elif next_next_trading_day.weekday() == 6:
        next_next_trading_day += timedelta(days=1)

    readme = f"""# 台指期預測系統

*最後更新: {update_time} ({data_type})*
*本儀表板僅供參考，不構成投資建議*

## 🎯 台股指數近日 開盤預測分析
相關資料　交易日(day N  ): {data_date.strftime("%Y.%m.%d")}
預測下一個交易日(day N+1): {next_trading_day.strftime("%Y.%m.%d")}

### 📊 市場訊號燈
{signal_lights}

### 🔮 08:45 開盤預測
- **方向**: {get_direction_emoji(opening_pred["direction"])} {opening_pred["direction"]}
- **幅度**: {opening_pred["range"][0]:+.0f} ~ {opening_pred["range"][1]:+.0f} 點 ({open_low:,.0f} ~ {open_high:,.0f})
- **信心度**: {opening_stars} ({opening_pred["confidence"] * 20}%)

### 📈 盤中趨勢預測
- **走勢**: {intraday_pred["trend"]}
- **關鍵價位**: {intraday_pred["key_level"]:,.0f}
- **信心度**: {intraday_stars} ({intraday_pred["confidence"] * 20}%)

### 💡 依據與風險

✅ **多方因素**:
"""

    # 合併開盤和盤中的貢獻度，並按權重排序（只保留多方）
    all_contributions = opening_pred.get("contributions", []) + intraday_pred.get("contributions", [])

    # 分離多方和空方因素
    bullish_contributions = []
    bearish_contributions = []

    for name, weight, text in all_contributions:
        # 判斷是多方還是空方（根據文字內容）
        if any(keyword in text for keyword in ["收高", "強勢", "做多", "買", "支撐", "穩定", "偏多"]):
            bullish_contributions.append((name, weight, text))
        else:
            bearish_contributions.append((name, weight, text))

    # 按權重排序，取前3名
    bullish_contributions.sort(key=lambda x: x[1], reverse=True)
    bearish_contributions.sort(key=lambda x: x[1], reverse=True)

    # 添加多方訊號（帶百分比）
    if bullish_contributions:
        for name, weight, text in bullish_contributions[:3]:  # 只顯示前3名
            readme += f"- {text} 【{weight}%】\n"
    else:
        readme += "- （暫無明顯多方訊號）\n"

    readme += "\n⚠️ **空方風險**:\n"

    # 添加風險因素（帶百分比）
    if bearish_contributions:
        for name, weight, text in bearish_contributions[:3]:  # 只顯示前3名
            readme += f"- {text} 【{weight}%】\n"
    else:
        readme += "- （暫無明顯風險因素）\n"

    # 缺失因子警告
    all_missing = list(set(opening_pred["missing_factors"] + intraday_pred["missing_factors"]))
    if all_missing:
        readme += f"\n⚠️ **資料缺失**: {', '.join(all_missing)}\n"

    readme += """
---

## 📊 因子數據總覽

### 🌍 國際市場指標
| 因子 | 數值 | 漲跌 | 狀態 |
|------|------|------|------|
"""

    # F21-F25 國際市場
    for code in ["F21", "F22", "F23", "F24", "F25"]:
        f = factors.get(code, {})
        if f.get("status") == "success":
            name = get_factor_name(code)
            value = f.get("value", 0)
            change = f.get("change", 0)
            pct = f.get("pct", 0)
            status_emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
            readme += f"| {code} {name} | {value:,.2f} | {change:+,.2f} ({pct:+.2f}%) | {status_emoji} |\n"
        else:
            name = get_factor_name(code)
            readme += f"| {code} {name} | - | - | ❌ |\n"

    readme += """
### 💼 法人籌碼動向
| 因子 | 數值 | 判讀 |
|------|------|------|
"""

    # F01-F03, F17 籌碼
    for code in ["F01", "F02", "F03", "F17"]:
        f = factors.get(code, {})
        if f.get("status") == "success":
            name = get_factor_name(code)
            value = f.get("value", 0)
            interpretation = interpret_value(code, value)
            # F17 是億元，保留2位小數；其他是口數，無小數
            if code == "F17":
                value_str = f"{value:,.2f} 億"
            else:
                value_str = f"{value:,.0f} 口"
            readme += f"| {code} {name} | {value_str} | {interpretation} |\n"
        else:
            name = get_factor_name(code)
            readme += f"| {code} {name} | - | ❌ 資料缺失 |\n"

    readme += """
### 📈 技術指標
| 因子 | 數值 | 說明 |
|------|------|------|
"""

    # F04-F07, F11-F16 技術指標
    for code in ["F04", "F06", "F07", "F11", "F13", "F14"]:
        f = factors.get(code, {})
        if f.get("status") == "success":
            name = get_factor_name(code)
            value = f.get("value", 0)
            unit = get_unit(code)
            readme += f"| {code} {name} | {value:,.2f} {unit} | |\n"
        else:
            name = get_factor_name(code)
            readme += f"| {code} {name} | - | ❌ |\n"

    readme += f"""
### 📌 數據品質
✅ 成功: {success_factors}/{total_factors} 因子 | ⚠️ 失敗: {len(failed_factors)} {f'({", ".join(failed_factors)})' if failed_factors else ''}
"""

    return readme


def generate_signal_lights(opening_score: float, intraday_score: float) -> str:
    """生成市場訊號燈"""
    avg_score = (opening_score + intraday_score) / 2

    if avg_score > 65:
        lights = "🟢🟢🟢🟢🟢"
        msg = "強勢多頭格局"
    elif avg_score > 55:
        lights = "🟢🟢🟢🟢⚪"
        msg = "偏多格局"
    elif avg_score > 48:
        lights = "🟢🟢🟡⚪⚪"
        msg = "震盪整理"
    elif avg_score > 40:
        lights = "🟡⚪⚪🔴🔴"
        msg = "偏空格局"
    else:
        lights = "⚪🔴🔴🔴🔴"
        msg = "弱勢空頭"

    return f"{lights}  **{msg}**"


def get_direction_emoji(direction: str) -> str:
    """取得方向對應的 emoji"""
    if "高開" in direction:
        return "📈"
    elif "低開" in direction:
        return "📉"
    else:
        return "➡️"


def get_factor_name(code: str) -> str:
    """取得因子名稱"""
    names = {
        "F01": "外資淨OI", "F02": "外資多單", "F03": "外資空單",
        "F04": "台指期收盤", "F05": "TXO成交量", "F06": "VIX", "F07": "PC Ratio",
        "F11": "加權指數", "F12": "成交金額", "F13": "與20MA距離",
        "F14": "台積電價", "F15": "台積電漲跌", "F16": "台積電量", "F17": "外資買超",
        "F21": "NASDAQ", "F22": "費半", "F23": "小那期", "F24": "TSM ADR", "F25": "台指期盤後"
    }
    return names.get(code, code)


def get_unit(code: str) -> str:
    """取得單位"""
    if code in ["F01", "F02", "F03", "F05", "F16"]:
        return "口/張"
    elif code in ["F12", "F17"]:
        return "億"
    elif code in ["F06", "F07"]:
        return "%"
    elif code in ["F04", "F11", "F13", "F14", "F15"]:
        return "點/元"
    else:
        return ""


def interpret_value(code: str, value: float) -> str:
    """判讀數值"""
    if code == "F01":
        if value > 30000:
            return "🟢 大量做多"
        elif value > 10000:
            return "🟢 偏多"
        elif value < -30000:
            return "🔴 大量做空"
        elif value < -10000:
            return "🔴 偏空"
        else:
            return "⚪ 中性"
    elif code == "F17":
        if value > 100:
            return "🟢 大買"
        elif value > 30:
            return "🟢 買超"
        elif value < -100:
            return "🔴 大賣"
        elif value < -30:
            return "🔴 賣超"
        else:
            return "⚪ 中性"
    else:
        return ""


# ========== Main Function ==========

def main():
    """主程式"""
    print("=" * 60)
    print("台指期預測儀表板生成程式")
    print("=" * 60)

    # Phase 1: 讀取因子數據
    print("\n[1/3] 讀取因子數據...")
    factors = load_latest_factors("data")

    success_count = sum(1 for f in factors.values() if f.get("status") == "success")
    print(f"[OK] 成功讀取 {success_count}/{len(factors)} 個因子")

    # 顯示失敗的因子
    failed = [k for k, v in factors.items() if v.get("status") != "success"]
    if failed:
        print(f"[WARN] 失敗因子: {', '.join(failed)}")

    # Phase 2: 生成預測
    print("\n[2/3] 計算預測分析...")
    opening_pred = predict_opening(factors)
    print(f"[PRED] 開盤預測: {opening_pred['direction']} ({opening_pred['range'][0]:+.0f}~{opening_pred['range'][1]:+.0f}點)")

    intraday_pred = predict_intraday(factors)
    print(f"[PRED] 盤中預測: {intraday_pred['trend']}")

    # Phase 3: 生成 README
    print("\n[3/3] 生成 README.md...")
    readme_content = generate_readme(factors, opening_pred, intraday_pred)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("[OK] README.md 已更新")
    print("\n" + "=" * 60)
    print("預測儀表板生成完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
