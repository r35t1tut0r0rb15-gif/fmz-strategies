"""CC-Trend 2, short only: with EMA 21 below EMA 55 and the previous close under the 100-bar high of
the EMA 9 / 55 envelope, go short; the close crossing above EMA 200 while the short is not losing, or
the previous close rising above the 23.6 % Fibonacci retracement line, closes it.
Port of FMZ strategy #427528 "Short-term Down Trend Strategy Based on EMA and Adaptive Fibonacci Retracement".

FMZ source id: 427528

Source
    https://www.fmz.com/strategy/427528 (PineScript v5, FMZ last modified 2023-09-21 21:36:16).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 156-218), Fibonacci length 100
    highF = highest(max(ema55, ema9), 100); lowF = lowest(min(ema55, ema9), 100); L236 = highF - 0.236 (highF - lowF)
    short = close[1] < highF and ema21 < ema55 -> entry short
    crossover(close, ema200) and openprofit >= 0 -> close; close[1] > L236 and not short -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * openprofit >= 0 for a short is close <= the entry price (the fill, next open after the
      signal): sizing-free, used so.
    * Short only. Entries only from flat (pyramiding 0); one signal per bar.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths and retracement fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, commission stored in original_sizing.txt.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427528_cc_trend_short"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fib_len": [100, 50, 200],
    "retrace": [0.236, 0.382],
}
DEFAULT_PARAMS = {"fib_len": 100, "retrace": 0.236}


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
    e9, e21, e55, e200 = (c.ewm(span=n, adjust=False).mean() for n in (9, 21, 55, 200))
    n = int(p["fib_len"])
    high_f = pd.concat([e55, e9], axis=1).max(axis=1).rolling(n).max()
    low_f = pd.concat([e55, e9], axis=1).min(axis=1).rolling(n).min()
    l236 = high_f - p["retrace"] * (high_f - low_f)
    short_c = ((c.shift(1) < high_f) & (e21 < e55)).to_numpy()
    x200 = ((c > e200) & (c.shift(1) <= e200.shift(1))).to_numpy()
    rm = ((c.shift(1) > l236).to_numpy()) & ~short_c
    ov, cv = bars_df["open"].to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pending, avg = 0, False, np.nan
    for i in range(m):
        if pending:
            pos, pending, avg = -1, False, ov[i]
        if pos == -1:
            if (x200[i] and cv[i] <= avg) or rm[i]:
                sx[i], pos = True, 0
        elif not pending and short_c[i]:
            se[i], pending = True, True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return false.copy(), false.copy(), pd.Series(se, index=idx), pd.Series(sx, index=idx)


def portfolio_kwargs(**params):
    return {}
