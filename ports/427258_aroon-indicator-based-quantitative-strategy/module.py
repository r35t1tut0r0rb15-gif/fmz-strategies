"""Noro's Aroon v1.0, long only by default: Aroon up above Aroon down (7 bars) goes long; Aroon down
above Aroon up closes the long (the short side is off, so its entry only closes the long).
Port of FMZ strategy #427258 "Aroon Indicator Based Quantitative Strategy".

FMZ source id: 427258

Source
    https://www.fmz.com/strategy/427258 (PineScript v2, FMZ last modified 2023-09-19 15:47:21).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 174-205), length 7, long on, short off
    upper = 200 (highestbars(high, 8) + 7) / 7; lower = 200 (lowestbars(low, 8) + 7) / 7
    upper > lower -> entry long; upper < lower -> entry short with qty 0 (needshort off)
    if true -> strategy.close_all()

Interpretation choices (Pine rules in SURVEY_README.md; Noro's template as worker A's ports)
    * The short side is off, so its entry has qty 0 and only closes the long (Noro's idiom).
    * `if true -> close_all()` is Noro's backtest-window close (`if time > timestamp(to year,
      month, day)`) whose condition FMZ's converter replaced by true; it is the author's backtest
      window, dropped (taken literally it would close every position one bar after it opens:
      decision owed if the project wants that version).
    * highestbars / lowestbars over 8 bars (length + 1, current bar included); on ties the most
      recent bar wins.
    * Long only.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bar counts only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427258_noro_aroon_long"
FAMILY = "momentum_breakout"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [7, 14, 25],
}
DEFAULT_PARAMS = {"length": 7}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _bars_since_extreme(v, w, highest):
    """Pine highestbars / lowestbars over w bars (current included): offset <= 0 of the extreme,
    the most recent bar on ties; nan before w bars exist."""
    m = len(v)
    out = np.full(m, np.nan)
    for t in range(w - 1, m):
        best, off = v[t], 0
        for k in range(1, w):
            x = v[t - k]
            if (x > best) if highest else (x < best):
                best, off = x, -k
        out[t] = off
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    n = int({**DEFAULT_PARAMS, **params}["length"])
    hi = _bars_since_extreme(bars_df["high"].to_numpy(dtype=float), n + 1, True)
    lo = _bars_since_extreme(bars_df["low"].to_numpy(dtype=float), n + 1, False)
    upper = 200 * (hi + n) / n
    lower = 200 * (lo + n) / n
    up, dn = upper > lower, upper < lower
    m = len(up)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and up[i]:
            le[i], pos = True, 1
        elif pos == 1 and dn[i]:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
