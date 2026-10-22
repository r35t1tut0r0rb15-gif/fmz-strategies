"""EMA 9 / 21 crossings, hourly bars: the up-cross goes long and the down-cross goes short, each with a 2 % stop and a 4 % target from the signal close; reversing.
Port of FMZ strategy #482889 "Multi Indicator Crossover Trend Following Strategy with Fibonacci Retracement and Stop Loss Take Profit Optimization System" (EMA Cross Strategy with TP, SL, Fibonacci Levels, and Trend).

FMZ source id: 482889

Source
    https://www.fmz.com/strategy/482889 (PineScript v5, FMZ last modified 2025-02-20 16:43:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-175), EMA 9 / 21; stop 2 %; target 4 %; Fibonacci 100-bar levels (labels only)
    crossover(ema9, ema21) -> entry BUY + exit(stop = close x 0.98, limit = close x 1.04);  crossunder -> entry SELL + exit(stop = close x 1.02, limit = close x 0.96)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Fibonacci levels, trend label and the other labels are drawing only. The levels are fixed at
      the signal close and sent as fractions of the fill open (a level at or through it is marketable and
      closed one bar late, as #458256). The crossings alternate, so a side never re-sends its bracket
      while held. An entry on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs
      {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with a percent bracket.
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

NAME = "fmz_482889_ema9_21_cross_2_4pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast_length": [9, 5],
    "slow_length": [21, 50],
}
DEFAULT_PARAMS = {"fast_length": 9, "slow_length": 21, "stop_pct": 2, "take_pct": 4}


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
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast_length"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow_length"]), adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    a, b = float(p["stop_pct"]) / 100, float(p["take_pct"]) / 100
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
