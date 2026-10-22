"""Crossings of two volatility stops (ATR 20 x 1.5 and ATR 20 x 3), 3-hour bars: the small stop crossing over the big one goes long, crossing under goes short; reversing.
Port of FMZ strategy #469617 "Volatility Stop Cloud Strategy with Moving Average Crossover System" (ATR (VStop) Cloud Strategy).

FMZ source id: 469617

Source
    https://www.fmz.com/strategy/469617 (PineScript v5, FMZ last modified 2024-10-14 11:42:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 136-199), volStop(close, 20, 3.0) and volStop(close, 20, 1.5) (TradingView's Volatility Stop logic); display inputs only colour
    crossover(vstop_small, vstop_big) -> entry Long;  crossunder -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The volatility stop follows the built-in logic as written: running max / min of the close since the
      last flip, the stop ratcheting by ATR x factor (the true range while the ATR is na; the close on
      the first bar), a flip resetting max / min and the stop. There is no exit: positions end at the
      opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "3h" from the backtest header
      (UTC-aligned 3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volatility-stop crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_469617_small_vs_big_volatility_stop_cross_reversal"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 14],
    "factor_small": [1.5, 1.0],
    "factor_big": [3.0, 4.0],
}
DEFAULT_PARAMS = {"length": 20, "factor_small": 1.5, "factor_big": 3.0}


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


def _vstop(bars_df, n, factor):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr = tr.where(pc.notna())                         # ta.tr is na on the first bar
    atr = _rma(tr, int(n)).to_numpy()
    trv, cv = tr.to_numpy(), c.to_numpy(dtype=float)
    m = len(cv)
    out = np.full(m, np.nan)
    mx = mn = cv[0] if m else np.nan
    up, stop, prev_up = True, 0.0, True
    for i in range(m):
        a = atr[i] * factor if not np.isnan(atr[i]) else trv[i]
        mx, mn = max(mx, cv[i]), min(mn, cv[i])
        if np.isnan(stop) or np.isnan(a):
            s = np.nan                            # math.max / min with an na give na
        else:
            s = max(stop, mx - a) if up else min(stop, mn + a)
        stop = cv[i] if np.isnan(s) else s
        up = cv[i] - stop >= 0.0
        if up != prev_up:
            mx = mn = cv[i]
            stop = mx - a if up else mn + a
        prev_up = up
        out[i] = stop
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    big = _vstop(bars_df, p["length"], float(p["factor_big"]))
    small = _vstop(bars_df, p["length"], float(p["factor_small"]))
    le = (small > big) & (small.shift(1) <= big.shift(1))
    se = (small < big) & (small.shift(1) >= big.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
