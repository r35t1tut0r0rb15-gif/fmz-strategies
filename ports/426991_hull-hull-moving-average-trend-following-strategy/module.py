"""Two EMA directions (always in): EMA 13 and EMA 21 both rising goes long, both falling goes short.
Port of FMZ strategy #426991 "Hull Moving Average Trend Following Strategy".

Source
    https://www.fmz.com/strategy/426991 (PineScript v2/v3 syntax, FMZ last modified 2023-09-16 18:41:33).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 164-205), EMA 13 / 21
    direction = rising(ema, 2) ? 1 : falling(ema, 2) ? -1 : 0   (for EMA 13 and EMA 21)
    both 1 -> entry long;  both -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * rising(x, 2) is x above both of its 2 previous values (falling mirrored). The Hull MA,
      support / resistance and 720-minute security values only plot.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426991_two_ema_directions"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len0": [8, 13],
    "len02": [21, 34],
}
DEFAULT_PARAMS = {"len0": 13, "len02": 21}


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


def _dir(x):
    up = (x > x.shift(1)) & (x > x.shift(2))
    dn = (x < x.shift(1)) & (x < x.shift(2))
    return up, dn


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    u1, d1 = _dir(c.ewm(span=int(p["len0"]), adjust=False).mean())
    u2, d2 = _dir(c.ewm(span=int(p["len02"]), adjust=False).mean())
    return _always_in((u1 & u2).to_numpy(), (d1 & d2).to_numpy(), bars_df.index)


def portfolio_kwargs(**params):
    return {}
