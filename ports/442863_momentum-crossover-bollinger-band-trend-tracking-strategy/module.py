"""SeaSide420's Hull crossover on ohlc4, 4-hour bars: from flat, the Hull line above its one-bar-lagged twin with the weighted cross score agreeing goes long, the mirror short; the opposite agreement closes.
Port of FMZ strategy #442863 "Momentum Crossover Bollinger Band Trend Tracking Strategy" (Hull Moving Average Crossover Strategy).

FMZ source id: 442863

Source
    https://www.fmz.com/strategy/442863 (PineScript v4, FMZ last modified 2024-02-26 16:52:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 131-168), HullMA cross 10 on ohlc4
    n1 = wma(2 wma(p, 5) - wma(p, 10), 3);  n2 = the same on p[1];  lc1 = (n1 - n1[3]) + (n1 - n2[4]) x 100;  lc2 = (n2 - n2[3]) + (n2 - n1[4]) x 100
    n1 < n2 and lc1 < lc2 -> close Long;  n1 > n2 and lc1 > lc2 -> close Short;  n1 > n2 and lc1 > lc2 and opentrades < 1 -> entry Long;  mirrored -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries need no open trade (opentrades < 1 at the bar), so a close on one bar is followed by
      an entry no earlier than the next bar. round(10 / 2) = 5 and round(sqrt(10)) = 3 as in Pine. No
      sizing code. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Hull line crossings with a cross score.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442863_seaside_hull_cross_score_flat_entries"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "keh": [10, 20],
}
DEFAULT_PARAMS = {"keh": 10}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _pine_round(x):
    return int(np.floor(x + 0.5))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    src = (o + h + lo + c) / 4
    k = int(p["keh"])
    diff = 2 * _wma(src, _pine_round(k / 2)) - _wma(src, k)
    n1 = _wma(diff, _pine_round(np.sqrt(k)))
    n2 = n1.shift(1)
    lc1 = (n1 - n1.shift(3)) + (n1 - n2.shift(4)) * 100
    lc2 = (n2 - n2.shift(3)) + (n2 - n1.shift(4)) * 100
    up = ((n1 > n2) & (lc1 > lc2)).to_numpy()
    dn = ((n1 < n2) & (lc1 < lc2)).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    held = 0
    for i in range(m):
        if held == 1 and dn[i]:
            lx[i] = True
        elif held == -1 and up[i]:
            sx[i] = True
        elif held == 0 and up[i]:
            le[i] = True
        elif held == 0 and dn[i]:
            se[i] = True
        held = 1 if le[i] else -1 if se[i] else 0 if (lx[i] or sx[i]) else held
    ix = bars_df.index
    return tuple(pd.Series(a, index=ix) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
