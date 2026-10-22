"""Engulfing-style rejections on the wrong side of the 50-bar range midpoint with the SMA 20 side, 1-minute bars: a green bar opening under a red bar's close, under the midpoint and over the SMA, goes long with the 50-bar low as stop and the 50-bar high as target; the mirror goes short; reversing.
Port of FMZ strategy #483514 "Dynamic Supply Demand Zone Midline Reversal Strategy" (Midline Rejection Entry with TP/SL at Supply/Demand).

FMZ source id: 483514

Source
    https://www.fmz.com/strategy/483514 (PineScript v6, FMZ last modified 2025-02-24 16:00:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 129-194), swing length 50; midline SMA 20; MPL 2.0 notice (bommytarton)
    long = close > sma20 and close < mid and close > open and open < close[1] and close[1] < open[1];  short mirror
    long or short -> close_all;  long -> zones stored, entry Long;  short -> entry Short
    long -> exit(limit = stored supply = highest(high, 50), stop = stored demand = lowest(low, 50));  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The zones include the signal bar and are stored at the signal; the exits are re-sent every bar from
      the stored values. The levels are sent as fractions of the fill open (a level at or through it is
      marketable and closed one bar late, as #458256). A repeat signal while held stores new zones and
      re-sends the bracket (and its close_all closes and re-opens the same side, which the port keeps as
      the open position); stops() keeps the first, so the repeat case is marked trailing_stop_pending (as
      #434428). An entry on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {}
      (driver D4). The labels are drawing only. No sizing code. The MPL 2.0 notice is kept with the
      verbatim copy (ported, stated). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; zone bracket as fractions of the fill.
    2 generic: PASS, midpoint rejections with range-edge brackets.
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

NAME = "fmz_483514_range50_midpoint_rejection_sma20_zone_bracket_reversal"
FAMILY = "mean_reversion_band"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [50, 100],
    "midline_length": [20, 50],
}
DEFAULT_PARAMS = {"length": 50, "midline_length": 20}


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
    n = int(p["length"])
    sup, dem = h.rolling(n).max(), lo.rolling(n).min()
    mid = (sup + dem) / 2
    sma = c.rolling(int(p["midline_length"])).mean()
    le = (c > sma) & (c < mid) & (c > o) & (o < c.shift(1)) & (c.shift(1) < o.shift(1))
    se = (c < sma) & (c > mid) & (c < o) & (o > c.shift(1)) & (c.shift(1) > o.shift(1))
    lvl = {"l_sl": dem, "l_tp": sup, "s_sl": sup, "s_tp": dem}
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
