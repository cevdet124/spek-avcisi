from __future__ import annotations

import numpy as np
import pandas as pd


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    diff = close.diff()
    up = diff.clip(lower=0)
    down = -diff.clip(upper=0)
    avg_up = up.ewm(alpha=1 / period, adjust=False).mean()
    avg_down = down.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_up / avg_down.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    prev = close.shift(1)
    tr = pd.concat(
        [(high - low), (high - prev).abs(), (low - prev).abs()],
        axis=1,
    ).max(axis=1)
    return tr.rolling(period).mean()


def mfi(high, low, close, volume, period: int = 14):
    typical = (high + low + close) / 3
    raw = typical * volume
    direction = typical.diff()
    pos = raw.where(direction > 0, 0.0)
    neg = raw.where(direction < 0, 0.0).abs()
    ratio = pos.rolling(period).sum() / neg.rolling(period).sum().replace(0, np.nan)
    return 100 - (100 / (1 + ratio))


def cmf(high, low, close, volume, period: int = 20):
    spread = (high - low).replace(0, np.nan)
    multiplier = (((close - low) - (high - close)) / spread).replace(
        [np.inf, -np.inf], 0
    ).fillna(0)
    return (multiplier * volume).rolling(period).sum() / volume.rolling(period).sum().replace(0, np.nan)


def obv(close, volume):
    return (np.sign(close.diff()).fillna(0) * volume).cumsum()


def ad_line(high, low, close, volume):
    spread = (high - low).replace(0, np.nan)
    multiplier = (((close - low) - (high - close)) / spread).replace(
        [np.inf, -np.inf], 0
    ).fillna(0)
    return (multiplier * volume).cumsum()


def bollinger_width(close, period: int = 20, std_mult: float = 2.0):
    ma = close.rolling(period).mean()
    std = close.rolling(period).std()
    upper = ma + std_mult * std
    lower = ma - std_mult * std
    return ((upper - lower) / ma.replace(0, np.nan)) * 100


def macd(close):
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    line = ema12 - ema26
    signal = line.ewm(span=9, adjust=False).mean()
    return line, signal, line - signal
