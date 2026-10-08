"""Gaan EMA (always in): with EMA 27 above EMA 81 a close above EMA 9 goes long; with EMA 27 below
EMA 81 a close below EMA 9 goes short.
Port of FMZ strategy #426902 "Gaan EMA Golden Cross Strategy".

Source
    https://www.fmz.com/strategy/426902 (PineScript v2/v3 syntax, FMZ last modified 2023-12-01 14:57:55).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 131-158), EMA 9 / 27 / 81
    ema27 > ema81 and close > ema9 -> entry long
    ema27 < ema81 and close < ema9 -> entry short, close long (close < ema9), close short (close > ema9)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two closes sit inside the short block: there the long close repeats the short entry's
      reversal and the short close can never fire, so positions change only by reversal.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "2min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426902_gaan_ema"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 13],
    "mid": [27, 34],
    "slow": [81, 100],
}
DEFAULT_PARAMS = {"fast": 9, "mid": 27, "slow": 81}


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
    e = lambda n: c.ewm(span=int(n), adjust=False).mean()
    e9, e27, e81 = e(p["fast"]), e(p["mid"]), e(p["slow"])
    long_ = ((e27 > e81) & (c > e9)).to_numpy()
    short = ((e27 < e81) & (c < e9)).to_numpy()
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
