"""An ATR 10 x 1 trailing line of closes (UT Bot style), 3-hour bars, long only: the close crossing up through the line goes long, the line crossing up through the close closes.
Port of FMZ strategy #489301 "Quantitative Long Short Trend Tracking Dynamic Stop Loss Strategy" (ducanhmaster v1).

FMZ source id: 489301

Source
    https://www.fmz.com/strategy/489301 (PineScript v6, FMZ last modified 2025-04-03 11:34:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 141-204), key 1; ATR 10; Heikin-Ashi source off; commission 0.1, slippage 3; 100 % of equity
    trail := both closes over prev ? max(prev, close - atr) : both under ? min(prev, close + atr) : close > prev ? close - atr : close + atr
    close > trail and crossover(close, trail) -> entry long;  close < trail and crossover(trail, close) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail is the script's recursion with nz(previous, 0), in a loop; ema(close, 1) is the close. Long
      only. The commission and slippage are costs. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR trailing-line crossings.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity, commission and slippage stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489301_ut_atr10_trail_line_cross_long"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "a": [1.0, 2.0],
    "c": [10, 20],
}
DEFAULT_PARAMS = {"a": 1.0, "c": 10}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    nl = (_rma(tr, int(p["c"])) * float(p["a"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ts = np.full(m, np.nan)
    for i in range(m):
        prev = ts[i - 1] if i >= 1 and not np.isnan(ts[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        if cv[i] > prev and c1 > prev:
            ts[i] = max(prev, cv[i] - nl[i])
        elif cv[i] < prev and c1 < prev:
            ts[i] = min(prev, cv[i] + nl[i])
        else:
            ts[i] = cv[i] - nl[i] if cv[i] > prev else cv[i] + nl[i]
    t = pd.Series(ts, index=c.index)
    le = (c > t) & (c.shift(1) <= t.shift(1))
    lx = (c < t) & (t.shift(1) <= c.shift(1)) & ~le
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
