"""TD setup count reaching 13: long after 13 closes below the close 4 bars back, short after 13
above (always in; the counts wrap 13 -> 1).
Port of FMZ strategy #361847 "Tom-DeMark-Sequential-Heat-Map" (Indicator-Jones, orders added).

Source
    https://www.fmz.com/strategy/361847 (PineScript v5, FMZ last modified 2022-05-08 17:29:16).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 164-181)
    buySetup  := close < close[4] ? (buySetup[1] == 13 ? 1 : buySetup[1] + 1) : 0
    sellSetup := close > close[4] ? (sellSetup[1] == 13 ? 1 : sellSetup[1] + 1) : 0
    buySetup == 13 -> entry long;  else sellSetup == 13 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * No backtest header: FREQ = "bar_size_pending" (rule 1).

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_361847_td_setup13_fade"
FAMILY = "td_sequential"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # source declares no bar size; set by the project before running
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [3, 4, 5],
    "count": [9, 13],
}
DEFAULT_PARAMS = {"lookback": 4, "count": 13}


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
    k, top = int(p["lookback"]), int(p["count"])
    c = bars_df["close"].to_numpy(dtype=float)
    m = len(c)
    buy = np.zeros(m, dtype=int)
    sell = np.zeros(m, dtype=int)
    for t in range(k, m):
        buy[t] = (1 if buy[t - 1] == top else buy[t - 1] + 1) if c[t] < c[t - k] else 0
        sell[t] = (1 if sell[t - 1] == top else sell[t - 1] + 1) if c[t] > c[t - k] else 0
    return _always_in(buy == top, sell == top, bars_df.index)


def portfolio_kwargs(**params):
    return {}
