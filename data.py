from __future__ import annotations

import pandas as pd
import yfinance as yf


def flatten_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)
    return frame


def download_symbol(symbol: str, period: str = "2y") -> pd.DataFrame | None:
    symbol = symbol.strip().upper()
    try:
        frame = yf.download(
            f"{symbol}.IS",
            period=period,
            interval="1d",
            auto_adjust=True,
            progress=False,
            timeout=20,
        )
        frame = flatten_columns(frame).dropna()
        return frame if len(frame) >= 120 else None
    except Exception:
        return None


def download_market() -> pd.DataFrame | None:
    try:
        frame = yf.download(
            "XU100.IS",
            period="1y",
            interval="1d",
            auto_adjust=True,
            progress=False,
            timeout=20,
        )
        frame = flatten_columns(frame).dropna()
        return frame if len(frame) >= 60 else None
    except Exception:
        return None
