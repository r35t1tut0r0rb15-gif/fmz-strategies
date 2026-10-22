"""Closes beyond the previous 15-minute bar's high or low, 15-minute bars: a close over the previous high goes long with a stop at the previous low and a 3 R target, a close under the previous low goes short with a stop at the previous high and a 3 R target; reversing.
Port of FMZ strategy #488850 "15分钟突破多周期协同策略基于风险收益比优化模型15-Minute-Breakout-Multi-Timeframe-Synergy-Strategy-with-Risk-Reward-Optimization-Model" (15-min Breakout via 2-min Candle (R:R=1:3)).

FMZ source id: 488850

Source
    https://www.fmz.com/strategy/488850 (PineScript v5, FMZ last modified 2025-03-31 17:32:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 175-230), security("15") high / low / time; RR 3; capital 100000, 10 % of equity
    time15 changes -> last15High := fifteenHigh[1], last15Low := fifteenLow[1]
    close > last15High -> entry Long + exit(stop = last15Low, limit = close + 3 (close - last15Low));  close < last15Low -> entry Short + mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the 15-minute header chart the "15" requests are the chart itself and its time changes on every
      bar, so the levels are the previous bar's high and low. The bracket is set on the signal bar and
      sent as fractions of the fill open (a level at or through it is marketable and closed one bar late,
      as #458256). A later same-side signal while held re-sends the bracket; the port keeps the opening
      levels, mark trailing_stop_pending (as #434428). An entry on the other side reverses (REVERSAL
      INTENDED). Stop module: portfolio_kwargs {} (driver D4). FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; previous-bar bracket as fractions of the fill.
    2 generic: PASS, previous-bar breakouts with a 3 R bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: capital 100000, 10 % of equity stored, not ported.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488850_prev_bar_breakout_prev_extreme_stop_3r_reversal"
FAMILY = "range_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [3.0, 1.5],
}
DEFAULT_PARAMS = {"rr": 3.0}


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
    ph, pl = h.shift(1), lo.shift(1)
    le = c > ph
    se = c < pl
    rr = float(p["rr"])
    lvl = {"l_sl": pl, "l_tp": c + rr * (c - pl), "s_sl": ph, "s_tp": c - rr * (ph - c)}
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
