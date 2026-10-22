"""Close side of Tillson's T3 (5, 0.7), 1-hour bars: a close above the T3 holds a long, below it a short; reversing; the entry is sent on every bar of the state.
Port of FMZ strategy #439268 "基于T3指标的趋势追踪交易策略Trend-Following-Trading-Strategy-Based-on-T3-Indicator" (T3 Averages).

FMZ source id: 439268

Source
    https://www.fmz.com/strategy/439268 (PineScript v2, FMZ last modified 2024-01-18 16:21:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 128-180), Length 5; b 0.7; trade reverse off
    T3 = c1 xe6 + c2 xe5 + c3 xe4 + c4 xe3 (six chained EMAs 5, Tillson coefficients of b);  pos = T3 > close ? -1 : T3 < close ? 1 : previous pos (0 at the start)
    possig == 1 -> entry Long;  possig == -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The EMAs follow Pine's ema (seeded with the first value). A same-side entry while in the position
      is ignored. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close / T3 side.
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

NAME = "fmz_439268_hpotter_t3_close_side"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [5, 10],
    "b": [0.7, 0.5],
}
DEFAULT_PARAMS = {"length": 5, "b": 0.7}


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
    c = bars_df["close"]
    n, b = int(p["length"]), float(p["b"])
    xe = [c]
    for _ in range(6):
        xe.append(xe[-1].ewm(span=n, adjust=False).mean())
    c1 = -b * b * b
    c2 = 3 * b * b + 3 * b * b * b
    c3 = -6 * b * b - 3 * b - 3 * b * b * b
    c4 = 1 + 3 * b + b * b * b + 3 * b * b
    t3 = (c1 * xe[6] + c2 * xe[5] + c3 * xe[4] + c4 * xe[3]).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if t3[i] > cv[i]:
            pos = -1
        elif t3[i] < cv[i]:
            pos = 1
        tgt[i] = pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(tgt == 1, index=ix), false, pd.Series(tgt == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
