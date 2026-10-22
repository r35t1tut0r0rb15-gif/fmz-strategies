"""Stochastic 14 (SMA 5) level crossings, 4-hour bars: crossing over 15 or over 40 goes long, crossing under 93 or under 40 goes short, each with a 1 % stop and 1 % target (1:1) from the signal close; reversing.
Port of FMZ strategy #477592 "Multi Parameter Stochastic Intelligent Trend Trading Strategy" (CM Stochastic POP Method 3).

FMZ source id: 477592

Source
    https://www.fmz.com/strategy/477592 (PineScript v6, FMZ last modified 2025-01-06 16:09:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 83-234), stochastic 14, smooth K 5; levels 15 / 40 / 93; R:R 1:1, stop 1 %, both on; EMA 20 / 50 / 100 / 200 plotted only
    crossover(k, 15) -> entry Long_15 + exit(stop = close x 0.99, limit = close x 1.01);  crossover(k, 40) -> entry Long_40 + exit;  crossunder(k, 93) -> entry Short_93 + exit;  crossunder(k, 40) -> entry Short_40 + exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * With pyramiding 1 a second long id while long is ignored and its exit names an entry that never
      filled, so each position keeps its opening signal's bracket; the bracket is sent as fractions of
      the fill open (a level at or through it is marketable and closed one bar late, as #458256). No two
      of the four crossings can fall on one bar. The default 1:1 ratio is ported. REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. No
      sizing code. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, stochastic level crossings with a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the stop percentage and R:R stored.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_477592_stoch14_level_cross_pct_bracket_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [1.0, 4.0, 8.0],
    "stop_pct": [0.01, 0.02],
}
DEFAULT_PARAMS = {"rr": 1.0, "stop_pct": 0.01, "length": 14, "smooth_k": 5}


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
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).where(hh > ll)).rolling(int(p["smooth_k"])).mean()

    def up(lv):
        return (k > lv) & (k.shift(1) <= lv)

    def dn(lv):
        return (k < lv) & (k.shift(1) >= lv)

    le = up(15.0) | up(40.0)
    se = dn(93.0) | dn(40.0)
    sp = float(p["stop_pct"])
    tp = sp * float(p["rr"])
    lvl = {"l_sl": c * (1 - sp), "l_tp": c * (1 + tp), "s_sl": c * (1 + sp), "s_tp": c * (1 - tp)}
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
