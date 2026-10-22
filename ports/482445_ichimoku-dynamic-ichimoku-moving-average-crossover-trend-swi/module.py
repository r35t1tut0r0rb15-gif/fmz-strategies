"""Crossings of a doubled Tenkan (9) over a doubled Kijun (26), 4-hour bars: the golden cross goes long, the dead cross goes short; reversing.
Port of FMZ strategy #482445 "动态ichimoku均线突破趋势转换策略-Dynamic-Ichimoku-Moving-Average-Crossover-Trend-Switching-Strategy" (Ichimoku Crossover Strategy with Switching).

FMZ source id: 482445

Source
    https://www.fmz.com/strategy/482445 (PineScript v6, FMZ last modified 2025-02-18 14:51:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-139), tenkan 9, kijun 26 as sma(highest + lowest, 2)
    tenkan = sma(highest(high, 9) + lowest(low, 9), 2);  kijun = sma(highest(high, 26) + lowest(low, 26), 2);  golden cross -> close Short and entry Long (or entry from flat);  dead cross -> close Long and entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lines are 2-bar SMAs of high + low sums (not halved), as written; both are scaled alike, so the
      crossings are those of the smoothed midpoints. Each cross closes the other side and enters, which is
      a reversal. REVERSAL INTENDED. No sizing code. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed Tenkan / Kijun crossings.
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

NAME = "fmz_482445_smoothed_tenkan_kijun_cross_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tenkan": [9, 20],
    "kijun": [26, 60],
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
        return (h.rolling(int(n)).max() + lo.rolling(int(n)).min()).rolling(2).mean()

    tk, kj = line(p["tenkan"]), line(p["kijun"])
    le = (tk > kj) & (tk.shift(1) <= kj.shift(1))
    se = (tk < kj) & (tk.shift(1) >= kj.shift(1))
    false = pd.Series(False, index=h.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
