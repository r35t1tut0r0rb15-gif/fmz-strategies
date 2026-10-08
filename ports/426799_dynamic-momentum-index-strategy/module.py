"""CMO disparity index (HPotter, always in): the close's percent distance from EMA 20 above its
distance from EMA 200 goes short; below its distance from EMA 50 goes long.
Port of FMZ strategy #426799 "Dynamic Momentum Index Strategy".

Source
    https://www.fmz.com/strategy/426799 (PineScript v2/v3 syntax, FMZ last modified 2023-09-14 16:15:42).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 134-154), EMA 200 / 50 / 20
    res_n = 100 (close - ema(close, n)) / close
    pos = res20 > res200 ? -1 : res20 < res50 ? 1 : previous;  1 -> entry long, -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The -1 test comes first, as in the source. "Trade reverse" off.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "3h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426799_cmo_disparity"
FAMILY = "ma_envelope_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len_first": [100, 200],
    "len_second": [50, 30],
    "len_third": [20, 10],
}
DEFAULT_PARAMS = {"len_first": 200, "len_second": 50, "len_third": 20}


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
    res = lambda k: 100 * (c - c.ewm(span=int(k), adjust=False).mean()) / c
    r1, r2, r3 = res(p["len_first"]), res(p["len_second"]), res(p["len_third"])
    return _always_in((r3 < r2).to_numpy(), (r3 > r1).to_numpy(), bars_df.index, short_first=True)


def portfolio_kwargs(**params):
    return {}
