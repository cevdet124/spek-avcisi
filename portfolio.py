from __future__ import annotations

import json
from typing import Any

import pandas as pd

from data import download_symbol
from engine import analyze


def normalize_symbols(text: str) -> list[str]:
    raw = text.replace(";", ",").replace("\n", ",").split(",")
    symbols = []
    for item in raw:
        symbol = item.strip().upper().replace(".IS", "")
        if symbol and symbol not in symbols:
            symbols.append(symbol)
    return symbols


def portfolio_table(symbols: list[str], market: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for symbol in symbols:
        frame = download_symbol(symbol)
        if frame is None:
            continue

        result = analyze(frame, market=market)
        if result is None:
            continue

        if result["Sınıf"] == "A":
            status = "🟢 Güçlü Tut / Aday"
        elif result["Sınıf"] == "B":
            status = "🟩 Tut / İzle"
        elif result["Sınıf"] == "C+":
            status = "🚀 Teyit Bekle"
        elif result["Sınıf"] == "R":
            status = "🔥 Riski Azalt / Kovalama"
        elif result["Sınıf"] == "C":
            status = "🟡 Nötr / Bekle"
        elif result["Sınıf"] == "D" and result["Risk"] >= 60:
            status = "🔴 Çıkış / Risk İncele"
        elif result["Sınıf"] == "D":
            status = "🟡 Zayıf — Bekle / İzle"
        else:
            status = "🟡 Nötr / Bekle"

        rows.append({
            "Hisse": symbol,
            "Fiyat": round(result["Fiyat"], 2),
            "Durum": status,
            "Karar": result["Karar"],
            "Güven": result["Güven"],
            "Risk": result["Risk"],
            "İşlem Kalitesi": result["İşlem Kalitesi"],
            "Destek": round(result["Destek"], 2),
            "Direnç": round(result["Direnç"], 2),
            "Kontrol": round(result["Kontrol"], 2),
            "Hedef Alt": round(result["Hedef Alt"], 2),
            "Hedef Üst": round(result["Hedef Üst"], 2),
            "Trend Evresi": result["Trend Evresi"],
            "Para Akışı": result["Para Akışı Yönü"],
            "Güven Yıldızı": result["Güven Yıldızı"],
            "AI Yorum": result["AI Yorum"],
            "AI Koçu": result["AI Koçu"],
        })

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows).sort_values(
        ["Risk", "İşlem Kalitesi"],
        ascending=[True, False],
    ).reset_index(drop=True)


def portfolio_health(table: pd.DataFrame) -> dict[str, Any]:
    if table.empty:
        return {
            "Güç": 0,
            "Risk": 0,
            "Güven": 0,
            "Olumlu": 0,
            "Uyarı": 0,
        }

    positive = table["Durum"].str.contains("🟢|🟩", regex=True, na=False).sum()
    warning = table["Durum"].str.contains("🔥|🔴", regex=True, na=False).sum()

    return {
        "Güç": int(round(table["İşlem Kalitesi"].mean())),
        "Risk": int(round(table["Risk"].mean())),
        "Güven": int(round(table["Güven"].mean())),
        "Olumlu": int(positive),
        "Uyarı": int(warning),
    }


def create_alerts(table: pd.DataFrame) -> pd.DataFrame:
    alerts: list[dict[str, str]] = []

    if table.empty:
        return pd.DataFrame()

    for _, row in table.iterrows():
        symbol = row["Hisse"]

        if row["Risk"] >= 65:
            alerts.append({
                "Hisse": symbol,
                "Öncelik": "🔴 Yüksek",
                "Alarm": "Risk puanı yüksek",
                "Açıklama": f"Risk {row['Risk']}/100 seviyesinde.",
            })

        if row["Fiyat"] <= row["Kontrol"] * 1.02:
            alerts.append({
                "Hisse": symbol,
                "Öncelik": "🔴 Yüksek",
                "Alarm": "Kontrol seviyesine yakın",
                "Açıklama": f"Fiyat {row['Fiyat']:.2f}, kontrol {row['Kontrol']:.2f}.",
            })

        if row["Fiyat"] >= row["Direnç"] * 0.99:
            alerts.append({
                "Hisse": symbol,
                "Öncelik": "🟡 Orta",
                "Alarm": "Direnç bölgesinde",
                "Açıklama": "Kırılım teyidi veya kâr satışı riski izlenmeli.",
            })

        if "A SINIFI" in row["Karar"]:
            alerts.append({
                "Hisse": symbol,
                "Öncelik": "🟢 Fırsat",
                "Alarm": "A sınıfı aday",
                "Açıklama": "Trend, güven ve işlem kalitesi güçlü.",
            })

        if "KOVALAMA" in row["Karar"]:
            alerts.append({
                "Hisse": symbol,
                "Öncelik": "🟠 Dikkat",
                "Alarm": "Kovalama riski",
                "Açıklama": "Aşırı ısınma veya spekülatif risk yükselmiş.",
            })

    return pd.DataFrame(alerts)


def export_lists(portfolio: list[str], favorites: list[str]) -> str:
    return json.dumps(
        {
            "portfolio": portfolio,
            "favorites": favorites,
        },
        ensure_ascii=False,
        indent=2,
    )


def import_lists(content: str) -> tuple[list[str], list[str]]:
    data = json.loads(content)
    portfolio = [str(x).strip().upper() for x in data.get("portfolio", []) if str(x).strip()]
    favorites = [str(x).strip().upper() for x in data.get("favorites", []) if str(x).strip()]
    return portfolio, favorites
