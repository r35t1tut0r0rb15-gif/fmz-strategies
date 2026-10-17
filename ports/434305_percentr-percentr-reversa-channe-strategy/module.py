"""Larry Williams' %R band, 1-hour bars, long only, as written: from flat, a 3-bar %R of the close between -87 and -20 goes
long, and on every bar that has a range (low under high) the long is closed, so each trade lasts one bar.
Port of FMZ strategy #434305 "反转PercentR连费通道策略PercentR-Reversa-Channe-Strategy" (Daily PercentR Strategy).

FMZ source id: 434305

Source
    https://www.fmz.com/strategy/434305 (PineScript v4, FMZ last modified 2023-12-05 12:04:13).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 140-172), %R length 3 on close, low marker -87, high marker -20; daily high / low / close / open fetched, unused
    percentR = 100 (close - highest(3)) / (highest(3) - lowest(3));  -87 < percentR < -20 -> entry long
    low < high -> close long ("exit at end of session")

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.close acts on the position held when the bar is calculated, so the close is issued on
      the bar after the fill (almost every bar has low < high) and the trade is held one bar; a new
      entry can follow on the bar the exit fills. The author's comment says the exit was meant for the
      session end: the intended version is owed. An entry while long is ignored.
    * The four daily security values are never used: dropped. The order size is computed but never
      passed. Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an oscillator band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the unused order-size line stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the per-bar close is not a session rule).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434305_percent_r_band_one_bar"
FAMILY = "williams_r_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [3, 7],
    "low_marker": [-87, -95],
}
DEFAULT_PARAMS = {"length": 3, "low_marker": -87, "high_marker": -20}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    pr = 100 * (c - hh) / (hh - ll).replace(0.0, np.nan)
    cond = ((pr < float(p["high_marker"])) & (pr > float(p["low_marker"]))).to_numpy()
    rng = (lo < h).to_numpy()
    m = len(cond)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0  # position held on bar i (filled at its open)
    for i in range(m):
        nxt = pos
        if pos == 0 and cond[i]:
            le[i] = True
            nxt = 1
        elif pos == 1 and rng[i]:
            lx[i] = True
            nxt = 0
        pos = nxt
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
