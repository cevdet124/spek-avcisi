from __future__ import annotations

import pandas as pd

from data import download_symbol
from engine import analyze


def scan(symbols: list[str], market: int) -> pd.DataFrame:
    rows = []
    for symbol in symbols:
        frame = download_symbol(symbol)
        if frame is None:
            continue
        result = analyze(frame, market=market)
        if result is None:
            continue

        rows.append({
            "Hisse": symbol,
            "Fiyat": round(result["Fiyat"], 2),
            "Sınıf": result["Sınıf"],
            "Karar": result["Karar"],
            "Spek İz": result["Spek İz"],
            "Güven": result["Güven"],
            "İşlem Kalitesi": result["İşlem Kalitesi"],
            "Trend": result["Trend Gücü"],
            "Trend Evresi": result["Trend Evresi"],
            "Para Akışı": result["Para Akışı Yönü"],
            "Güven Yıldızı": result["Güven Yıldızı"],
            "Kurumsal Para": result["Kurumsal Para"],
            "Hareket Hazırlığı": result["Hareket Hazırlığı"],
            "Yeni Güç": result["Yeni Güç"],
            "Risk": result["Risk"],
            "Likidite": result["Likidite"],
            "Toplama/Dağıtım": result["Toplama/Dağıtım"],
            "Sahte Hareket": result["Sahte Hareket"],
            "AI Yorum": result["AI Yorum"],
        })

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
