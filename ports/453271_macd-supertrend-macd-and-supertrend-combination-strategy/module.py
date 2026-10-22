"""MACD 12 / 26 / 9 side with the Supertrend (10, 3), 1-hour bars: the MACD over its signal with the close over the Supertrend is long, under with the close under it is short; the MACD turning to the other side of its signal closes; reversing.
Port of FMZ strategy #453271 "MACD与Supertrend组合策略-MACD-and-Supertrend-Combination-Strategy" (MACD + Supertrend Strategy).

FMZ source id: 453271

Source
    https://www.fmz.com/strategy/453271 (PineScript v5, FMZ last modified 2024-06-03 16:35:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 80-144), MACD 12 / 26 / 9; Supertrend 10 / 3
    macd > signal and st < close -> entry Long;  signal > macd -> close Long;  signal > macd and st > close -> entry Short;  macd > signal -> close Short
    short condition -> close Long;  long condition -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * All tests are states. In call order a long condition enters (reversing a short, whose closes
      then find it reversed); the MACD under its signal closes a long, and with the close under the
      Supertrend it also opens the short (one reversal); the mirror for shorts. With the MACD on one
      side but the Supertrend against it, the trade on the other side is closed and the position
      stays flat. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD side with Supertrend confirmation.
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

NAME = "fmz_453271_macd_side_supertrend_confirm_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "st_len": [10, 14],
    "st_mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"st_len": 10, "st_mult": 3.0}


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


def _supertrend(h, lo, c, factor, n):
    """Pine's built-in supertrend(factor, atrPeriod): (direction -1 up / 1 down, line)."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub, st = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    dr = np.ones(m)
    for i in range(m):
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if np.isnan(atr[i]):
            lb[i], ub[i] = np.nan, np.nan
        if i == 0 or np.isnan(atr[i - 1]):
            dr[i] = 1
        elif st[i - 1] == ub[i - 1]:
            dr[i] = -1 if cv[i] > ub[i] else 1
        else:
            dr[i] = 1 if cv[i] < lb[i] else -1
        st[i] = lb[i] if dr[i] == -1 else ub[i]
    return dr, st


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    _, line = _supertrend(h, lo, c, float(p["st_mult"]), int(p["st_len"]))
    st = pd.Series(line, index=c.index)
    le = (macd > sig) & (st < c)
    se = (sig > macd) & (st > c)
    lx = (sig > macd) & ~se
    sx = (macd > sig) & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
