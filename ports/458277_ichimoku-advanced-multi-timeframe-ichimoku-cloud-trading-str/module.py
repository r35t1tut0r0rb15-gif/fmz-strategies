"""Tenkan / Kijun crossings above the undisplaced cloud, 2-hour bars, long only: the Tenkan crossing over the Kijun with the close over both spans buys; the Tenkan crossing under the Kijun with the close under both spans sells.
Port of FMZ strategy #458277 "基于多维度动态云图的Ichimoku高级多周期交易策略-Advanced-Multi-Timeframe-Ichimoku-Cloud-Trading-Strategy-with-Dynamic-Multidimensional-Analysis" (Ichimoku (Flexible Ichimoku Cloud)).

FMZ source id: 458277

Source
    https://www.fmz.com/strategy/458277 (PineScript v5, FMZ last modified 2024-07-31 14:54:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 192-272), Tenkan 9, Kijun 26, Span B 52 (spans compared undisplaced; the displacement only offsets the plot); stop 5 % / target 10 % computed but never sent
    crossover(tenkan, kijun) and close > spanA and close > spanB -> entry Long;  crossunder(tenkan, kijun) and close < spanA and close < spanB -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The spans are compared on the current bar (the displacement only shifts the plotted cloud). The
      stop and target levels are stored but no exit order uses them. Long only. No sizing code. FREQ =
      "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Tenkan / Kijun crossings with a cloud filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458277_tenkan_kijun_cross_above_cloud_long"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tenkan": [9, 7],
    "kijun": [26, 22],
    "span_b": [52, 44],
}
DEFAULT_PARAMS = {"tenkan": 9, "kijun": 26, "span_b": 52}


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


def _mid(h, lo, n):
    return (h.rolling(int(n)).max() + lo.rolling(int(n)).min()) / 2


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    tk, kj = _mid(h, lo, p["tenkan"]), _mid(h, lo, p["kijun"])
    sa, sb = (tk + kj) / 2, _mid(h, lo, p["span_b"])
    le = (tk > kj) & (tk.shift(1) <= kj.shift(1)) & (c > sa) & (c > sb)
    lx = (tk < kj) & (tk.shift(1) >= kj.shift(1)) & (c < sa) & (c < sb)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
