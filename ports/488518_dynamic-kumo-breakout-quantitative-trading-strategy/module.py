"""Undisplaced Ichimoku cloud breakouts long, SMA 14 / 28 death crosses short, always in, 1-hour bars: the close crossing
above the cloud top (the current, not shifted, Senkou spans) goes long; the SMA 14 crossing below the SMA 28 goes
short; each entry reverses the other.
Port of FMZ strategy #488518 "动态云层突破量化交易策略-Dynamic-Kumo-Breakout-Quantitative-Trading-Strategy" (KumoBreakLong).

FMZ source id: 488518

Source
    https://www.fmz.com/strategy/488518 (PineScript v6, FMZ last modified 2025-03-28 15:16:43).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 205-238), Tenkan 9, Kijun 26, Senkou B 52
    senkouA = (tenkan + kijun) / 2;  senkouB = midpoint of the 52-bar range;  cloudTop = max(A, B)
    crossover(close, cloudTop) -> entry long;  crossunder(sma(close, 14), sma(close, 28)) -> entry short
    (exitCondition = crossunder(close, cloudBottom) is computed but never used)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The spans are used as written, without Ichimoku's 26-bar displacement; the unused exit condition is not ported.
    * Entries reverse (REVERSAL INTENDED); both on one bar: the short, written last, wins (the long is not emitted).
    * FREQ = "1h" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, range midpoints and moving averages.
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

NAME = "fmz_488518_kumo_break_long_sma_cross_short"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len_kijun": [26, 39],
    "len_senkou": [52, 78],
}
DEFAULT_PARAMS = {"len_tenkan": 9, "len_kijun": 26, "len_senkou": 52, "sma_fast": 14, "sma_slow": 28}


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


def _mid(bars_df, n):
    return (bars_df["high"].rolling(n).max() + bars_df["low"].rolling(n).min()) / 2


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    tenkan, kijun = _mid(bars_df, int(p["len_tenkan"])), _mid(bars_df, int(p["len_kijun"]))
    span_a = (tenkan + kijun) / 2
    span_b = _mid(bars_df, int(p["len_senkou"]))
    top = np.maximum(span_a, span_b)
    long_e = (c > top) & (c.shift(1) <= top.shift(1))
    f, s = c.rolling(int(p["sma_fast"])).mean(), c.rolling(int(p["sma_slow"])).mean()
    short_e = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    long_e = (long_e & ~short_e).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
