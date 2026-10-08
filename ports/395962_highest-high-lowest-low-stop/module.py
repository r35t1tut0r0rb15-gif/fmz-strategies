"""Highest-high / lowest-low stop (Zer3192): from flat, three higher closes in a row go long and three
lower closes go short; the long is stopped at the lowest low of the previous 20 bars, the short at
the highest high.
Port of FMZ strategy #395962 "Highest high/lowest low stop".

Source
    https://www.fmz.com/strategy/395962 (PineScript v4, author Zer3192, FMZ last modified
    2023-01-07 21:10:04). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 26-70), look-backs 20 / 20
    flat and close > close[1] > close[2] > close[3] -> entry long
    flat and close < close[1] < close[2] < close[3] -> entry short
    long: exit(stop = lowest(low, 20)[1]);  short: exit(stop = highest(high, 20)[1])  (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop level is re-set every bar (a moving stop): rule 2, mark trailing_stop_pending. The
      port fixes it at the signal bar's level: sl_stop = distance from the close to that level,
      shifted one bar inside stops(); vbt re-bases it on the fill price.
    * Entries need a flat position: simulate() mirrors the engine's fixed stop; opposite entries
      cannot occur (portfolio_kwargs upon_opposite_entry="ignore", rule 6).
    * No bar size in the source: FREQ = "bar_size_pending" (rule 1, 2026-10-07).

Marks: bar_size_pending, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_395962_three_closes_hl_stop"
FAMILY = "momentum_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # no bar size in the source (rule 1, 2026-10-07)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "hi_len": [10, 20, 40],
    "lo_len": [10, 20, 40],
}
DEFAULT_PARAMS = {"hi_len": 20, "lo_len": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _plan(bars_df, p):
    c = bars_df["close"]
    up = ((c > c.shift(1)) & (c.shift(1) > c.shift(2)) & (c.shift(2) > c.shift(3))).to_numpy()
    dn = ((c < c.shift(1)) & (c.shift(1) < c.shift(2)) & (c.shift(2) < c.shift(3))).to_numpy()
    lo = bars_df["low"].rolling(int(p["lo_len"])).min().shift(1)
    hi = bars_df["high"].rolling(int(p["hi_len"])).max().shift(1)
    lfrac = ((c - lo) / c).to_numpy()
    sfrac = ((hi - c) / c).to_numpy()
    o, h, l = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(c)
    le, se, frac = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool), np.full(m, np.nan)
    pos, pending, f, stop = 0, 0, np.nan, np.nan
    for i in range(m):
        if pending:
            pos, pending = pending, 0
            stop = o[i] * (1 - pos * f)
        if pos == 1 and l[i] <= stop:
            pos = 0
        elif pos == -1 and h[i] >= stop:
            pos = 0
        if pos == 0 and not pending:
            if up[i] and lfrac[i] > 0:
                le[i], pending, f = True, 1, lfrac[i]
            elif dn[i] and sfrac[i] > 0:
                se[i], pending, f = True, -1, sfrac[i]
            frac[i] = f if (le[i] or se[i]) else np.nan
    return le, se, frac


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _plan(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, frac = _plan(bars_df, p)
    return {"sl_stop": pd.Series(frac, index=bars_df.index).shift(1)}


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
