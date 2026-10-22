"""EMA 21 / 55 crossings, hourly bars: the up-cross goes long with its stop at the 2-bar low and a 2R target from the signal close, the down-cross goes short with the 2-bar high and a 2R target; reversing.
Port of FMZ strategy #482849 "Adaptive EMA Crossover Dynamic Position Risk Management Strategy" (EMA Crossover Strategy).

FMZ source id: 482849

Source
    https://www.fmz.com/strategy/482849 (PineScript v5, FMZ last modified 2025-02-27 17:36:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-134), EMA 21 / 55; stop lowest low / highest high of 2 bars; RR 2; risk 1 % sizing; 10 % of equity; MPL 2.0 notice
    crossover(ema21, ema55) -> entry Long + exit(stop = lowest(low, 2), limit = close + 2 (close - stop))
    crossunder(ema21, ema55) -> entry Short + exit(stop = highest(high, 2), limit = close - 2 (stop - close))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed at the signal bar and sent as fractions of the fill open (a level at or through
      it is marketable and closed one bar late, as #458256). An entry on the other side reverses
      (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). The risk-percent quantity and the
      10 % of equity default are sizing. The MPL 2.0 notice is kept with the verbatim copy (ported,
      stated). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 2-bar stop and 2R target as fractions of the fill.
    2 generic: PASS, EMA crossings with a swing bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk-percent quantity and 10 % of equity stored, not ported.
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

NAME = "fmz_482849_ema21_55_cross_2bar_stop_2r_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "mt_ema": [21, 9],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"mt_ema": 21, "rr": 2.0, "lt_ema": 55, "stop_bars": 2}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.ewm(span=int(p["mt_ema"]), adjust=False).mean()
    s = c.ewm(span=int(p["lt_ema"]), adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    nb, rr = int(p["stop_bars"]), float(p["rr"])
    l_sl, s_sl = lo.rolling(nb).min(), h.rolling(nb).max()
    lvl = {"l_sl": l_sl, "l_tp": c + (c - l_sl) * rr, "s_sl": s_sl, "s_tp": c - (s_sl - c) * rr}
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
