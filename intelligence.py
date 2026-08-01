from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _clip(value: float) -> int:
    return int(np.clip(round(value), 0, 100))


def trend_phase(
    close: pd.Series,
    ma20: pd.Series,
    ma50: pd.Series,
    ma100: pd.Series,
) -> tuple[str, int]:
    price = float(close.iloc[-1])
    p5 = float(close.iloc[-5])

    m20 = float(ma20.iloc[-1])
    m20_5 = float(ma20.iloc[-5])
    m50 = float(ma50.iloc[-1])
    m100 = float(ma100.iloc[-1])

    slope20 = ((m20 / m20_5) - 1) * 100 if m20_5 else 0

    if price > m20 > m50 > m100 and slope20 > 1:
        return "🚀 Güçleniyor", 95

    if price > m20 > m50 and p5 <= float(ma20.iloc[-5]):
        return "🌱 Başlıyor", 82

    if price > m20 > m50 and slope20 >= 0:
        return "🟢 Olgun yükseliş", 78

    if price > m50 and slope20 < 0:
        return "⚠️ Zayıflıyor", 52

    if price < m20 < m50:
        return "🔴 Trend bitti / düşüş", 18

    return "🟡 Kararsız", 42


def money_flow_trend(
    cmf: pd.Series,
    obv: pd.Series,
    adl: pd.Series,
    volume: pd.Series,
) -> tuple[str, int, dict[str, int]]:
    cmf_now = float(cmf.iloc[-1])
    cmf_change = float(cmf.iloc[-1] - cmf.iloc[-5])

    obv_base = max(abs(float(obv.iloc[-10])), 1)
    obv_change = ((float(obv.iloc[-1]) - float(obv.iloc[-10])) / obv_base) * 100

    adl_base = max(abs(float(adl.iloc[-10])), 1)
    adl_change = ((float(adl.iloc[-1]) - float(adl.iloc[-10])) / adl_base) * 100

    vol_5 = float(volume.tail(5).mean())
    vol_prev = float(volume.iloc[-10:-5].mean())
    vol_change = (vol_5 / vol_prev) if vol_prev > 0 else 1

    cmf_score = _clip(np.interp(cmf_now, [-0.2, 0, 0.2], [10, 55, 100]))
    obv_score = _clip(np.interp(obv_change, [-10, 0, 10], [15, 55, 100]))
    adl_score = _clip(np.interp(adl_change, [-10, 0, 10], [15, 55, 100]))
    volume_score = _clip(np.interp(vol_change, [0.7, 1.0, 1.5], [20, 55, 100]))

    total = _clip(
        cmf_score * 0.35
        + obv_score * 0.25
        + adl_score * 0.25
        + volume_score * 0.15
    )

    if total >= 75 and cmf_change > 0:
        label = "💰 Para girişi hızlanıyor"
    elif total >= 60:
        label = "🟢 Para akışı pozitif"
    elif total <= 35:
        label = "🔴 Para çıkışı belirgin"
    else:
        label = "🟡 Para akışı durağan"

    return label, total, {
        "CMF": cmf_score,
        "OBV": obv_score,
        "A/D": adl_score,
        "Hacim Devam": volume_score,
    }


def risk_breakdown(
    rsi_value: float,
    atr_pct: float,
    liquidity_score: int,
    distance_to_resistance: float,
    market_score: int,
) -> dict[str, int]:
    rsi_risk = _clip(np.interp(rsi_value, [55, 70, 80, 90], [5, 25, 70, 100]))
    volatility_risk = _clip(np.interp(atr_pct, [2, 4, 7, 12], [8, 25, 65, 100]))
    liquidity_risk = 100 - int(liquidity_score)

    if distance_to_resistance <= 0:
        resistance_risk = 75
    elif distance_to_resistance <= 2:
        resistance_risk = 55
    elif distance_to_resistance <= 5:
        resistance_risk = 25
    else:
        resistance_risk = 10

    market_risk = 100 - int(market_score)

    total = _clip(
        rsi_risk * 0.22
        + volatility_risk * 0.25
        + liquidity_risk * 0.23
        + resistance_risk * 0.15
        + market_risk * 0.15
    )

    return {
        "RSI Riski": rsi_risk,
        "Volatilite Riski": volatility_risk,
        "Likidite Riski": liquidity_risk,
        "Direnç Riski": resistance_risk,
        "Piyasa Riski": market_risk,
        "Toplam": total,
    }


def confidence_stars(confidence: int) -> str:
    stars = max(1, min(5, round(confidence / 20)))
    return "★" * stars + "☆" * (5 - stars)


def coach_decision(
    result: dict[str, Any],
    trend_label: str,
    money_label: str,
    risk_parts: dict[str, int],
) -> str:
    cls = result["Sınıf"]
    risk = risk_parts["Toplam"]
    resistance_risk = risk_parts["Direnç Riski"]

    if cls == "A" and risk <= 35 and resistance_risk < 55:
        return (
            "Bugün işlem açmayı düşünebilirdim. "
            "Trend ve para akışı güçlü; yine de girişte fiyatın destekten tepki "
            "vermesi veya direnç kırılımının hacimle teyit edilmesi daha güvenli olur."
        )

    if cls in {"A", "B"} and resistance_risk >= 55:
        return (
            "Bugün doğrudan kovalamazdım. Teknik yapı olumlu fakat fiyat direnç bölgesine yakın. "
            "Kırılım teyidi veya kontrollü geri çekilme beklerdim."
        )

    if cls == "B":
        return (
            "İzleme listesine alırdım ancak hemen işlem açmazdım. "
            "Olumlu sinyal var; güven, para akışı veya hareket hazırlığından biri henüz tam değil."
        )

    if cls == "C+":
        return (
            "Hareket hazırlığı var fakat yön teyidi eksik. "
            "Hacim devamı ve direnç kırılımı oluşmadan işlem açmazdım."
        )

    if cls == "R":
        return (
            "Bugün işlem açmazdım. Aşırı ısınma, oynaklık veya kovalama riski yüksek. "
            "Fiyatın sakinleşmesini ve risk puanının düşmesini beklerdim."
        )

    if cls == "C":
        return (
            "Beklerdim. Trend ve para akışı aynı anda yeterli teyidi vermiyor. "
            "Yeni güçlenme oluşmadan işlem açmak gereksiz risk yaratabilir."
        )

    return (
        "Bugün işlem açmazdım. Trend veya para akışı zayıf ve risk-getiri dengesi yeterli değil."
    )
