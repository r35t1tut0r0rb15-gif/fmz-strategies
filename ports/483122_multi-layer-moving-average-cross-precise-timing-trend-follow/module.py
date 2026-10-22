"""Bar-range crossings of the SMA 50 in a stacked SMA 50 / 100 / 200 trend, hourly bars: a high reaching the SMA 50 after a low under it goes long in an uptrend, the mirror goes short in a downtrend; the low crossing under the SMA 20 closes a long, the high crossing over it closes a short; reversing.
Port of FMZ strategy #483122 "Multi Layer Moving Average Cross Precise Timing Trend Following Strategy" (Multi-SMA Strategy - Core Signals).

FMZ source id: 483122

Source
    https://www.fmz.com/strategy/483122 (PineScript v5, FMZ last modified 2025-02-21 14:32:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-145), SMA 20 / 50 / 100 / 200; tick-precise crosses on (default)
    golden = high >= sma50 and low[1] < sma50[1];  death = low <= sma50 and high[1] > sma50[1]
    golden and sma50 > sma100 > sma200 -> entry Long;  death and sma50 < sma100 < sma200 -> entry Short
    crossunder(low, sma20) -> close Long;  crossover(high, sma20) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "tick-precise" crosses are on by default (useTickCross true), so the SMA 20 / 50 crossing branch
      is not used for entries. A close on the bar of an entry is masked by the entry; an entry on the
      other side reverses (REVERSAL INTENDED). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bar-range SMA crossings in a stacked trend.
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

NAME = "fmz_483122_bar_range_sma50_cross_stacked_trend_sma20_exit_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_period1": [20, 10],
    "sma_period2": [50, 30],
}
DEFAULT_PARAMS = {"sma_period1": 20, "sma_period2": 50}


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
    s20, s50 = c.rolling(int(p["sma_period1"])).mean(), c.rolling(int(p["sma_period2"])).mean()
    s100, s200 = c.rolling(100).mean(), c.rolling(200).mean()
    golden = (h >= s50) & (lo.shift(1) < s50.shift(1))
    death = (lo <= s50) & (h.shift(1) > s50.shift(1))
    up = (s50 > s100) & (s100 > s200)
    dn = (s50 < s100) & (s100 < s200)
    le, se = golden & up, death & dn
    lx = (lo < s20) & (lo.shift(1) >= s20.shift(1))
    sx = (h > s20) & (h.shift(1) <= s20.shift(1))
    return le & ~se, lx & ~le & ~se, se, sx & ~se & ~le


def portfolio_kwargs(**params):
    return {}
