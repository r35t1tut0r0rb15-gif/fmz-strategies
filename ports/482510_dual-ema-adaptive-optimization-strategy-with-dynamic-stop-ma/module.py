"""EMA 5 / 10 crossings, hourly bars: each crossing enters its side with a 1 % stop and a 1 % target from the signal close; reversing.
Port of FMZ strategy #482510 "Dual EMA Adaptive Optimization Strategy with Dynamic Stop Management System" (Evolutivna Strategija - AI Optimizacija).

FMZ source id: 482510

Source
    https://www.fmz.com/strategy/482510 (PineScript v5, FMZ last modified 2025-02-18 18:14:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 78-131), EMA 5 / 10; stop 1 %, target 1 %; 100 % of equity
    netprofit > bestProfit (or na) -> bestStopLoss := sl_input, bestTakeProfit := tp_input
    crossover(ema5, ema10) -> entry BUY + exit(stop = close x (1 - best SL), limit = close x (1 + best TP));  crossunder -> entry SELL + exit (mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "adaptive" levels are always the two inputs: the netprofit test only decides when the same
      values are copied again, so no order depends on profit. The levels are fixed at the signal close and
      sent as fractions of the fill open (a level at or through it is marketable and closed one bar late,
      as #458256); the crossings alternate, so no repeat re-sends them. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). The 100 % of equity size is sizing. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the signal close as fractions of the fill.
    2 generic: PASS, EMA crossings with a fixed percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
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

NAME = "fmz_482510_ema5_10_cross_pct1_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_input": [1.0, 2.0],
    "tp_input": [1.0, 3.0],
}
DEFAULT_PARAMS = {"sl_input": 1.0, "tp_input": 1.0, "ema_fast": 5, "ema_slow": 10}


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
    f = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    sl, tp = float(p["sl_input"]) / 100, float(p["tp_input"]) / 100
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
    return le, lf & l_thr & ~se, se, sf & s_thr & ~le


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
