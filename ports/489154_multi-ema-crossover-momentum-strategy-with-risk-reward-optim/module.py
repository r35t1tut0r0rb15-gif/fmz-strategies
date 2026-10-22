"""EMA 50 / 200 crossings, 2-hour bars: the golden cross goes long and the death cross goes short, each with a 1 % stop and a 2 % target from the signal close; reversing.
Port of FMZ strategy #489154 "Multi EMA Crossover Momentum Strategy with Risk Reward Optimization" (Golden Cross & Death Cross Strategy with SL & TP).

FMZ source id: 489154

Source
    https://www.fmz.com/strategy/489154 (PineScript v5, FMZ last modified 2025-04-02 11:19:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 186-228), EMA 50 / 200; SL 1 %; RR 2
    crossover(ema50, ema200) -> entry Buy + exit(stop = close x 0.99, limit = close x 1.02);  crossunder -> entry Sell + mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set on the signal bar from its close and sent as fractions of the fill open (a level
      at or through it is marketable and closed one bar late, as #458256). The crossings alternate, so a
      same-side signal cannot come while held. An entry on the other side reverses (REVERSAL INTENDED). Stop
      module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. No
      sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with a percent bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_489154_ema50_200_cross_sl1_tp2pct_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stopLossPercent": [1.0, 2.0],
    "riskRewardRatio": [2.0, 3.0],
}
DEFAULT_PARAMS = {"stopLossPercent": 1.0, "riskRewardRatio": 2.0}


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
    f = c.ewm(span=50, adjust=False).mean()
    s = c.ewm(span=200, adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    sl = float(p["stopLossPercent"]) / 100
    tp = sl * float(p["riskRewardRatio"])
    lvl = {"l_sl": c * (1 - sl), "l_tp": c * (1 + tp), "s_sl": c * (1 + sl), "s_tp": c * (1 - tp)}
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
