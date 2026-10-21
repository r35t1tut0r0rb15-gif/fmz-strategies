"""Noro's ZigTrend, 30-minute bars: when a triple-smoothed EMA of the close turns up, a close above the 4-bar low goes long; when it turns down, a close below the 4-bar high goes short; reversing.
Port of FMZ strategy #438006 "基于ZigZag指标的趋势追踪交易策略ZigZag-Trend-Following-Strategy" (ZigTrend 1.0).

FMZ source id: 438006

Source
    https://www.fmz.com/strategy/438006 (PineScript v3, FMZ last modified 2024-01-08 10:13:24).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 174-206), length 4, ExtremeDetection 4, source close; long and short on; capital 100 %; date window 1900-2100
    hls = ema(ema(ema(close, 4), round(4 x 0.66)), round(4 x 0.33));  rising = hls >= hls[1];  zigzag = lowest(4) on a turn up, highest(4) on a turn down, else na
    up = close > zigzag -> entry Long;  dn = close < zigzag -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The zigzag value exists only on a turn bar, so the signals fire only there; lowest(4) / highest(4)
      are of the lows / highs and include the current bar. Pine's round is half away from zero. The
      date window is always true. strategy.entry reverses: REVERSAL INTENDED. The equity lot and capital
      input are sizing. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed-EMA turns and 4-bar extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity lot, capital input and percent-of-equity size stored.
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

NAME = "fmz_438006_zigtrend_turns"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [4, 8],
    "detection": [4, 8],
}
DEFAULT_PARAMS = {"length": 4, "detection": 4}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _pine_round(x):
    return int(np.floor(x + 0.5))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, k = int(p["length"]), int(p["detection"])
    e1 = c.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=max(1, _pine_round(n * 0.66)), adjust=False).mean()
    hls = e2.ewm(span=max(1, _pine_round(n * 0.33)), adjust=False).mean()
    rising = hls >= hls.shift(1)
    prev = rising.shift(1, fill_value=False)
    turn_up = rising & ~prev
    turn_dn = ~rising & prev
    up = turn_up & (c > lo.rolling(k).min())
    dn = turn_dn & (c < h.rolling(k).max())
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
