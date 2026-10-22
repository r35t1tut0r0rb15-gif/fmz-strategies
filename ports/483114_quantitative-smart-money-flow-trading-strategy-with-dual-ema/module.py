"""Order-block bars (the 5-bar low two bars back on a green bar, or the 5-bar high on a red bar) with the EMA 50 / 200 trend, hourly bars: a bullish block in an uptrend goes long with the 5-bar low as stop and a 2R target, a bearish block in a downtrend goes short with the mirror; reversing.
Port of FMZ strategy #483114 "Quantitative Smart Money Flow Trading Strategy with Dual EMA and Dynamic Order Block Detection" (XAU/EUR Beginner-Friendly Strategy).

FMZ source id: 483114

Source
    https://www.fmz.com/strategy/483114 (PineScript v5, FMZ last modified 2025-02-21 14:10:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-154), EMA 50 / 200; swing 5 bars; RR 2; margin 100 / 100
    low[2] == lowest(low, 5)[2] and close[2] > open[2] and ema50 > ema200 -> entry Long + exit(stop = lowest(low, 5), limit = close + 2 (close - stop))
    high[2] == highest(high, 5)[2] and close[2] < open[2] and ema50 < ema200 -> entry Short + exit(stop = highest(high, 5), limit = close - 2 (stop - close))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed at the signal bar and sent as fractions of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256). A repeat signal while held re-sends
      the bracket; stops() keeps the first, so the repeat case is marked trailing_stop_pending (as
      #434428). An entry on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {}
      (driver D4). The labels are drawing only. No sizing code (margin 100 / 100). FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; swing bracket as fractions of the fill.
    2 generic: PASS, order-block bars with an EMA trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_483114_order_block5_ema50_200_trend_swing_2r_reversal"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_fast": [50, 20],
    "risk_reward": [2.0, 3.0],
}
DEFAULT_PARAMS = {"ema_fast": 50, "risk_reward": 2.0, "ema_slow": 200, "swing": 5}


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
    f = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    n = int(p["swing"])
    sh, sl = h.rolling(n).max(), lo.rolling(n).min()
    ob_bull = (lo.shift(2) == sl.shift(2)) & (c.shift(2) > o.shift(2))
    ob_bear = (h.shift(2) == sh.shift(2)) & (c.shift(2) < o.shift(2))
    le = (f > s) & ob_bull
    se = (f < s) & ob_bear
    rr = float(p["risk_reward"])
    lvl = {"l_sl": sl, "l_tp": c + (c - sl) * rr, "s_sl": sh, "s_tp": c - (sh - c) * rr}
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
