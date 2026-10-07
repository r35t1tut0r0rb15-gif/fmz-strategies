"""Pivot-based trailing maxima / minima (LuxAlgo): a confirmed 14-bar pivot low goes long, a
confirmed pivot high goes short (always in); the trailing max / min lines only draw.
Port of FMZ strategy #365719 "Pivot Based Trailing Maxima & Minima [LUX]".

Source
    https://www.fmz.com/strategy/365719 (PineScript v5, FMZ last modified 2022-05-25 18:18:49).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 69-138), length 14
    ph = pivothigh(14, 14); pl = pivotlow(14, 14)
    pl -> entry long; else ph -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pivots are confirmed 14 bars after the pivot bar (no look-ahead). A pivot value of 0
      counts as none (Pine float-as-bool).
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365719_lux_pivot_reverse"
FAMILY = "pivot_reversal"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [5, 10, 14, 20],
}
DEFAULT_PARAMS = {"length": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _pivots(x, left, right, high):
    """ta.pivothigh/pivotlow(x, left, right): value of the pivot confirmed on each bar (NaN if
    none); the centre bar t-right strictly beyond the `left` bars before and `right` bars after."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    for t in range(left + right, len(v)):
        c = t - right
        side = np.concatenate([v[c - left:c], v[c + 1:t + 1]])
        if np.isnan(v[c]) or np.isnan(side).any():
            continue
        if (high and v[c] > side.max()) or (not high and v[c] < side.min()):
            out[t] = v[c]
    return out


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
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    ph = _pivots(bars_df["high"], n, n, True)
    pl = _pivots(bars_df["low"], n, n, False)
    long_ = ~np.isnan(pl) & (np.nan_to_num(pl) != 0)
    short = ~np.isnan(ph) & (np.nan_to_num(ph) != 0)
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
