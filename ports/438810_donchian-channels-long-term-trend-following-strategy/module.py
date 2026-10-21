"""Donchian channel breakouts with a double-length middle band exit, 15-minute bars: a close above the previous 20-bar high goes long, a close below the previous 20-bar low goes short (reversing); a long
closes on a close under the 40-bar middle band, a short on a close above it.
Port of FMZ strategy #438810 "Donchian Channels Long Term Trend Following Strategy" (Donchian Channels LT Strategy).

FMZ source id: 438810

Source
    https://www.fmz.com/strategy/438810 (PineScript v4, FMZ last modified 2024-01-15 14:48:03).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 136-158), length 20; middle band double (40)
    upper = highest(high, 20)[1], lower = lowest(low, 20)[1], middle = avg(highest(high, 40)[1], lowest(low, 40)[1]);  close > upper -> entry long;  close < middle -> close long
    close < lower -> entry short;  close > middle -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bands exclude the current bar ([1]). The close of the opposite side on an entry bar acts on a
      trade the reversing entry already closed, so the reversal stands (as #438020). strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Donchian bands of past bars.
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

NAME = "fmz_438810_donchian_breakout_middle_exit"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 55],
    "double_mid": [True, False],
}
DEFAULT_PARAMS = {"length": 20, "double_mid": True}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    k = 2 * n if p["double_mid"] else n
    upper = h.rolling(n).max().shift(1).to_numpy()
    lower = lo.rolling(n).min().shift(1).to_numpy()
    mid = ((h.rolling(k).max().shift(1) + lo.rolling(k).min().shift(1)) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if cv[i] > upper[i] and i + 1 < m:
            if pos != 1:
                le[i], pos = True, 1
        elif cv[i] < lower[i] and i + 1 < m:
            if pos != -1:
                se[i], pos = True, -1
        elif pos == 1 and cv[i] < mid[i]:
            lx[i], pos = True, 0
        elif pos == -1 and cv[i] > mid[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
