"""Stochastic %K / %D crossings at the extremes, 5-minute bars: %K crossing over %D under 20 goes long, crossing under %D over 80 goes short; reversing. Each trade has a 1 % stop and 2 % target from its signal close.
Port of FMZ strategy #474833 "Dual Timeframe Stochastic Momentum Trading Strategy" (Enhanced Stochastic Strategy).

FMZ source id: 474833

Source
    https://www.fmz.com/strategy/474833 (PineScript v5, FMZ last modified 2024-12-12 14:19:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-154), stochastic 14, smooth K 3, D 3; 80 / 20; target 2 %, stop 1 % of the signal close
    crossover(k, d) and k < 20 -> tp := close x 1.02, sl := close x 0.99, entry Buy, exit(limit = tp, stop = sl);  crossunder(k, d) and k > 80 -> mirror for Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on each signal bar from its close: the opening signal's levels are ported,
      sent as fractions of the fill open (a level at or through it is marketable and closed one bar
      late, as #458256); a repeat signal inside a trade re-sends it from its own close and is not
      followed (as #434428, mark trailing_stop_pending). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). No sizing code. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, stochastic crossings at the extremes with a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_474833_stoch14_kd_cross_extremes_pct_bracket_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [14, 21],
    "tp_pct": [2.0, 4.0],
    "sl_pct": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 14, "tp_pct": 2.0, "sl_pct": 1.0, "smooth_k": 3, "smooth_d": 3}


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
    n = int(p["length"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    le = (k > d) & (k.shift(1) <= d.shift(1)) & (k < 20)
    se = (k < d) & (k.shift(1) >= d.shift(1)) & (k > 80)
    tp, sl = float(p["tp_pct"]) / 100, float(p["sl_pct"]) / 100
    lvl = {"l_sl": c * (1 - sl), "l_tp": c * (1 + tp), "s_sl": c * (1 + sl), "s_tp": c * (1 - tp)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
