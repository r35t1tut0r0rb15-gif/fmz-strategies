"""Rolling Heikin Ashi over a tf-bar window: a red rolling candle (open above close) goes LONG and
a green one goes SHORT, as written (always in).
Port of FMZ strategy #362649 "Rolling Heikin Ashi Candles".

Source
    https://www.fmz.com/strategy/362649 (PineScript v4, FMZ last modified 2022-05-12 16:42:15).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 60-77), tf 5
    haclose = (open[tf-1] + highest(high, tf) + lowest(low, tf) + close) / 4
    haopen  = (open[tf-1] + close) / 2
    if not na(haopen[2*tf-1]): haopen := (haopen[2*tf-1] + haclose[tf]) / 2
    haopen > haclose -> entry "Enter Long"; else haopen < haclose -> entry "Enter Short"

Interpretation choices (Pine rules in SURVEY_README.md)
    * The direction is inverted relative to the candle colour (red -> long); kept as written.
    * haopen's history holds the reassigned values, so the recursion on haopen[2*tf-1] is kept.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "6h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362649_rolling_heikin_ashi_inverse"
FAMILY = "heikin_ashi_trend"  # proposed 2026-10-07, user to confirm
FREQ = "6h"  # backtest header period: 6h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tf": [3, 5, 8],
}
DEFAULT_PARAMS = {"tf": 5}


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
    tf = int(p["tf"])
    o_lag = bars_df["open"].shift(tf - 1)
    hc = ((o_lag + bars_df["high"].rolling(tf).max() + bars_df["low"].rolling(tf).min()
           + bars_df["close"]) / 4).to_numpy()
    ho = ((o_lag + bars_df["close"]) / 2).to_numpy()
    k = 2 * tf - 1
    for i in range(k, len(ho)):
        if not np.isnan(ho[i - k]):
            ho[i] = (ho[i - k] + hc[i - tf]) / 2
    return _always_in(ho > hc, ho < hc, bars_df.index)


def portfolio_kwargs(**params):
    return {}
