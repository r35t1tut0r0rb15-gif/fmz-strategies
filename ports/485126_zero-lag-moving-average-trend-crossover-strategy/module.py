"""Zero-lag EMA crosses over the EMA 15, long only, 1-hour bars: the zero-lag EMA (EMA 15 of close + (close - EMA 15))
crossing above the EMA 15 goes long; the cross back down closes the trade.
Port of FMZ strategy #485126 "零延迟移动平均趋势交叉策略Zero-Lag-Moving-Average-Trend-Crossover-Strategy" (Zero-Lag MA Trend Strategy).

FMZ source id: 485126

Source
    https://www.fmz.com/strategy/485126 (PineScript v5, FMZ last modified 2025-03-06 11:06:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 143-173), length 15
    zlma = ema(close + (close - ema(close, 15)), 15)
    crossover(zlma, ema) -> entry long;  crossunder(zlma, ema) -> close long
    hour == 15 and minute >= 45 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Session open (check 9 / C6): the 15:45 close-all (chart time zone) never matches a 1-hour bar, whose minute is
      always 0: it never fires as written; not emitted.
    * The two crosses cannot fall on one bar. Long only: opposite entries cannot occur.
    * FREQ = "1h" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: a 15:45 close-all in the chart's time zone, never on 1-hour bars as written; not emitted.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_485126_zero_lag_ema_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [15, 30],
}
DEFAULT_PARAMS = {"length": 15}


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
    n = int(p["length"])
    ema = c.ewm(span=n, adjust=False).mean()
    zl = (c + (c - ema)).ewm(span=n, adjust=False).mean()
    long_e = ((zl > ema) & (zl.shift(1) <= ema.shift(1))).astype(bool)
    long_x = ((zl < ema) & (zl.shift(1) >= ema.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
