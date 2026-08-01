from __future__ import annotations

from dataclasses import asdict
from itertools import product
from typing import Any

import numpy as np
import pandas as pd

from backtest import BacktestConfig, run_backtest


def _number(value: Any, default: float = 0.0) -> float:
    try:
        if value == "∞":
            return 10.0
        value = float(value)
        return value if np.isfinite(value) else default
    except Exception:
        return default


def objective(summary: dict[str, Any]) -> float:
    """Risk-adjusted score. Rejects tiny samples to reduce overfitting."""
    trades = int(summary.get("İşlem Sayısı", 0))
    if trades < 12:
        return -999.0

    total_return = _number(summary.get("Toplam Bileşik Getiri %"))
    average_return = _number(summary.get("Ortalama Net Getiri %"))
    drawdown = abs(_number(summary.get("Maksimum Düşüş %")))
    profit_factor = min(_number(summary.get("Kâr Faktörü")), 4.0)
    win_rate = _number(summary.get("Başarı Oranı %"))

    return round(
        total_return * 0.30
        + average_return * 8.0
        + profit_factor * 8.0
        + win_rate * 0.08
        - drawdown * 0.45
        + min(trades, 50) * 0.08,
        3,
    )


def _split_frame(frame: pd.DataFrame, train_ratio: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    split = int(len(frame) * train_ratio)
    split = max(220, min(split, len(frame) - 120))
    train = frame.iloc[:split].copy()
    # Give test set enough warm-up history without allowing training outcomes into scoring.
    warmup_start = max(0, split - 140)
    test = frame.iloc[warmup_start:].copy()
    test.attrs["evaluation_start"] = frame.index[split]
    return train, test


def _filter_test_trades(result: dict[str, Any], evaluation_start: Any) -> dict[str, Any]:
    trades = result.get("trades", pd.DataFrame()).copy()
    if trades.empty:
        return {"summary": {}, "trades": trades, "equity": pd.DataFrame()}

    dates = pd.to_datetime(trades["Tarih"])
    trades = trades.loc[dates >= pd.Timestamp(evaluation_start)].reset_index(drop=True)
    if trades.empty:
        return {"summary": {}, "trades": trades, "equity": pd.DataFrame()}

    returns = trades["Net Getiri %"] / 100
    equity = (1 + returns).cumprod()
    wins = trades["Net Getiri %"] > 0
    gross_profit = trades.loc[wins, "Net Getiri %"].sum()
    gross_loss = abs(trades.loc[~wins, "Net Getiri %"].sum())
    pf = gross_profit / gross_loss if gross_loss > 0 else np.inf
    peak = equity.cummax()
    max_dd = float((equity / peak - 1).min() * 100)

    summary = {
        "İşlem Sayısı": int(len(trades)),
        "Başarı Oranı %": round(float(wins.mean() * 100), 1),
        "Ortalama Net Getiri %": round(float(trades["Net Getiri %"].mean()), 2),
        "Medyan Net Getiri %": round(float(trades["Net Getiri %"].median()), 2),
        "Toplam Bileşik Getiri %": round(float((equity.iloc[-1] - 1) * 100), 2),
        "Maksimum Düşüş %": round(max_dd, 2),
        "Kâr Faktörü": round(float(pf), 2) if np.isfinite(pf) else "∞",
    }
    equity_df = pd.DataFrame({"Strateji": equity.values}, index=pd.to_datetime(trades["Tarih"]))
    return {"summary": summary, "trades": trades, "equity": equity_df}


def walk_forward_optimize(
    frame: pd.DataFrame,
    market_score: int = 55,
    train_ratio: float = 0.70,
    max_combinations: int = 120,
) -> dict[str, Any]:
    if frame is None or len(frame) < 420:
        return {
            "leaderboard": pd.DataFrame(),
            "best_config": None,
            "train": {},
            "test": {},
        }

    train, test = _split_frame(frame, train_ratio)

    grid = product(
        [55, 60, 65],       # min_score
        [45, 55],           # max_risk
        [50, 60],           # min_confidence
        [1.5, 2.0, 2.5],    # atr_stop
        [1.5, 2.0, 2.5],    # target1
        [3.0, 3.5, 4.0],    # target2
        [1.5, 2.0, 2.5],    # trailing
    )

    rows: list[dict[str, Any]] = []
    for number, params in enumerate(grid):
        if number >= max_combinations:
            break
        min_score, max_risk, min_conf, stop, t1, t2, trailing = params
        if t2 <= t1:
            continue
        config = BacktestConfig(
            horizon=20,
            step=3,
            min_score=min_score,
            max_risk=max_risk,
            min_confidence=min_conf,
            fee_bps=20.0,
            atr_stop=stop,
            atr_target_1=t1,
            atr_target_2=t2,
            trailing_atr=trailing,
        )
        result = run_backtest(train, market_score=market_score, config=config)
        summary = result.get("summary", {})
        if not summary:
            continue
        rows.append({
            "Skor": objective(summary),
            "Min Spek": min_score,
            "Maks Risk": max_risk,
            "Min Güven": min_conf,
            "ATR Stop": stop,
            "Hedef 1": t1,
            "Hedef 2": t2,
            "Trailing": trailing,
            **summary,
        })

    leaderboard = pd.DataFrame(rows)
    if leaderboard.empty:
        return {
            "leaderboard": leaderboard,
            "best_config": None,
            "train": {},
            "test": {},
        }

    leaderboard = leaderboard.sort_values("Skor", ascending=False).reset_index(drop=True)
    best = leaderboard.iloc[0]
    best_config = BacktestConfig(
        horizon=20,
        step=3,
        min_score=int(best["Min Spek"]),
        max_risk=int(best["Maks Risk"]),
        min_confidence=int(best["Min Güven"]),
        fee_bps=20.0,
        atr_stop=float(best["ATR Stop"]),
        atr_target_1=float(best["Hedef 1"]),
        atr_target_2=float(best["Hedef 2"]),
        trailing_atr=float(best["Trailing"]),
    )

    train_result = run_backtest(train, market_score=market_score, config=best_config)
    raw_test = run_backtest(test, market_score=market_score, config=best_config)
    test_result = _filter_test_trades(raw_test, test.attrs["evaluation_start"])

    return {
        "leaderboard": leaderboard,
        "best_config": asdict(best_config),
        "train": train_result,
        "test": test_result,
        "train_end": str(train.index[-1])[:10],
        "test_start": str(test.attrs["evaluation_start"])[:10],
    }
