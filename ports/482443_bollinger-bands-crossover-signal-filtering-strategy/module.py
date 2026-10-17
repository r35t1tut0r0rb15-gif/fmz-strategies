"""Bollinger (55, 1) side switches, always in, two-hour bars: when the latest close outside the bands flips from below
the lower band to above the upper band go long, the reverse goes short.
Port of FMZ strategy #482443 "布林带交叉信号筛选交易策略-Bollinger-Bands-Crossover-Signal-Filtering-Strategy" (Bollinger Bands Filter [Strategy]).

FMZ source id: 482443

Source
    https://www.fmz.com/strategy/482443 (PineScript v5, FMZ last modified 2025-02-18 14:47:16).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 102-150), SMA 55, StdDev 1
    L1 = barssince(close > upper), S1 = barssince(close < lower)
    longSignal = L1 < S1 and not (L1 < S1)[1] -> entry long; shortSignal = S1 < L1 and not (S1 < L1)[1] -> short

Interpretation choices (Pine rules in SURVEY_README.md)
    * barssince is na until its event has happened once; a comparison with na is false (as Pine).
    * Entries reverse (REVERSAL INTENDED); always in. Signal module, no stops. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
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

NAME = "fmz_482443_bb55_last_side_switch_always_in"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [55, 30],
    "mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 55, "mult": 1.0}


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


def _barssince(cond):
    out = np.full(len(cond), np.nan)
    last = None
    for i, v in enumerate(cond):
        if v:
            last = i
        if last is not None:
            out[i] = i - last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = p["mult"] * c.rolling(n).std(ddof=0)
    l1 = _barssince((c > basis + dev).to_numpy())
    s1 = _barssince((c < basis - dev).to_numpy())
    lt = pd.Series(l1 < s1, index=c.index)
    st = pd.Series(s1 < l1, index=c.index)
    long_e = (lt & ~lt.shift(1, fill_value=False)).astype(bool)
    short_e = (st & ~st.shift(1, fill_value=False)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
