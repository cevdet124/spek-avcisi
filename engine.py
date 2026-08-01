from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from indicators import ad_line, atr, bollinger_width, cmf, macd, mfi, obv, rsi
from intelligence import confidence_stars, coach_decision, money_flow_trend, risk_breakdown, trend_phase


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        return result if math.isfinite(result) else default
    except Exception:
        return default


def market_score(frame: pd.DataFrame | None) -> tuple[int, str]:
    if frame is None or len(frame) < 60:
        return 55, "🟡 BIST verisi yetersiz"
    close = frame["Close"].astype(float)
    ma20 = close.rolling(20).mean().iloc[-1]
    ma50 = close.rolling(50).mean().iloc[-1]
    price = close.iloc[-1]
    if price > ma20 > ma50:
        return 90, "🟢 BIST trend pozitif"
    if price > ma50:
        return 65, "🟡 BIST kararsız"
    return 35, "🔴 BIST trend zayıf"


def analyze(frame: pd.DataFrame, market: int = 55) -> dict[str, Any] | None:
    if frame is None:
        return None
    frame = frame.dropna(subset=["Open", "High", "Low", "Close", "Volume"])
    if len(frame) < 120:
        return None

    close = frame["Close"].astype(float)
    high = frame["High"].astype(float)
    low = frame["Low"].astype(float)
    volume = frame["Volume"].astype(float)

    price = safe_float(close.iloc[-1])
    previous = safe_float(close.iloc[-2], price)
    daily_change = ((price / previous) - 1) * 100 if previous else 0

    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()
    ma100 = close.rolling(100).mean()

    rsi_s = rsi(close)
    atr_s = atr(high, low, close)
    mfi_s = mfi(high, low, close, volume)
    cmf_s = cmf(high, low, close, volume)
    obv_s = obv(close, volume)
    ad_s = ad_line(high, low, close, volume)
    bw_s = bollinger_width(close)
    _, _, macd_hist = macd(close)

    last_rsi = safe_float(rsi_s.iloc[-1], 50)
    last_atr = safe_float(atr_s.iloc[-1])
    atr_pct = (last_atr / price * 100) if price else 0
    last_mfi = safe_float(mfi_s.iloc[-1], 50)
    last_cmf = safe_float(cmf_s.iloc[-1])

    avg_vol20 = safe_float(volume.rolling(20).mean().iloc[-1], 1)
    vol_ratio = safe_float(volume.iloc[-1] / avg_vol20 if avg_vol20 else 0)
    vol_persistence = safe_float(
        volume.tail(5).mean() / volume.iloc[-10:-5].mean()
        if safe_float(volume.iloc[-10:-5].mean()) > 0 else 1
    )
    transaction_value = price * safe_float(volume.iloc[-1])

    obv_slope = safe_float((obv_s.iloc[-1] - obv_s.iloc[-10]) / max(abs(obv_s.iloc[-10]), 1) * 100)
    ad_slope = safe_float((ad_s.iloc[-1] - ad_s.iloc[-10]) / max(abs(ad_s.iloc[-10]), 1) * 100)

    weekly = close.resample("W-FRI").last().dropna()
    if len(weekly) >= 20:
        w10 = weekly.rolling(10).mean().iloc[-1]
        w20 = weekly.rolling(20).mean().iloc[-1]
        weekly_score = 100 if weekly.iloc[-1] > w10 > w20 else 65 if weekly.iloc[-1] > w20 else 25
    else:
        weekly_score = 50

    ma20_last = safe_float(ma20.iloc[-1], price)
    ma50_last = safe_float(ma50.iloc[-1], price)
    ma100_last = safe_float(ma100.iloc[-1], price)

    if price > ma20_last > ma50_last > ma100_last:
        trend_score = 100
    elif price > ma20_last > ma50_last:
        trend_score = 82
    elif price > ma50_last:
        trend_score = 55
    else:
        trend_score = 20

    institutional = round(np.clip(
        np.interp(last_cmf, [-0.2, 0, 0.2], [10, 55, 100]) * 0.30
        + np.interp(last_mfi, [20, 50, 80], [20, 65, 90]) * 0.20
        + np.interp(obv_slope, [-10, 0, 10], [15, 55, 100]) * 0.25
        + np.interp(ad_slope, [-10, 0, 10], [15, 55, 100]) * 0.25,
        0, 100
    ))

    momentum = round(np.clip(
        np.interp(last_rsi, [30, 50, 62, 75, 90], [20, 70, 100, 55, 10]) * 0.55
        + np.interp(safe_float(macd_hist.iloc[-1]), [-abs(price)*0.01, 0, abs(price)*0.01], [15, 55, 100]) * 0.45,
        0, 100
    ))

    recent_high = safe_float(high.iloc[-21:-1].max(), price)
    recent_low = safe_float(low.tail(20).min(), price)
    distance_to_resistance = ((recent_high - price) / price * 100) if price else 0

    bw_now = safe_float(bw_s.iloc[-1])
    bw_mean = safe_float(bw_s.tail(20).mean(), bw_now)
    squeeze_score = round(np.clip(
        np.interp((bw_now / bw_mean) if bw_mean else 1, [0.5, 0.8, 1.2], [100, 70, 20]),
        0, 100
    ))

    volume_score = round(np.clip(
        np.interp(vol_ratio, [0.5, 1, 1.5, 2.5], [15, 50, 80, 100]) * 0.65
        + np.interp(vol_persistence, [0.7, 1, 1.3, 1.8], [15, 50, 80, 100]) * 0.35,
        0, 100
    ))

    breakout_score = round(
        100 if price > recent_high
        else np.clip(np.interp(distance_to_resistance, [0, 3, 8, 15], [90, 75, 40, 15]), 0, 100)
    )

    preparation = round(
        squeeze_score * 0.25
        + volume_score * 0.30
        + momentum * 0.20
        + breakout_score * 0.15
        + institutional * 0.10
    )

    liquidity = round(np.clip(
        np.interp(transaction_value, [5_000_000, 30_000_000, 100_000_000, 500_000_000], [15, 45, 75, 100]),
        0, 100
    ))

    speculative_risk = round(np.clip(
        np.interp(atr_pct, [2, 4, 7, 12], [10, 30, 65, 100]) * 0.30
        + np.interp(last_rsi, [55, 70, 80, 90], [10, 35, 75, 100]) * 0.20
        + (100 - liquidity) * 0.25
        + np.interp(max(-distance_to_resistance, 0), [0, 3, 8], [10, 55, 100]) * 0.10
        + (100 - weekly_score) * 0.15,
        1, 100
    ))

    new_strength = 0
    if safe_float(rsi_s.iloc[-1] - rsi_s.iloc[-5]) >= 5:
        new_strength += 30
    if price > ma20_last and safe_float(close.iloc[-5]) <= safe_float(ma20.iloc[-5], price):
        new_strength += 30
    if vol_persistence >= 1.20:
        new_strength += 20
    if last_cmf > 0 and safe_float(cmf_s.iloc[-1] - cmf_s.iloc[-5]) > 0:
        new_strength += 20
    new_strength = min(new_strength, 100)

    risk = round(
        speculative_risk * 0.55
        + (100 - liquidity) * 0.20
        + max(0, 50 - institutional) * 0.15
        + max(0, 50 - weekly_score) * 0.10
    )
    risk = int(np.clip(risk, 1, 100))

    confidence = round(
        trend_score * 0.20
        + weekly_score * 0.15
        + institutional * 0.25
        + volume_score * 0.15
        + momentum * 0.15
        + market * 0.10
        - risk * 0.15
    )
    confidence = int(np.clip(confidence, 0, 100))

    trade_quality = round(
        confidence * 0.35
        + preparation * 0.25
        + liquidity * 0.15
        + trend_score * 0.15
        + institutional * 0.10
        - speculative_risk * 0.15
    )
    trade_quality = int(np.clip(trade_quality, 0, 100))

    spek = round(
        trend_score * 0.18
        + weekly_score * 0.10
        + institutional * 0.24
        + volume_score * 0.15
        + momentum * 0.12
        + preparation * 0.12
        + market * 0.09
        - risk * 0.18
    )
    spek = int(np.clip(spek, 0, 100))

    if last_rsi >= 80 or speculative_risk >= 75:
        decision, cls = "🔥 KOVALAMA / AŞIRI RİSK", "R"
    elif spek >= 75 and confidence >= 70 and trade_quality >= 70 and risk <= 35 and liquidity >= 50:
        decision, cls = "🟢 A SINIFI AL ADAYI", "A"
    elif spek >= 62 and confidence >= 55 and risk <= 55:
        decision, cls = "🟩 B SINIFI AL / İZLE", "B"
    elif preparation >= 65 and risk <= 55:
        decision, cls = "🚀 HAREKET HAZIRLIĞI — TEYİT BEKLE", "C+"
    elif spek >= 40:
        decision, cls = "🟡 BEKLE", "C"
    else:
        decision, cls = "🔴 KAÇIN", "D"

    fake_move = "✅ Hareket teyitli"
    if daily_change > 1 and last_cmf < 0:
        fake_move = "🚨 Sahte yükseliş şüphesi"
    elif vol_ratio >= 1.5 and institutional < 40:
        fake_move = "⚠️ Hacim var, para teyidi zayıf"

    accumulation = (
        "🧲 Toplama ihtimali yüksek"
        if last_cmf > 0.10 and vol_persistence >= 1.05 and price >= ma20_last
        else "📤 Dağıtım ihtimali"
        if last_cmf < -0.05 and price < ma20_last
        else "⚖️ Net toplama/dağıtım yok"
    )

    control = max(recent_low * 0.98, price - 2 * last_atr)
    target_low = recent_high
    target_high = recent_high + max(recent_high - recent_low, last_atr * 2) * 0.50

    reasons, warnings = [], []
    if trend_score >= 80:
        reasons.append("Günlük trend güçlü.")
    if weekly_score >= 65:
        reasons.append("Haftalık trend destekliyor.")
    if institutional >= 70:
        reasons.append("Kurumsal para göstergeleri pozitif.")
    if volume_score >= 70:
        reasons.append("Hacim ve devamlılık güçlü.")
    if preparation >= 70:
        reasons.append("Hareket hazırlığı yüksek.")
    if new_strength >= 60:
        reasons.append("Yeni güçlenme oluşmuş.")

    if last_rsi >= 75:
        warnings.append("RSI aşırı alım bölgesinde.")
    if distance_to_resistance <= 3:
        warnings.append("Dirence yakın; kovalama riski var.")
    if liquidity < 50:
        warnings.append("Likidite düşük veya orta-alt.")
    if speculative_risk >= 60:
        warnings.append("Spekülatif risk yüksek.")
    if fake_move != "✅ Hareket teyitli":
        warnings.append(fake_move)

    if cls == "A":
        ai_comment = "Trend, para akışı, hacim ve güven birlikte güçlü. Aday kalitesi yüksek; giriş yine destek/direnç teyidiyle değerlendirilmelidir."
    elif cls == "B":
        ai_comment = "Olumlu teknik yapı var ancak A sınıfı için güven, likidite veya risk koşullarından biri eksik."
    elif cls == "C+":
        ai_comment = "Hareket hazırlığı var fakat yön teyidi tam değil. Kırılım ve hacim devamı izlenmeli."
    elif cls == "R":
        ai_comment = "Teknik güç görünse bile fiyat aşırı ısınmış veya spekülatif risk yüksek. Kovalamak yerine sakinleşme beklenmeli."
    elif cls == "C":
        ai_comment = "Göstergeler tam uyumlu değil. Yeni işlem için teyit beklemek daha uygun."
    else:
        ai_comment = "Trend, para veya risk koşulları yeni pozisyon için yeterli değil."


    trend_phase_label, trend_phase_score = trend_phase(
        close,
        ma20,
        ma50,
        ma100,
    )

    money_label, money_trend_score, money_components = money_flow_trend(
        cmf_s,
        obv_s,
        ad_s,
        volume,
    )

    risk_parts = risk_breakdown(
        last_rsi,
        atr_pct,
        liquidity,
        distance_to_resistance,
        market,
    )

    calibrated_risk = int(round(
        risk * 0.45
        + risk_parts["Toplam"] * 0.55
    ))

    evidence_count = sum([
        trend_score >= 70,
        weekly_score >= 65,
        institutional >= 65,
        volume_score >= 60,
        momentum >= 60,
        preparation >= 60,
    ])

    calibrated_confidence = int(np.clip(
        confidence * 0.70
        + evidence_count / 6 * 100 * 0.30
        - max(0, calibrated_risk - 50) * 0.20,
        0,
        100,
    ))

    coach_text = coach_decision(
        {
            "Sınıf": cls,
            "Karar": decision,
        },
        trend_phase_label,
        money_label,
        risk_parts,
    )

    return {
        "Fiyat": price,
        "Günlük %": daily_change,
        "Spek İz": spek,
        "Güven": calibrated_confidence,
        "Güven Yıldızı": confidence_stars(calibrated_confidence),
        "İşlem Kalitesi": trade_quality,
        "Risk": calibrated_risk,
        "Trend Gücü": trend_score,
        "Trend Evresi": trend_phase_label,
        "Trend Evre Puanı": trend_phase_score,
        "Kurumsal Para": institutional,
        "Para Akışı Yönü": money_label,
        "Para Akışı Puanı": money_trend_score,
        "Para Bileşenleri": money_components,
        "Hareket Hazırlığı": preparation,
        "Momentum": momentum,
        "Likidite": liquidity,
        "Spekülatif Risk": speculative_risk,
        "Yeni Güç": new_strength,
        "Toplama/Dağıtım": accumulation,
        "Sahte Hareket": fake_move,
        "Destek": recent_low,
        "Direnç": recent_high,
        "Hedef Alt": target_low,
        "Hedef Üst": target_high,
        "Kontrol": control,
        "ATR": last_atr,
        "Karar": decision,
        "Sınıf": cls,
        "AI Yorum": ai_comment,
        "AI Koçu": coach_text,
        "Risk Bileşenleri": risk_parts,
        "Olumlu Nedenler": reasons or ["Belirgin güçlü teyit oluşmadı."],
        "Uyarılar": warnings or ["Belirgin ek risk uyarısı yok."],
        "Veri Tarihi": str(frame.index[-1])[:10],
    }
