"""Andean oscillator (length 50): the bull component above the bear component goes long, below goes short, always
in, hourly bars.
Port of FMZ strategy #482454 "Adaptive-Trend-Detection-Strategy-with-Dual-Envelope-EMA-System-基于双包络EMA系统的自适应趋势检测策略" (Andean Oscillator [Strategy]).

FMZ source id: 482454

Source
    https://www.fmz.com/strategy/482454 (PineScript v5, FMZ last modified 2025-02-18 15:06:49).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 113-158), length 50 (alpha = 2 / 51)
    up1 = max(C, O, up1[1] - (up1[1] - C) alpha), up2 the same on squares; dn1 = min(C, O, dn1[1] + (C - dn1[1])
    alpha), dn2 on squares (var, starting at 0)
    bull = sqrt(dn2 - dn1^2), bear = sqrt(up2 - up1^2)
    bull > bear -> entry long; bear > bull -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The envelopes start from the var value 0, as written (dn1 / dn2 start near zero and recover over the first
      bars). The signal line feeds no order.
    * Every bar in a state is an entry signal (same-side ignored while held); entries reverse (REVERSAL INTENDED),
      always in. Signal module, no stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, exponential envelopes of prices and squared prices.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482454_andean_bull_bear_always_in"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 100],
}
DEFAULT_PARAMS = {"length": 50}


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
    a = 2.0 / (int(p["length"]) + 1)
    cv, ov = bars_df["close"].to_numpy(dtype=float), bars_df["open"].to_numpy(dtype=float)
    m = len(cv)
    bull, bear = np.full(m, np.nan), np.full(m, np.nan)
    up1 = up2 = dn1 = dn2 = 0.0
    for i in range(m):
        c, o = cv[i], ov[i]
        up1 = max(c, o, up1 - (up1 - c) * a)
        up2 = max(c * c, o * o, up2 - (up2 - c * c) * a)
        dn1 = min(c, o, dn1 + (c - dn1) * a)
        dn2 = min(c * c, o * o, dn2 + (c * c - dn2) * a)
        vb, vr = dn2 - dn1 * dn1, up2 - up1 * up1
        bull[i] = np.sqrt(vb) if vb >= 0 else np.nan     # sqrt of a negative is na in Pine
        bear[i] = np.sqrt(vr) if vr >= 0 else np.nan
    idx = bars_df.index
    long_e = pd.Series(bull > bear, index=idx)
    short_e = pd.Series(bear > bull, index=idx)
    false = pd.Series(False, index=idx)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
