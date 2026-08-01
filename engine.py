from __future__ import annotations

import math
import time
from typing import Any

import numpy as np
import pandas as pd
import yfinance as yf


def _flat_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)
    return frame


def download_one(symbol: str) -> pd.DataFrame | None:
    symbol = symbol.strip().upper()
    try:
        frame = yf.download(
            f"{symbol}.IS",
            period="2y",
            interval="1d",
            auto_adjust=True,
            progress=False,
            timeout=15,
        )
        frame = _flat_columns(frame).dropna()
        return frame if len(frame) >= 120 else None
    except Exception:
        return None


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    diff = close.diff()
    up = diff.clip(lower=0)
    down = -diff.clip(upper=0)
    avg_up = up.ewm(alpha=1 / period, adjust=False).mean()
    avg_down = down.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_up / avg_down.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    previous = close.shift(1)
    tr = pd.concat(
        [(high - low), (high - previous).abs(), (low - previous).abs()],
        axis=1,
    ).max(axis=1)
    return tr.rolling(period).mean()


def _mfi(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series,
    period: int = 14,
) -> pd.Series:
    typical = (high + low + close) / 3
    raw = typical * volume
    direction = typical.diff()
    positive = raw.where(direction > 0, 0.0)
    negative = raw.where(direction < 0, 0.0).abs()
    ratio = positive.rolling(period).sum() / negative.rolling(period).sum().replace(0, np.nan)
    return 100 - (100 / (1 + ratio))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        return result if math.isfinite(result) else default
    except Exception:
        return default


def analyze_frame(frame: pd.DataFrame, market_score: int = 55) -> dict[str, Any] | None:
    if frame is None:
        return None

    frame = _flat_columns(frame).dropna(subset=["Open", "High", "Low", "Close", "Volume"])
    if len(frame) < 120:
        return None

    close = frame["Close"].astype(float)
    high = frame["High"].astype(float)
    low = frame["Low"].astype(float)
    volume = frame["Volume"].astype(float)

    price = _safe_float(close.iloc[-1])
    previous_price = _safe_float(close.iloc[-2], price)
    daily_change = ((price - previous_price) / previous_price * 100) if previous_price else 0

    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()
    ma100 = close.rolling(100).mean()

    rsi = _rsi(close)
    last_rsi = _safe_float(rsi.iloc[-1], 50)

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    macd_hist = macd - macd_signal

    avg_volume20 = _safe_float(volume.rolling(20).mean().iloc[-1], 1)
    volume_ratio = _safe_float(volume.iloc[-1] / avg_volume20 if avg_volume20 else 0)
    volume_persistence = _safe_float(
        volume.tail(5).mean() / volume.iloc[-10:-5].mean()
        if _safe_float(volume.iloc[-10:-5].mean()) > 0
        else 1
    )
    transaction_value = price * _safe_float(volume.iloc[-1])

    price_range = (high - low).replace(0, np.nan)
    multiplier = (((close - low) - (high - close)) / price_range).replace(
        [np.inf, -np.inf], 0
    ).fillna(0)
    money_volume = multiplier * volume
    cmf = money_volume.rolling(20).sum() / volume.rolling(20).sum().replace(0, np.nan)
    last_cmf = _safe_float(cmf.iloc[-1])

    mfi = _mfi(high, low, close, volume)
    last_mfi = _safe_float(mfi.iloc[-1], 50)

    obv = (np.sign(close.diff()).fillna(0) * volume).cumsum()
    obv_slope = _safe_float(
        (obv.iloc[-1] - obv.iloc[-10]) / max(abs(obv.iloc[-10]), 1) * 100
    )

    adl = (multiplier * volume).cumsum()
    adl_slope = _safe_float(
        (adl.iloc[-1] - adl.iloc[-10]) / max(abs(adl.iloc[-10]), 1) * 100
    )

    atr = _atr(high, low, close)
    atr_value = _safe_float(atr.iloc[-1])
    atr_percent = (atr_value / price * 100) if price else 0

    weekly = close.resample("W-FRI").last().dropna()
    if len(weekly) >= 20:
        wma10 = weekly.rolling(10).mean().iloc[-1]
        wma20 = weekly.rolling(20).mean().iloc[-1]
        weekly_score = 100 if weekly.iloc[-1] > wma10 > wma20 else 65 if weekly.iloc[-1] > wma20 else 25
    else:
        weekly_score = 50

    last_ma20 = _safe_float(ma20.iloc[-1], price)
    last_ma50 = _safe_float(ma50.iloc[-1], price)
    last_ma100 = _safe_float(ma100.iloc[-1], price)

    if price > last_ma20 > last_ma50 > last_ma100:
        trend_score = 100
    elif price > last_ma20 > last_ma50:
        trend_score = 82
    elif price > last_ma50:
        trend_score = 55
    else:
        trend_score = 20

    institutional_score = round(
        np.clip(
            (
                np.interp(last_cmf, [-0.2, 0, 0.2], [10, 55, 100]) * 0.30
                + np.interp(last_mfi, [20, 50, 80], [20, 65, 90]) * 0.20
                + np.interp(obv_slope, [-10, 0, 10], [15, 55, 100]) * 0.25
                + np.interp(adl_slope, [-10, 0, 10], [15, 55, 100]) * 0.25
            ),
            0,
            100,
        )
    )

    momentum_score = round(
        np.clip(
            np.interp(last_rsi, [30, 50, 62, 75, 90], [20, 70, 100, 55, 10]) * 0.55
            + np.interp(_safe_float(macd_hist.iloc[-1]), [-abs(price)*0.01, 0, abs(price)*0.01], [15, 55, 100]) * 0.45,
            0,
            100,
        )
    )

    recent_high = _safe_float(high.iloc[-21:-1].max(), price)
    recent_low = _safe_float(low.tail(20).min(), price)
    range_percent = ((recent_high - recent_low) / price * 100) if price else 0
    distance_to_resistance = ((recent_high - price) / price * 100) if price else 0

    squeeze_score = round(np.clip(np.interp(range_percent, [5, 10, 20], [100, 65, 20]), 0, 100))
    volume_score = round(
        np.clip(
            np.interp(volume_ratio, [0.5, 1, 1.5, 2.5], [15, 50, 80, 100]) * 0.65
            + np.interp(volume_persistence, [0.7, 1, 1.3, 1.8], [15, 50, 80, 100]) * 0.35,
            0,
            100,
        )
    )
    breakout_score = round(
        100 if price > recent_high else np.clip(np.interp(distance_to_resistance, [0, 3, 8, 15], [90, 75, 40, 15]), 0, 100)
    )

    movement_readiness = round(
        squeeze_score * 0.25
        + volume_score * 0.30
        + momentum_score * 0.20
        + breakout_score * 0.15
        + institutional_score * 0.10
    )

    liquidity_score = round(
        np.clip(
            np.interp(transaction_value, [5_000_000, 30_000_000, 100_000_000, 500_000_000], [15, 45, 75, 100]),
            0,
            100,
        )
    )

    speculative_risk = round(
        np.clip(
            np.interp(atr_percent, [2, 4, 7, 12], [10, 30, 65, 100]) * 0.30
            + np.interp(last_rsi, [55, 70, 80, 90], [10, 35, 75, 100]) * 0.20
            + (100 - liquidity_score) * 0.25
            + np.interp(max(-distance_to_resistance, 0), [0, 3, 8], [10, 55, 100]) * 0.10
            + (100 - weekly_score) * 0.15,
            1,
            100,
        )
    )

    new_strength = 0
    if _safe_float(rsi.iloc[-1] - rsi.iloc[-5]) >= 5:
        new_strength += 30
    if price > last_ma20 and _safe_float(close.iloc[-5]) <= _safe_float(ma20.iloc[-5], price):
        new_strength += 30
    if volume_persistence >= 1.20:
        new_strength += 20
    if last_cmf > 0 and _safe_float(cmf.iloc[-1] - cmf.iloc[-5]) > 0:
        new_strength += 20
    new_strength = min(new_strength, 100)

    fake_move = "✅ Hareket teyitli"
    if daily_change > 1 and last_cmf < 0:
        fake_move = "🚨 Sahte yükseliş şüphesi"
    elif volume_ratio >= 1.5 and institutional_score < 40:
        fake_move = "⚠️ Hacim var, para teyidi zayıf"
    elif price < last_ma20 and volume_ratio >= 1.5:
        fake_move = "🚨 Satış baskısı riski"

    if last_cmf > 0.10 and volume_persistence >= 1.05 and price >= last_ma20:
        accumulation = "🧲 Toplama ihtimali yüksek"
    elif last_cmf < -0.05 and price < last_ma20:
        accumulation = "📤 Dağıtım ihtimali"
    else:
        accumulation = "⚖️ Net toplama/dağıtım yok"

    if _safe_float(macd_hist.iloc[-1]) > 0 and _safe_float(macd_hist.iloc[-4]) <= 0:
        trend_change = "🟢 Yeni pozitif trend dönüşü"
    elif _safe_float(macd_hist.iloc[-1]) < 0 and _safe_float(macd_hist.iloc[-4]) >= 0:
        trend_change = "🔴 Negatif trend dönüşü"
    else:
        trend_change = "🟡 Trend değişimi yok"

    risk = round(
        speculative_risk * 0.55
        + (100 - liquidity_score) * 0.20
        + max(0, 50 - institutional_score) * 0.15
        + max(0, 50 - weekly_score) * 0.10
    )
    risk = int(np.clip(risk, 1, 100))

    confidence = round(
        trend_score * 0.20
        + weekly_score * 0.15
        + institutional_score * 0.25
        + volume_score * 0.15
        + momentum_score * 0.15
        + market_score * 0.10
        - risk * 0.15
    )
    confidence = int(np.clip(confidence, 0, 100))

    trade_quality = round(
        confidence * 0.35
        + movement_readiness * 0.25
        + liquidity_score * 0.15
        + trend_score * 0.15
        + institutional_score * 0.10
        - speculative_risk * 0.15
    )
    trade_quality = int(np.clip(trade_quality, 0, 100))

    spek_score = round(
        trend_score * 0.18
        + weekly_score * 0.10
        + institutional_score * 0.24
        + volume_score * 0.15
        + momentum_score * 0.12
        + movement_readiness * 0.12
        + market_score * 0.09
        - risk * 0.18
    )
    spek_score = int(np.clip(spek_score, 0, 100))

    positive_reasons = []
    warnings = []
    if trend_score >= 80:
        positive_reasons.append("Günlük trend güçlü.")
    if weekly_score >= 65:
        positive_reasons.append("Haftalık trend günlük görünümü destekliyor.")
    if institutional_score >= 70:
        positive_reasons.append("Kurumsal para göstergeleri pozitif uyum gösteriyor.")
    if volume_score >= 70:
        positive_reasons.append("Hacim ve hacim devamlılığı güçlü.")
    if movement_readiness >= 70:
        positive_reasons.append("Hareket hazırlığı yüksek.")
    if new_strength >= 60:
        positive_reasons.append("Son günlerde yeni güçlenme oluşmuş.")

    if last_rsi >= 75:
        warnings.append("RSI aşırı alım bölgesinde.")
    if distance_to_resistance <= 3:
        warnings.append("Fiyat kısa vadeli dirence yakın; kovalama riski var.")
    if liquidity_score < 50:
        warnings.append("Likidite düşük veya orta-alt seviyede.")
    if speculative_risk >= 60:
        warnings.append("Spekülatif ve oynaklık riski yüksek.")
    if fake_move != "✅ Hareket teyitli":
        warnings.append(fake_move)

    if (
        spek_score >= 75
        and confidence >= 70
        and trade_quality >= 70
        and risk <= 35
        and last_rsi < 75
        and liquidity_score >= 50
    ):
        decision = "🟢 A SINIFI AL ADAYI"
        class_name = "A"
    elif spek_score >= 62 and confidence >= 55 and risk <= 55:
        decision = "🟩 B SINIFI AL / İZLE"
        class_name = "B"
    elif movement_readiness >= 65 and risk <= 55:
        decision = "🚀 HAREKET HAZIRLIĞI — TEYİT BEKLE"
        class_name = "C+"
    elif last_rsi >= 80 or speculative_risk >= 75:
        decision = "🔥 KOVALAMA / AŞIRI RİSK"
        class_name = "R"
    elif spek_score >= 40:
        decision = "🟡 BEKLE"
        class_name = "C"
    else:
        decision = "🔴 KAÇIN"
        class_name = "D"

    if decision.startswith("🟢"):
        scenario = "Trend, para akışı, hacim ve güven birlikte olumlu; giriş yine destek/direnç teyidiyle değerlendirilmelidir."
    elif "HAREKET HAZIRLIĞI" in decision:
        scenario = "Hareket hazırlığı var fakat henüz güçlü yön teyidi oluşmamış."
    elif "KOVALAMA" in decision:
        scenario = "Hisse güçlü görünse bile fiyat aşırı ısınmış veya riskli bölgede; kovalamak yerine sakinleşme beklenmeli."
    elif decision.startswith("🟩"):
        scenario = "Olumlu teknik yapı var fakat A sınıfı için güven, likidite veya risk koşullarından biri eksik."
    elif decision.startswith("🟡"):
        scenario = "Göstergeler tam uyumlu değil; yeni pozisyon için teyit beklenmeli."
    else:
        scenario = "Trend, para veya risk koşulları yeni pozisyon için yeterli değil."

    control = max(recent_low * 0.98, price - 2 * atr_value)
    target_low = recent_high
    target_high = recent_high + max(recent_high - recent_low, atr_value * 2) * 0.50

    return {
        "Fiyat": price,
        "Günlük %": daily_change,
        "Spek İz": spek_score,
        "Güven": confidence,
        "İşlem Kalitesi": trade_quality,
        "Risk": risk,
        "Trend Gücü": trend_score,
        "Kurumsal Para": institutional_score,
        "Hareket Hazırlığı": movement_readiness,
        "Momentum": momentum_score,
        "Likidite": liquidity_score,
        "Spekülatif Risk": speculative_risk,
        "Yeni Güç": new_strength,
        "Para Yönü": "💰 Para girişi" if institutional_score >= 70 else "📤 Para çıkışı/zayıflık" if institutional_score < 40 else "⚖️ Para akışı nötr",
        "Toplama/Dağıtım": accumulation,
        "Sahte Hareket": fake_move,
        "Trend Değişimi": trend_change,
        "Destek": recent_low,
        "Direnç": recent_high,
        "Hedef Alt": target_low,
        "Hedef Üst": target_high,
        "Kontrol": control,
        "Karar": decision,
        "Sınıf": class_name,
        "Senaryo": scenario,
        "Olumlu Nedenler": positive_reasons or ["Belirgin güçlü teyit oluşmadı."],
        "Uyarılar": warnings or ["Belirgin ek risk uyarısı yok."],
        "Veri Tarihi": str(frame.index[-1])[:10],
    }


def scan_universe(symbols: list[str], market_score: int = 55) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for symbol in symbols:
        frame = download_one(symbol)
        if frame is None:
            continue
        result = analyze_frame(frame, market_score=market_score)
        if result is None:
            continue
        rows.append(
            {
                "Hisse": symbol,
                "Fiyat": round(result["Fiyat"], 2),
                "Sınıf": result["Sınıf"],
                "Karar": result["Karar"],
                "Spek İz": result["Spek İz"],
                "Güven": result["Güven"],
                "İşlem Kalitesi": result["İşlem Kalitesi"],
                "Trend": result["Trend Gücü"],
                "Kurumsal Para": result["Kurumsal Para"],
                "Hareket Hazırlığı": result["Hareket Hazırlığı"],
                "Yeni Güç": result["Yeni Güç"],
                "Risk": result["Risk"],
                "Likidite": result["Likidite"],
                "Toplama/Dağıtım": result["Toplama/Dağıtım"],
                "Sahte Hareket": result["Sahte Hareket"],
            }
        )
        time.sleep(0.05)

    if not rows:
        return pd.DataFrame()

    table = pd.DataFrame(rows)
    table["Kalite Sırası"] = (
        table["İşlem Kalitesi"] * 0.35
        + table["Spek İz"] * 0.30
        + table["Güven"] * 0.20
        + table["Yeni Güç"] * 0.15
        - table["Risk"] * 0.25
    ).round(1)

    return table.sort_values(
        ["Kalite Sırası", "Risk"],
        ascending=[False, True],
    ).reset_index(drop=True)
