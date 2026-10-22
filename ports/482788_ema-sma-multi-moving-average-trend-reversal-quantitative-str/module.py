"""SMA 50 / 200 crossings, 6-hour bars: the cross up goes long, the cross down goes short; reversing.
Port of FMZ strategy #482788 "多均线趋势反转量化策略基于EMA和SMA的组合信号系统-Multi-Moving-Average-Trend-Reversal-Quantitative-Strategy-Combined-EMA-and-SMA-Signal-System" (9/21/50/200 By DSW Trend Reversal for Options).

FMZ source id: 482788

Source
    https://www.fmz.com/strategy/482788 (PineScript v6, FMZ last modified 2025-02-27 17:49:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-176), SMA 50 / 200; EMA 9 / 21 and pivots 10 (plots / alerts only)
    crossover(sma50, sma200) -> entry "Buy Option" (long);  crossunder -> entry "Sell Option" (short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The EMA 9 / 21 crossings and the pivots feed plots and alerts only. Entries only; each reverses the
      other side. REVERSAL INTENDED. No sizing code. FREQ = "6h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA 50 / 200 crossings.
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

NAME = "fmz_482788_sma50_200_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "6h"  # backtest header period: 6h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [50, 20],
    "slow": [200, 100],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
