"""Double-smoothed stochastic (DSS Bressert) states, 2-hour bars: the 5-bar trigger above the DSS and over 80 reads long, the trigger under the DSS and under 20 reads short (as written); the state holds
between; reversing.
Port of FMZ strategy #441102 "Dual Smoothed Stochastic Bressert Strategy" (DSS Bressert).

FMZ source id: 441102

Source
    https://www.fmz.com/strategy/441102 (PineScript v2, FMZ last modified 2024-02-05 15:57:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 149-181), PDS 10, EMA 9, trigger 5; levels 80 / 20; reverse off
    xPreCalc = ema(stoch(close, high, low, 10), 9);  xDSS = ema(stoch(xPreCalc, xPreCalc, xPreCalc, 10), 9);  xTrigger = ema(xDSS, 5)
    pos = xTrigger < xDSS and xTrigger < 20 ? -1 : xTrigger > xDSS and xTrigger > 80 ? 1 : pos[1];  1 -> entry Long, -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The states are ported as written (the trigger under the DSS in the low zone reads short, above it in
      the high zone long). strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "2h" from the
      backtest header (bars on UTC multiples of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, double-smoothed stochastic states.
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

NAME = "fmz_441102_dss_bressert_zone_state_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pds": [10, 14],
    "ema_len": [9, 5],
}
DEFAULT_PARAMS = {"pds": 10, "ema_len": 9, "trigger_len": 5, "overbought": 80, "oversold": 20, "reverse": False}


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


def _stoch(x, hi, lo, n):
    ll, hh = lo.rolling(n).min(), hi.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        return 100.0 * (x - ll) / (hh - ll).where(hh > ll)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, e = int(p["pds"]), int(p["ema_len"])
    pre = _stoch(c, h, lo, n).ewm(span=e, adjust=False).mean()
    dss = _stoch(pre, pre, pre, n).ewm(span=e, adjust=False).mean()
    trg = dss.ewm(span=int(p["trigger_len"]), adjust=False).mean()
    dn = ((trg < dss) & (trg < float(p["oversold"]))).to_numpy()
    up = ((trg > dss) & (trg > float(p["overbought"]))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if dn[i]:
            pos = -1
        elif up[i]:
            pos = 1
        tgt[i] = pos
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
