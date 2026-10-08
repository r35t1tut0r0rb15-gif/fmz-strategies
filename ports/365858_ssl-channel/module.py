"""SSL channel (channel 2: SMA 20 of highs / lows): a close above the high SMA after being below
the low SMA goes long; the mirror goes short (always in).
Port of FMZ strategy #365858 "SSL Channel".

Source
    https://www.fmz.com/strategy/365858 (PineScript v5, FMZ last modified 2022-05-26 12:19:48).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 67-148), channel 2: SMA 20 of high / SMA 20 of low,
wicks off
    Hlv2 := close > ma3 ? 1 : close < ma4 ? -1 : Hlv2[1]
    Hlv2 -1 -> 1 -> entry long; else 1 -> -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The orders use channel 2 (20 bars); channel 1 (200 bars) only draws and alerts.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "45min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365858_ssl_channel_flip"
FAMILY = "ma_envelope_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20, 50],
}
DEFAULT_PARAMS = {"length": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    c = bars_df["close"]
    up = (c > bars_df["high"].rolling(n).mean()).to_numpy()
    dn = (c < bars_df["low"].rolling(n).mean()).to_numpy()
    m = len(c)
    hlv = np.full(m, np.nan)
    for i in range(m):
        hlv[i] = 1.0 if up[i] else (-1.0 if dn[i] else (hlv[i - 1] if i else np.nan))
    prev = np.concatenate([[np.nan], hlv[:-1]])
    return _always_in((hlv == 1) & (prev == -1), (hlv == -1) & (prev == 1), bars_df.index)


def portfolio_kwargs(**params):
    return {}
