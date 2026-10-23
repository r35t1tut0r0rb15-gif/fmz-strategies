"""Hourly bars: the exponential volume-weighted average (EMA 22 of volume x close over EMA 22 of volume) under the previous close goes long, above it goes short (the last state kept on a tie); reversing.
Port of FMZ strategy #439987 "Quantitative Strategy Based on Exponential Moving Average and Volume Weighting" (Combining Exponential And Volume Weighting (HPotter)).

FMZ source id: 439987

Source
    https://www.fmz.com/strategy/439987 (PineScript v2, FMZ last modified 2024-01-25 15:31:21).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 186-208), length 22; reverse off
    nRes = ema(volume * close, 22) / ema(volume, 22);  pos = nRes < close[1] ? 1 : nRes > close[1] ? -1 : pos[1]
    pos == 1 -> entry Long;  pos == -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries repeat every bar of a state and add nothing while in it, so the position follows the
      state. reverse is off. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close against its exponential volume-weighted average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the weights of the exponential volume-weighted average; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439987_exp_volume_weighted_average_vs_prev_close_1h_reversal"
FAMILY = "volume_weighted_ma"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [22, 50],
}
DEFAULT_PARAMS = {"length": 22}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    n = int(p["length"])
    ev = v.ewm(span=n, adjust=False).mean()
    res = (v * c).ewm(span=n, adjust=False).mean() / ev.where(ev != 0)
    pc = c.shift(1)
    raw = np.where(res < pc, 1, np.where(res > pc, -1, 0))
    m = len(raw)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if raw[i] == 1 and pos != 1:
            le[i], pos = True, 1
        elif raw[i] == -1 and pos != -1:
            se[i], pos = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
