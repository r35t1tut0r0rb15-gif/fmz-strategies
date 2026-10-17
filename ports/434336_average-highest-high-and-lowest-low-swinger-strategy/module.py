"""Average highest-high / lowest-low lines, 1-minute bars: a close above the 9-bar and 26-bar channel midpoints and above
their average and the 52-bar midpoint (both of those taken 26 bars back) goes long; a close below all four goes short;
held otherwise and reversed on the opposite condition.
Port of FMZ strategy #434336 "Average Highest High and Lowest Low Swinger Strategy" (Avg HH/LL Crypto Swinger).

FMZ source id: 434336

Source
    https://www.fmz.com/strategy/434336 (PineScript v4, FMZ last modified 2023-12-05 16:34:01).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 161-183), fast 9, slow 26
    c = mid(9);  f = mid(26);  g = ((c + f) / 2)[26];  h = mid(52)[26]   (mid(n) = (highest(n) + lowest(n)) / 2)
    close above c, f, g and h -> entry long;  close below all four -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest / lowest use the bar highs / lows and include the current bar (Pine's default).
      strategy.entry reverses: REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel midpoints.
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

NAME = "fmz_434336_avg_hh_ll_swinger"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 20],
    "slow": [26, 52],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 26}


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
    h, lo, cl = bars_df["high"], bars_df["low"], bars_df["close"]
    mid = lambda n: (h.rolling(n).max() + lo.rolling(n).min()) / 2  # noqa: E731
    a, b = int(p["fast"]), int(p["slow"])
    c, f = mid(a), mid(b)
    g = ((c + f) / 2).shift(b)
    hh = mid(2 * b).shift(b)
    lc = ((cl > c) & (cl > f) & (cl > g) & (cl > hh)).to_numpy()
    sc = ((cl < c) & (cl < f) & (cl < g) & (cl < hh)).to_numpy()
    m = len(lc)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if lc[i]:
            q = 1
        elif sc[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
