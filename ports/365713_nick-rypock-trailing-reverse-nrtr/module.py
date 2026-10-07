"""Nick Rypock Trailing Reverse (NRTR): a close-based 2 % trailing reverse level; the close
falling 2 % below the highest close since the last reversal turns short, rising 2 % above the
lowest close turns long (always in).
Port of FMZ strategy #365713 "Nick Rypock Trailing Reverse".

Source
    https://www.fmz.com/strategy/365713 (PineScript v4, FMZ last modified 2022-05-25 18:14:32).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 53-115), coefficient 2 %
    trend >= 0: hp = max close; nrtr = hp * 0.98; close <= nrtr -> trend -1, lp = close
    trend < 0:  lp = min close; nrtr = lp * 1.02; close > nrtr -> trend 1, hp = close
    trend -1 -> 1 -> entry long; trend 1 -> -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The reversal level is checked on closes and reverses the position: it is the strategy's
      signal (an always-in reversal), not a protective stop, so no stop mark applies.
    * trend starts 0 and counts as up; the first down-turn is not an entry (trend[1] is 0).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365713_nrtr_close_reverse"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "k_pct": [1.0, 2.0, 3.0, 5.0],
}
DEFAULT_PARAMS = {"k_pct": 2.0}


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
    pct = p["k_pct"] * 0.01
    c = bars_df["close"].to_numpy(dtype=float)
    m = len(c)
    trend = np.zeros(m, dtype=int)
    t = 0
    hp = lp = c[0] if m else np.nan
    for i in range(m):
        if t >= 0:
            hp = max(hp, c[i])
            if c[i] <= hp * (1 - pct):
                t, lp = -1, c[i]
        else:
            lp = min(lp, c[i])
            if c[i] > lp * (1 + pct):
                t, hp = 1, c[i]
        trend[i] = t
    prev = np.concatenate([[0], trend[:-1]])
    return _always_in((trend == 1) & (prev == -1), (trend == -1) & (prev == 1), bars_df.index)


def portfolio_kwargs(**params):
    return {}
