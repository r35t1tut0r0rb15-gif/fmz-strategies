"""Supertrend (3, ATR 14) flips, 1-hour bars: the direction turning up goes long, turning down goes short; reversing. The ATR bracket re-sent every bar from the current close is not ported (pending).
Port of FMZ strategy #455364 "Dynamic Optimized Supertrend Trading Strategy" (Optimized Supertrend Strategy).

FMZ source id: 455364

Source
    https://www.fmz.com/strategy/455364 (PineScript v5, FMZ last modified 2024-06-28 15:23:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-186), Supertrend factor 3, ATR 14; stop 1 ATR, target 2 ATR from the current close (every bar)
    change(direction) < 0 -> entry Buy;  change(direction) > 0 -> entry Sell;  in a trade: exit(stop = close -+ atr, limit = close +- 2 atr) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend's direction is -1 in an up trend, so a fall in it is the turn up. The bracket is
      re-sent on every bar from that bar's close, so its levels move with the price; stops() cannot
      express this: it is not ported and the module gets the mark trailing_stop_pending (as #438034);
      positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the per-bar bracket pending (mark).
    2 generic: PASS, Supertrend flips.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_455364_supertrend3_14_flip_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_len": [14, 10],
    "factor": [3.0, 2.0],
}
DEFAULT_PARAMS = {"atr_len": 14, "factor": 3.0}


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
    d, _ = _supertrend(h, lo, c, float(p["factor"]), int(p["atr_len"]))
    ds = pd.Series(d, index=c.index).diff()
    false = pd.Series(False, index=bars_df.index)
    return ds < 0, false, ds > 0, false.copy()


def portfolio_kwargs(**params):
    return {}
