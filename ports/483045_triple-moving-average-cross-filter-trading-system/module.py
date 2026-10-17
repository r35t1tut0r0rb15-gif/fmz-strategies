"""SMA 21 / 50 crosses on the right side of SMA 100, long only, 1-hour bars: SMA 21 crossing above SMA 50 with both
above SMA 100 goes long; SMA 21 crossing below SMA 50 with both below SMA 100 closes it.
Port of FMZ strategy #483045 "多均线趋势交叉三重过滤交易策略-Triple-Moving-Average-Cross-Filter-Trading-System" (Vezpa's Gold Strategy).

FMZ source id: 483045

Source
    https://www.fmz.com/strategy/483045 (PineScript v5, FMZ last modified 2025-02-21 10:48:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 134-154), SMA 21 / 50 / 100
    crossover(fast, slow) and fast > trend and slow > trend -> entry long
    crossunder(fast, slow) and fast < trend and slow < trend -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only; the source has no shorts. No stops. "Gold" in the title is a label. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483045_sma21_50_cross_sma100_filter_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [21, 10],
    "trend": [100, 200],
}
DEFAULT_PARAMS = {"fast": 21, "slow": 50, "trend": 100}


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
    f, s, t = (c.rolling(int(p[k])).mean() for k in ("fast", "slow", "trend"))
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (f > t) & (s > t)).astype(bool)
    long_x = ((f < s) & (f.shift(1) >= s.shift(1)) & (f < t) & (s < t)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
