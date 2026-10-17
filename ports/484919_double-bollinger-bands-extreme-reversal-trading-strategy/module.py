"""Double Bollinger reversals, 1-hour bars: the close crossing back above the 3-sigma lower band goes long and leaves on
a cross above the 2-sigma upper band; the close crossing back below the 3-sigma upper band goes short and leaves on a
cross below the 2-sigma lower band.
Port of FMZ strategy #484919 "双布林带极值反转交易策略-Double-Bollinger-Bands-Extreme-Reversal-Trading-Strategy" (Double Bollinger Bands Strategy with Signals (By Rolwin)).

FMZ source id: 484919

Source
    https://www.fmz.com/strategy/484919 (PineScript v5, FMZ last modified 2025-03-05 10:10:08).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 197-226), BB 20 with 2 / 3 standard deviations
    crossover(close, lower3) -> entry long;  crossunder(close, upper3) -> entry short
    crossover(close, upper2) -> close long;  crossunder(close, lower2) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Closes act on the position held at the bar's start and never undo an entry on that bar (#430850); entries
      reverse (REVERSAL INTENDED).
    * FREQ = "1h" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_484919_double_bollinger_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "outer_mult": [3.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "inner_mult": 2.0, "outer_mult": 3.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _xover(a, b):
    return ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up1, lo1 = basis + p["inner_mult"] * sd, basis - p["inner_mult"] * sd
    up2, lo2 = basis + p["outer_mult"] * sd, basis - p["outer_mult"] * sd
    go_l, go_s = _xover(c, lo2), _xover(up2, c)
    out_l, out_s = _xover(c, up1), _xover(lo1, c)
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if go_l[i]:
            pos = 1
        if go_s[i]:
            pos = -1
        if out_l[i] and start == 1 and pos == 1:
            pos = 0
        if out_s[i] and start == -1 and pos == -1:
            pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
