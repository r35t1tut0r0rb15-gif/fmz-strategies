"""Gann HiLo activator (Zer3192): after a close above the previous SMA 13 of highs the line is the
SMA 21 of lows, after a close below the previous SMA 21 of lows it is the SMA 13 of highs; the
close crossing above the line goes long, below goes short (always in).
Port of FMZ strategy #370655 "Gann High Low".

Source
    https://www.fmz.com/strategy/370655 (PineScript v5, author Zer3192, FMZ last modified
    2022-06-25 10:00:25). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 34-53), high period 13, low period 21
    HLd = close > sma(high, 13)[1] ? 1 : close < sma(low, 21)[1] ? -1 : 0;  HLv = last non-zero HLd
    HiLo = HLv == -1 ? sma(high, 13) : sma(low, 21)
    crossover(close, HiLo) -> entry long; else crossunder(close, HiLo) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * nz(sma)[1] is 0 before the SMA exists, as coded.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_370655_gann_hilo_cross"
FAMILY = "ma_envelope_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "h_period": [8, 13, 21],
    "l_period": [13, 21, 34],
}
DEFAULT_PARAMS = {"h_period": 13, "l_period": 21}


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
    c = bars_df["close"]
    sh = bars_df["high"].rolling(int(p["h_period"])).mean()
    sl = bars_df["low"].rolling(int(p["l_period"])).mean()
    hld = np.where(c > sh.fillna(0.0).shift(1), 1, np.where(c < sl.fillna(0.0).shift(1), -1, 0))
    hlv = np.zeros(len(hld))
    for i in range(len(hld)):
        hlv[i] = hld[i] if hld[i] != 0 else (hlv[i - 1] if i else 0)
    hilo = np.where(hlv == -1, sh.to_numpy(), sl.to_numpy())
    cv = c.to_numpy(dtype=float)
    lag = lambda a: np.concatenate([[np.nan], a[:-1]])
    buy = (cv > hilo) & (lag(cv) <= lag(hilo))
    sell = (cv < hilo) & (lag(cv) >= lag(hilo))
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
