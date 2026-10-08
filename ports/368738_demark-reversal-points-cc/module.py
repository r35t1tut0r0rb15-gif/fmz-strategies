"""Demark reversal points [CC] (Zer3192 copy): nine consecutive closes below the close four bars
earlier (on the previous bar's close series) is a buy setup; the DRP turning positive goes long,
turning negative goes short (always in).
Port of FMZ strategy #368738 "Demark Reversal Points [CC]".

Source
    https://www.fmz.com/strategy/368738 (PineScript v5, author Zer3192, FMZ last modified
    2022-06-12 17:18:26). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 41-70), length 9, look-back 4, repainting off,
resolution ""
    src = request.security(chart, close)[1]
    uCount = #{i < 9: nz(src[i]) > nz(src[i + 4])};  dCount likewise with <
    drp = dCount == 9 ? 1 : uCount == 9 ? -1 : 0
    crossover(drp, 0) -> entry long; else crossunder(drp, 0) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Resolution "" is the chart, so (unlike #361719, rejected for its "18000" resolution) the
      series is defined; repainting off reads it one bar back ([1]). nz() as coded.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_368738_demark_reversal_points"
FAMILY = "td_sequential"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [6, 9, 13],
    "lb_length": [2, 4],
}
DEFAULT_PARAMS = {"length": 9, "lb_length": 4}


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
    n, lb = int(p["length"]), int(p["lb_length"])
    src = bars_df["close"].shift(1)
    nz = lambda s: s.fillna(0.0)
    up = sum((nz(src.shift(i)) > nz(src.shift(i + lb))).astype(int) for i in range(n))
    dn = sum((nz(src.shift(i)) < nz(src.shift(i + lb))).astype(int) for i in range(n))
    drp = np.where(dn == n, 1, np.where(up == n, -1, 0))
    prev = np.concatenate([[0], drp[:-1]])
    return _always_in((drp > 0) & (prev <= 0), (drp < 0) & (prev >= 0), bars_df.index)


def portfolio_kwargs(**params):
    return {}
