"""A2MK-style EMA support / resistance line, 1-hour bars: the line (the EMA 13 of the 3-bar lowest or highest EMA 34 of the true-range midpoint) crossing over the midpoint EMA goes short, crossing under goes
long; reversing.
Port of FMZ strategy #439863 "基于双EMA的趋势追踪策略Trend-Following-Strategy-Based-on-Dual-EMA" (EMA STRATEGY).

FMZ source id: 439863

Source
    https://www.fmz.com/strategy/439863 (PineScript v3, FMZ last modified 2024-01-24 14:52:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 146-171), EMA2 13, EMA1 34
    ema_sr = ema((max(close[1], high) + min(close[1], low)) / 2, 34);  highest_ema = ema(highest(ema_sr, 3), 13);  lowest_ema = ema(lowest(ema_sr, 3), 13);  ema_ysl = ema_sr > highest_ema ? lowest_ema : highest_ema
    crossover(ema_ysl, ema_sr) -> entry "Short" (short);  crossunder(ema_ysl, ema_sr) -> entry "Long" (long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The condition names are swapped relative to the orders (longCondition opens the short), but the
      orders match the line logic: the line rising through the price line is bearish. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA line crossings.
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

NAME = "fmz_439863_a2mk_ema_support_line_cross"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema1": [34, 21],
    "ema2": [13, 8],
}
DEFAULT_PARAMS = {"ema1": 34, "ema2": 13}


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
    c1 = c.shift(1)
    mid = (pd.concat([c1, h], axis=1).max(axis=1, skipna=False) + pd.concat([c1, lo], axis=1).min(axis=1, skipna=False)) / 2
    sr = mid.ewm(span=int(p["ema1"]), adjust=False).mean()
    n2 = int(p["ema2"])
    hi_e = sr.rolling(3).max().ewm(span=n2, adjust=False).mean()
    lo_e = sr.rolling(3).min().ewm(span=n2, adjust=False).mean()
    ysl = lo_e.where(sr > hi_e, hi_e)
    xo = (ysl > sr) & (ysl.shift(1) <= sr.shift(1))
    xu = (ysl < sr) & (ysl.shift(1) >= sr.shift(1))
    false = pd.Series(False, index=c.index)
    return xu, false, xo, false.copy()


def portfolio_kwargs(**params):
    return {}
