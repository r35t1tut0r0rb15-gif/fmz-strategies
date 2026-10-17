"""Built-in Supertrend 3 / 10 flips, 1-hour bars, as written: a flip to up goes long, a flip to down goes short (reversing).
The three-candle exits are never sent (they close entry ids that do not exist).
Port of FMZ strategy #435233 "Sunny Supertrend Strategy" (Sunny Supertrend Strategy).

FMZ source id: 435233

Source
    https://www.fmz.com/strategy/435233 (PineScript v5, FMZ last modified 2023-12-13 14:40:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 120-190), factor 3, ATR 10; dates 2021 (the date range is replaced by true in the code)
    long = change(direction) < 0;  short = change(direction) > 0;  first signal of each kind -> entry "enter long" / "enter short"
    strategy.close("long", when = 3 red bars or flip down) / strategy.close("short", ...)   (ids "long" / "short" never opened)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes name the ids "long" / "short" while the entries are "enter long" / "enter short",
      and they are only reached on an entry bar: no exit, as written (the intended three-candle exits
      are owed). The memory flags only suppress repeats of the same flip, which cannot occur.
      strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR bands.
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

NAME = "fmz_435233_sunny_supertrend_flips"
FAMILY = "supertrend"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "atr_len": [10, 20],
}
DEFAULT_PARAMS = {"factor": 3.0, "atr_len": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _direction(h, lo, c, factor, n):
    """Direction of Pine's built-in supertrend(factor, atrPeriod): -1 up, 1 down."""
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
    return dr


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    dr = _direction(bars_df["high"], bars_df["low"], bars_df["close"], float(p["factor"]), int(p["atr_len"]))
    d1 = np.concatenate(([dr[0]], dr[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(dr - d1 < 0, index=ix), false, pd.Series(dr - d1 > 0, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
