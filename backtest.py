from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import numpy as np
import pandas as pd
from engine import analyze_frame

@dataclass
class BacktestConfig:
    horizon: int = 20
    step: int = 3
    min_score: int = 60
    max_risk: int = 55
    min_confidence: int = 55
    fee_bps: float = 20.0
    atr_stop: float = 2.0
    atr_target_1: float = 2.0
    atr_target_2: float = 3.5
    trailing_atr: float = 2.0


def _atr(frame: pd.DataFrame, period: int = 14) -> pd.Series:
    prev = frame['Close'].shift(1)
    tr = pd.concat([
        frame['High'] - frame['Low'],
        (frame['High'] - prev).abs(),
        (frame['Low'] - prev).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def _max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    return float((equity / peak - 1).min() * 100)


def _simulate(frame: pd.DataFrame, idx: int, signal: dict[str, Any], cfg: BacktestConfig) -> dict[str, Any]:
    entry = float(frame['Close'].iloc[idx])
    atr_value = float(_atr(frame.iloc[:idx + 1]).iloc[-1])
    if not np.isfinite(atr_value) or atr_value <= 0:
        atr_value = entry * 0.02

    stop = entry - cfg.atr_stop * atr_value
    target1 = entry + cfg.atr_target_1 * atr_value
    target2 = entry + cfg.atr_target_2 * atr_value
    trail = stop
    remaining = 1.0
    realized = 0.0
    exit_price = entry
    exit_reason = 'Süre Sonu'
    first_target_hit = False
    end = min(idx + cfg.horizon, len(frame) - 1)

    for j in range(idx + 1, end + 1):
        high = float(frame['High'].iloc[j])
        low = float(frame['Low'].iloc[j])
        close = float(frame['Close'].iloc[j])
        trail = max(trail, close - cfg.trailing_atr * atr_value)

        if low <= trail:
            realized += remaining * (trail / entry - 1)
            exit_price = trail
            exit_reason = 'ATR / Hareketli Stop'
            remaining = 0.0
            break

        if not first_target_hit and high >= target1:
            realized += 0.5 * (target1 / entry - 1)
            remaining -= 0.5
            first_target_hit = True
            trail = max(trail, entry)

        if first_target_hit and high >= target2:
            realized += remaining * (target2 / entry - 1)
            exit_price = target2
            exit_reason = 'Hedef 2'
            remaining = 0.0
            break

        current = analyze_frame(frame.iloc[:j + 1], market_score=55)
        if current is not None and remaining > 0 and (current['Sınıf'] in {'D', 'R'} or current['Risk'] >= 70):
            realized += remaining * (close / entry - 1)
            exit_price = close
            exit_reason = 'Trend / Risk Bozulması'
            remaining = 0.0
            break

        exit_price = close

    if remaining > 0:
        realized += remaining * (exit_price / entry - 1)

    realized -= cfg.fee_bps / 10_000
    return {
        'Çıkış': exit_price,
        'Net Getiri %': realized * 100,
        'Çıkış Nedeni': exit_reason,
        'Hedef 1': target1,
        'Hedef 2': target2,
        'Başlangıç Stop': stop,
    }


def run_backtest(frame: pd.DataFrame, market_score: int = 55, config: BacktestConfig | None = None) -> dict[str, Any]:
    cfg = config or BacktestConfig()
    if frame is None or len(frame) < 220:
        return {'summary': {}, 'trades': pd.DataFrame(), 'equity': pd.DataFrame()}

    rows = []
    for idx in range(120, len(frame) - cfg.horizon - 1, max(cfg.step, 1)):
        signal = analyze_frame(frame.iloc[:idx + 1], market_score=market_score)
        if signal is None:
            continue
        if not (
            signal['Spek İz'] >= cfg.min_score
            and signal['Risk'] <= cfg.max_risk
            and signal['Güven'] >= cfg.min_confidence
            and signal['Sınıf'] in {'A', 'B', 'C+'}
        ):
            continue

        sim = _simulate(frame, idx, signal, cfg)
        rows.append({
            'Tarih': str(frame.index[idx])[:10],
            'Sınıf': signal['Sınıf'],
            'Karar': signal['Karar'],
            'Spek İz': signal['Spek İz'],
            'Güven': signal['Güven'],
            'Risk': signal['Risk'],
            'İşlem Kalitesi': signal['İşlem Kalitesi'],
            'Giriş': round(float(frame['Close'].iloc[idx]), 4),
            'Çıkış': round(sim['Çıkış'], 4),
            'Net Getiri %': round(sim['Net Getiri %'], 2),
            'Çıkış Nedeni': sim['Çıkış Nedeni'],
            'Hedef 1': round(sim['Hedef 1'], 4),
            'Hedef 2': round(sim['Hedef 2'], 4),
            'Başlangıç Stop': round(sim['Başlangıç Stop'], 4),
        })

    trades = pd.DataFrame(rows)
    if trades.empty:
        return {'summary': {}, 'trades': trades, 'equity': pd.DataFrame()}

    returns = trades['Net Getiri %'] / 100
    equity = (1 + returns).cumprod()
    wins = trades['Net Getiri %'] > 0
    gross_profit = trades.loc[wins, 'Net Getiri %'].sum()
    gross_loss = abs(trades.loc[~wins, 'Net Getiri %'].sum())
    pf = gross_profit / gross_loss if gross_loss > 0 else np.inf

    summary = {
        'İşlem Sayısı': int(len(trades)),
        'Başarı Oranı %': round(float(wins.mean() * 100), 1),
        'Ortalama Net Getiri %': round(float(trades['Net Getiri %'].mean()), 2),
        'Medyan Net Getiri %': round(float(trades['Net Getiri %'].median()), 2),
        'Toplam Bileşik Getiri %': round(float((equity.iloc[-1] - 1) * 100), 2),
        'Maksimum Düşüş %': round(_max_drawdown(equity), 2),
        'Kâr Faktörü': round(float(pf), 2) if np.isfinite(pf) else '∞',
    }
    equity_df = pd.DataFrame({'Strateji': equity.values}, index=pd.to_datetime(trades['Tarih']))
    return {'summary': summary, 'trades': trades, 'equity': equity_df}
