"""Tenkan / Kijun crosses above or below the current cloud, 1-hour bars: the Tenkan 9 crossing above the Kijun 26 with the
close above both spans goes long, the cross down below both spans goes short (reversing). The 0.5 % / 1 % bracket is armed
only by a repeated signal inside a trade and is not ported.
Port of FMZ strategy #435169 "基于一目均衡表的5分钟快速突破策略Ichimoku-Scalping-Strategy-for-5-Minute-Timeframe" (Scalping Ichimoku Strategy).

FMZ source id: 435169

Source
    https://www.fmz.com/strategy/435169 (PineScript v5, FMZ last modified 2023-12-12 18:12:02).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 175-210), Tenkan 9, Kijun 26, Span B 52 (current values); SL 0.5 %, TP 1 % of the average price
    crossover(tenkan, kijun) and close > span1 and close > span2 -> entry long, exit(stop = avg (1 - 0.5 %), limit = avg (1 + 1 %))
    crossunder(tenkan, kijun) and close below both -> entry short, exit(stop = avg (1 + 0.5 %), limit = avg (1 - 1 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.exit is called only on a signal bar, with levels from the position's average price,
      which is na until a trade is open (or is the opposite trade's price on a reversal): the
      opening signal arms nothing useful, and a bracket appears only when a signal repeats inside a
      trade. A stop that starts after entry cannot be expressed by stops(): the bracket is not ported
      and the module gets the mark trailing_stop_pending (as #434466; the intended bracket is owed).
    * The spans are the current (undisplaced) values, as the code compares them. strategy.entry
      reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the late-armed bracket not ported (mark).
    2 generic: PASS, Ichimoku crosses and spans.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the percent bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_435169_tk_cross_cloud_side"
FAMILY = "ichimoku"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conv": [9, 20],
    "base": [26, 52],
}
DEFAULT_PARAMS = {"conv": 9, "base": 26, "span_b": 52}


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
    mid = lambda n: (h.rolling(n).max() + lo.rolling(n).min()) / 2  # noqa: E731
    t, k = mid(int(p["conv"])), mid(int(p["base"]))
    l1, l2 = (t + k) / 2, mid(int(p["span_b"]))
    le = ((t > k) & (t.shift(1) <= k.shift(1)) & (c > l1) & (c > l2)).astype(bool)
    se = ((t < k) & (t.shift(1) >= k.shift(1)) & (c < l1) & (c < l2)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
