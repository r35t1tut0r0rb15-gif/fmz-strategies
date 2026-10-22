"""Bollinger 34 / 2 states, 2-hour bars: a close over the 2-deviation upper band is long, under the lower band is short; reversing.
Port of FMZ strategy #455366 "Enhanced Dynamic Bollinger Bands Trading Strategy" (Bollinger Bands (MBB, Madrid 2-deviation states)).

FMZ source id: 455366

Source
    https://www.fmz.com/strategy/455366 (PineScript v5, FMZ last modified 2024-06-28 15:31:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 119-161), SMA 34; 1 and 2 SD bands (the 1 SD bands plotted only)
    close > upper2 -> entry Long;  close < lower2 -> entry Short;  close <= lower2 -> close Long;  close >= upper2 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are called before the closes; an opposite entry reverses and the close then finds the
      trade reversed, so the closes only act on a close exactly at a band. REVERSAL INTENDED. No sizing
      code. FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, two-deviation band states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND455366 (2 members, best partner #473235, Jaccard 0.779); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_455366_bollinger34_two_sd_state_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [34, 20],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 34, "mult": 2.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, lo = (basis + dev).to_numpy(), (basis - dev).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    with np.errstate(invalid="ignore"):
        el, es, xl, xs = cv > up, cv < lo, cv <= lo, cv >= up
    for i in range(m):
        cur = pos
        if el[i] and cur != 1:
            cur = 1
        if es[i] and cur != -1:
            cur = -1
        if xl[i] and pos == 1 and cur == 1:
            cur = 0
        if xs[i] and pos == -1 and cur == -1:
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
