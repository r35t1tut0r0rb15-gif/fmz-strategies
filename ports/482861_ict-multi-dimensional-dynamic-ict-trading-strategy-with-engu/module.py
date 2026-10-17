"""Engulfing candles beyond the 20-bar demand / supply levels with a 1.5 % stop / 3 % target, 1-hour bars: a bullish
engulfing bar closing above the 20-bar lowest low goes long; a bearish engulfing bar closing below the 20-bar highest
high goes short.
Port of FMZ strategy #482861 "多维度动态ICT交易策略结合吞没形态与供需区域分析系统-Multi-Dimensional-Dynamic-ICT-Trading-Strategy-with-Engulfing-Patterns-and-Supply-Demand-Zone-Analysis-System" (ICT + Engulfing + Supply & Demand).

FMZ source id: 482861

Source
    https://www.fmz.com/strategy/482861 (PineScript v5, FMZ last modified 2025-02-20 15:44:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 114-146), zones on, SL 1.5 %, TP 3 %
    long = bullish engulfing and close > lowest(low, 20); short = bearish engulfing and close < highest(high, 20)
    entry + exit(stop = close x (1 -+ 1.5 %), limit = close x (1 +- 3 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The zone conditions hold on almost every engulfing bar (the close is inside the 20-bar range), as written; the
      "Backtest Timeframe" input is unused.
    * The bracket is placed with the entry from the signal close: 1.5 % / 3 % re-based on the fill (house rule). A
      later same-side signal while held re-places it: mark trailing_stop_pending.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, candle patterns, rolling extremes and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_482861_engulfing_zone_pct_bracket"
FAMILY = "candlestick"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [1.5, 1.0],
    "tp_pct": [3.0, 2.0],
}
DEFAULT_PARAMS = {"zone_len": 20, "sl_pct": 1.5, "tp_pct": 3.0}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    o1, c1 = o.shift(1), c.shift(1)
    n = int(p["zone_len"])
    bull = (c1 < o1) & (c > o) & (c > o1) & (o < c1) & (c > lo.rolling(n).min())
    bear = (c1 > o1) & (c < o) & (c < o1) & (o > c1) & (c < h.rolling(n).max())
    false = pd.Series(False, index=bars_df.index)
    return bull.astype(bool), false, bear.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
