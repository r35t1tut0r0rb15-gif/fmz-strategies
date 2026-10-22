"""EMA 10 / 20 crossings with the close beyond both EMAs, hourly bars, inside the source's date window (2017-01-01 to 2029-01-30): the cross up goes long, the cross down goes short; reversing.
Port of FMZ strategy #482687 "基于EMA双均线交叉的智能趋势跟踪交易策略系统-Intelligent-Trend-Following-Trading-Strategy-System-Based-on-EMA-Double-Moving-Average-Crossover" (BFX Buy and Sell).

FMZ source id: 482687

Source
    https://www.fmz.com/strategy/482687 (PineScript v5, FMZ last modified 2025-02-27 17:52:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 28-73), EMA 10 / 20; backtest window 2017-01-01 .. 2029-01-30 23:59
    in_backtest and crossover(ema10, ema20) and close above both -> entry Long;  in_backtest and crossunder and close below both -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The date window is kept as written (UTC bar times); it only removes bars before 2017. Entries only;
      each reverses the other side. A near twin of #482764 without the window (rule 7: both ported).
      REVERSAL INTENDED. No sizing code. The source carries the Mozilla Public License 2.0 notice.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with close confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: date window 2017-01-01 .. 2029-01-30 (UTC); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482687_ema10_20_cross_close_confirm_window_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_fast_length": [10, 5],
    "ema_slow_length": [20, 50],
}
DEFAULT_PARAMS = {"ema_fast_length": 10, "ema_slow_length": 20}
WINDOW = (pd.Timestamp("2017-01-01 00:00", tz="UTC"), pd.Timestamp("2029-01-30 23:59", tz="UTC"))


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
    f = c.ewm(span=int(p["ema_fast_length"]), adjust=False).mean()
    s = c.ewm(span=int(p["ema_slow_length"]), adjust=False).mean()
    t = bars_df.index
    inside = pd.Series((t >= WINDOW[0]) & (t <= WINDOW[1]), index=t)
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (c > f) & (c > s) & inside
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (c < f) & (c < s) & inside
    false = pd.Series(False, index=t)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
