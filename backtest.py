from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from engine import analyze_frame


@dataclass
class BacktestConfig:
    horizon: int = 10
    step: int = 3
    min_score: int = 60
    max_risk: int = 55
    min_confidence: int = 55
    fee_bps: float = 20.0


def _max_drawdown(returns: pd.Series) -> float:
    if returns.empty:
        return 0.0
    equity = (1 + returns).cumprod()
    running_max = equity.cummax()
    drawdown = equity / running_max - 1
    return float(drawdown.min() * 100)


def run_backtest(
    frame: pd.DataFrame,
    market_score: int = 55,
    config: BacktestConfig | None = None,
) -> dict[str, Any]:
    config = config or BacktestConfig()

    if frame is None or len(frame) < 180:
        return {
            "summary": {},
            "trades": pd.DataFrame(),
            "equity": pd.DataFrame(),
        }

    rows: list[dict[str, Any]] = []
    start_index = 120
    end_index = len(frame) - config.horizon - 1

    for idx in range(start_index, end_index, max(config.step, 1)):
        history = frame.iloc[: idx + 1]
        result = analyze_frame(history, market_score=market_score)
        if result is None:
            continue

        qualifies = (
            result["Spek İz"] >= config.min_score
            and result["Risk"] <= config.max_risk
            and result["Güven"] >= config.min_confidence
            and result["Sınıf"] in {"A", "B", "C+"}
        )
        if not qualifies:
            continue

        entry = float(frame["Close"].iloc[idx])
        exit_price = float(frame["Close"].iloc[idx + config.horizon])
        gross_return = (exit_price / entry - 1) * 100
        net_return = gross_return - (config.fee_bps / 100)

        future_path = frame["Close"].iloc[idx + 1 : idx + config.horizon + 1]
        max_favorable = (float(future_path.max()) / entry - 1) * 100
        max_adverse = (float(future_path.min()) / entry - 1) * 100

        rows.append(
            {
                "Tarih": str(frame.index[idx])[:10],
                "Sınıf": result["Sınıf"],
                "Karar": result["Karar"],
                "Spek İz": result["Spek İz"],
                "Güven": result["Güven"],
                "Risk": result["Risk"],
                "İşlem Kalitesi": result["İşlem Kalitesi"],
                "Giriş": round(entry, 4),
                "Çıkış": round(exit_price, 4),
                "Brüt Getiri %": round(gross_return, 2),
                "Net Getiri %": round(net_return, 2),
                "Maks. Lehte %": round(max_favorable, 2),
                "Maks. Aleyhte %": round(max_adverse, 2),
            }
        )

    trades = pd.DataFrame(rows)
    if trades.empty:
        return {
            "summary": {},
            "trades": trades,
            "equity": pd.DataFrame(),
        }

    net = trades["Net Getiri %"] / 100
    wins = trades["Net Getiri %"] > 0
    gross_profit = trades.loc[wins, "Net Getiri %"].sum()
    gross_loss = abs(trades.loc[~wins, "Net Getiri %"].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf

    equity = pd.DataFrame(
        {
            "Tarih": pd.to_datetime(trades["Tarih"]),
            "Strateji": (1 + net).cumprod(),
        }
    ).set_index("Tarih")

    summary = {
        "İşlem Sayısı": int(len(trades)),
        "Başarı Oranı %": round(float(wins.mean() * 100), 1),
        "Ortalama Net Getiri %": round(float(trades["Net Getiri %"].mean()), 2),
        "Medyan Net Getiri %": round(float(trades["Net Getiri %"].median()), 2),
        "Toplam Bileşik Getiri %": round(float((equity["Strateji"].iloc[-1] - 1) * 100), 2),
        "Maksimum Düşüş %": round(_max_drawdown(net), 2),
        "Kâr Faktörü": round(float(profit_factor), 2) if np.isfinite(profit_factor) else "∞",
        "Ortalama Lehte Hareket %": round(float(trades["Maks. Lehte %"].mean()), 2),
        "Ortalama Aleyhte Hareket %": round(float(trades["Maks. Aleyhte %"].mean()), 2),
    }

    return {
        "summary": summary,
        "trades": trades,
        "equity": equity,
    }
