"""Tenkan / kijun crosses (SMA 2 of the 9- and 26-bar high + low sums), always in, four-hour bars: a golden cross goes
long, a dead cross goes short.
Port of FMZ strategy #482445 "动态ichimoku均线突破趋势转换策略-Dynamic-Ichimoku-Moving-Average-Crossover-Trend-Switching-Strategy" (Ichimoku Crossover Strategy with Switching).

FMZ source id: 482445

Source
    https://www.fmz.com/strategy/482445 (PineScript v6, FMZ last modified 2025-02-18 14:51:56).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 106-133), tenkan 9, kijun 26
    tenkan = sma(highest(high, 9) + lowest(low, 9), 2); kijun the same over 26
    golden cross: short -> close and entry long; flat -> entry long (dead cross mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lines are SMA 2 smoothings of the high + low sums, not the classic mid-points (as written); the crosses are
      the same as for the halves.
    * The switching is a reversal (REVERSAL INTENDED); always in after the first cross. Signal module, no stops.
      FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rolling extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
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

NAME = "fmz_482445_tenkan_kijun_sma2_cross_always_in"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tenkan": [9, 20],
    "kijun": [26, 52],
}
DEFAULT_PARAMS = {"tenkan": 9, "kijun": 26}


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
    h, lo = bars_df["high"], bars_df["low"]

    def line(n):
        return (h.rolling(n).max() + lo.rolling(n).min()).rolling(2).mean()

    tk, kj = line(int(p["tenkan"])), line(int(p["kijun"]))
    long_e = ((tk > kj) & (tk.shift(1) <= kj.shift(1))).astype(bool)
    short_e = ((tk < kj) & (tk.shift(1) >= kj.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
