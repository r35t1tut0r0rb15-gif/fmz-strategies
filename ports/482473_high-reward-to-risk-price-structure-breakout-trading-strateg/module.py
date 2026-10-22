"""Closes crossing over the previous 20-bar high or under the previous 20-bar low, 3-hour bars: each side enters with its stop at the 10-bar low / high and a target 5 times that risk from the signal close; reversing.
Port of FMZ strategy #482473 "High Reward to Risk Price Structure Breakout Trading Strategy" (Filtered Price Action Breakout).

FMZ source id: 482473

Source
    https://www.fmz.com/strategy/482473 (PineScript v6, FMZ last modified 2025-02-18 15:42:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 116-193), lookback 20; stop lookback 10; reward 5.0 x risk; max trades per day 5 (never binds)
    crossover(close, highest(high, 20)[1]) and tradeCount < 5 and close - lowest(low, 10) > 0 -> entry Long + exit(stop = lowest(low, 10), limit = close + 5 risk);  mirror -> entry Short + exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * tradeCount is declared afresh on every bar (0, then 1 when the day did not change), so it is always
      under 5 and the daily limit never binds, as written. The levels are fixed at the signal close and
      sent as fractions of the fill open (a level at or through it is marketable and closed one bar late,
      as #458256). A repeat breakout while the side is held re-sends the bracket from the new close;
      stops() keeps the first, so the repeat case is marked trailing_stop_pending (as #434428). REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark
      coarse_bar_stop. No sizing code. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; swing stop and R-multiple target as fractions of the fill.
    2 generic: PASS, Donchian-style breakouts with a swing stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG482473 (2 members, best partner #482797, Jaccard 0.859); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482473_hh20_ll20_close_break_swing10_stop_5r_reversal"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [20, 50],
    "rr_multiplier": [5.0, 2.0],
}
DEFAULT_PARAMS = {"lookback": 20, "rr_multiplier": 5.0, "stop_lookback": 10}


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
    n = int(p["lookback"])
    hh, ll = h.rolling(n).max().shift(1), lo.rolling(n).min().shift(1)
    ns = int(p["stop_lookback"])
    ls, ss = lo.rolling(ns).min(), h.rolling(ns).max()
    rr = float(p["rr_multiplier"])
    lr, sr = c - ls, ss - c
    le = (c > hh) & (c.shift(1) <= hh.shift(1)) & (lr > 0)
    se = (c < ll) & (c.shift(1) >= ll.shift(1)) & (sr > 0)
    lvl = {"l_sl": ls, "l_tp": c + rr * lr, "s_sl": ss, "s_tp": c - rr * sr}
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
