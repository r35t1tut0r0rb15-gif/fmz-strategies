"""Trendelicious: price (hl2) above a rising Donchian midline (risen two bars, not fallen for two
more) turns the trend up; the mirror turns it down. Up-trend is long, otherwise short (always in).
Port of FMZ strategy #363793 "Trendelicious".

Source
    https://www.fmz.com/strategy/363793 (PineScript v5, FMZ last modified 2022-05-17 13:47:42).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 61-103), length 30, price hl2, aggressive mode off
    PP = (highest(hl2, 30) + lowest(hl2, 30)) / 2;  d = change(PP)
    up   = hl2 > PP and d > 0 and d[1] > 0 and d[2] >= 0 and d[3] >= 0
    down = hl2 < PP and d < 0 and d[1] < 0 and d[2] <= 0 and d[3] <= 0
    uptrend = up ? true : down ? false : uptrend[1]
    uptrend -> entry long; else -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Aggressive mode defaults to false; its extra conditions are not ported.
    * uptrend starts false (a v5 bool history is false, not na), so the script is short from its
      first bar until the first up-trend; kept.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363793_trendelicious_midline_trend"
FAMILY = "donchian_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 30, 50],
}
DEFAULT_PARAMS = {"length": 30}


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
    price = (bars_df["high"] + bars_df["low"]) / 2
    pp = (price.rolling(n).max() + price.rolling(n).min()) / 2
    d = pp.diff()
    up = ((price > pp) & (d > 0) & (d.shift(1) > 0) & (d.shift(2) >= 0) & (d.shift(3) >= 0)).to_numpy()
    down = ((price < pp) & (d < 0) & (d.shift(1) < 0) & (d.shift(2) <= 0) & (d.shift(3) <= 0)).to_numpy()
    m = len(price)
    uptrend = np.zeros(m, dtype=bool)
    for i in range(m):
        uptrend[i] = True if up[i] else (False if down[i] else (uptrend[i - 1] if i else False))
    return _always_in(uptrend, ~uptrend, bars_df.index)


def portfolio_kwargs(**params):
    return {}
