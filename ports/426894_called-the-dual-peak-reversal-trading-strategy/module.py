"""HHLL reversed (always in): with "Trade reverse" on (source default), a high above the upper
envelope (SMA 29 of highs plus half the high-low SMA spread) goes long and a low below the lower
envelope goes short.
Port of FMZ strategy #426894 "Dual Peak Reversal Trading Strategy".

Source
    https://www.fmz.com/strategy/426894 (PineScript v5, FMZ last modified 2023-09-15 12:33:57).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 75-95), Len 29, reverse on
    hh = sma(high, 29); ll = sma(low, 29); m = (hh - ll) / 2
    pos = low < (ll - m)[1] ? 1 : high > (hh + m)[1] ? -1 : pos[1]
    possig = reverse ? -pos : pos;  entries on a change of possig

Interpretation choices (Pine rules in SURVEY_README.md)
    * The low test is checked first (it wins when both fire), then reversed: such a bar goes short.
    * The 2018 start date is a backtest window: dropped.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426894_hhll_reversed"
FAMILY = "ma_envelope_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 29, 40],
    "reverse": [True, False],
}
DEFAULT_PARAMS = {"length": 29, "reverse": True}


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
    h, l = bars_df["high"], bars_df["low"]
    hh, ll = h.rolling(n).mean(), l.rolling(n).mean()
    m = (hh - ll) / 2
    lo_break = (l < (ll - m).shift(1)).to_numpy()
    hi_break = (h > (hh + m).shift(1)).to_numpy()
    if p["reverse"]:
        return _always_in(hi_break & ~lo_break, lo_break, bars_df.index, short_first=True)
    return _always_in(lo_break, hi_break & ~lo_break, bars_df.index)


def portfolio_kwargs(**params):
    return {}
