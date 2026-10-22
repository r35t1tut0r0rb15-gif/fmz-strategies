"""Engulfing candles against the 20-bar low / high, hourly bars: a bullish engulfing closing over the 20-bar low goes long, a bearish engulfing closing under the 20-bar high goes short, each with a 1.5 % stop and a 3 % target from the signal close; reversing.
Port of FMZ strategy #482861 "多维度动态ICT交易策略结合吞没形态与供需区域分析系统-Multi-Dimensional-Dynamic-ICT-Trading-Strategy-with-Engulfing-Patterns-and-Supply-Demand-Zone-Analysis-System" (ICT + Engulfing + Supply & Demand).

FMZ source id: 482861

Source
    https://www.fmz.com/strategy/482861 (PineScript v5, FMZ last modified 2025-02-20 15:44:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 110-150), engulfing; zones = highest high / lowest low of 20 bars; stop 1.5 %; target 3 %; 10 % of equity
    bullishEngulfing and close > lowest(low, 20) -> entry Long + exit(stop = close x 0.985, limit = close x 1.03)
    bearishEngulfing and close < highest(high, 20) -> entry Short + exit(stop = close x 1.015, limit = close x 0.97)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The zones are the 20-bar extremes including the bar, as written (use_snd on). The "Backtest
      Timeframe" input feeds nothing. The levels are fixed at the signal close and sent as fractions of
      the fill open (a level at or through it is marketable and closed one bar late, as #458256). A
      repeat signal while held re-sends the bracket from the new close; stops() keeps the first, so the
      repeat case is marked trailing_stop_pending (as #434428). An entry on the other side reverses
      (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). The 10 % of equity size is
      sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: PASS, engulfing candles with 20-bar extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_482861_engulfing_20bar_zone_1_5_3pct_bracket_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_loss_perc": [1.5, 1.0],
    "take_profit_perc": [3.0, 2.0],
}
DEFAULT_PARAMS = {"stop_loss_perc": 1.5, "take_profit_perc": 3.0, "zone_length": 20}


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


def _signals(bars_df, p):
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    o1, c1 = o.shift(1), c.shift(1)
    bull = (c1 < o1) & (c > o) & (c > o1) & (o < c1)
    bear = (c1 > o1) & (c < o) & (c < o1) & (o > c1)
    n = int(p["zone_length"])
    le = bull & (c > lo.rolling(n).min())
    se = bear & (c < h.rolling(n).max())
    a, b = float(p["stop_loss_perc"]) / 100, float(p["take_profit_perc"]) / 100
    lvl = {"l_sl": c * (1 - a), "l_tp": c * (1 + b), "s_sl": c * (1 + a), "s_tp": c * (1 - b)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
