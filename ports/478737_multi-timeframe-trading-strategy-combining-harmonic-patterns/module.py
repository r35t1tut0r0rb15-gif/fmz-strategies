"""Confirmed 5-bar pivot lows (highs) with Williams %R 14 in its extreme, 1-minute bars: a pivot low with the close above its 5-bar low and %R under -80 goes long with a stop 0.5 % under the signal bar's low and a 61.8 % target; the mirror goes short; reversing.
Port of FMZ strategy #478737 "Multi Timeframe Trading Strategy Combining Harmonic Patterns and Williams R" (Harmonic Pattern with WPR Backtest).

FMZ source id: 478737

Source
    https://www.fmz.com/strategy/478737 (PineScript v5, FMZ last modified 2025-01-17 16:19:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-157), pattern length 5; WPR 14, -20 / -80; target multiplier 0.618 (of the price); stop buffer 0.5 %
    pivotlow(low, 5, 5) and close > lowest(close, 5) and wpr < -80 -> entry Long + exit(stop = low x 0.995, limit = close x 1.618);  pivothigh mirror and wpr > -20 -> entry Short + exit(stop = high x 1.005, limit = close x 0.382)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pivot is confirmed 5 bars after its centre (strict, as Pine's pivotlow / pivothigh). The
      target multiplier is applied to the price itself, as written (a 61.8 % move). The bracket is sent
      on each signal bar: the opening signal's levels are ported, sent as fractions of the fill open (a
      level at or through it is marketable and closed one bar late, as #458256); a repeat signal inside a
      trade re-sends it, which is not followed (as #434428, mark trailing_stop_pending). REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, confirmed pivots with Williams %R extremes.
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

NAME = "fmz_478737_pivot5_williams_r_extreme_bracket_reversal"
FAMILY = "support_resistance"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "pattern_length": [5, 10],
    "rr_mult": [0.618, 0.01],
}
DEFAULT_PARAMS = {"pattern_length": 5, "rr_mult": 0.618, "wpr_length": 14, "buffer": 0.005}


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


def _pivot(x, side, span=5):
    """Strict pivot of x at t - span, confirmed at t (Pine ta.pivothigh / pivotlow), on rolling
    windows (1-minute bars): the centre beats every bar of the span on each side."""
    s = x if side > 0 else -x
    centre = s.shift(span)
    left = s.shift(span + 1).rolling(span).max()
    right = s.rolling(span).max()
    return ((centre > left) & (centre > right)).to_numpy()


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k = int(p["pattern_length"])
    n = int(p["wpr_length"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    wpr = (hh - c) / (hh - ll).where(hh > ll) * -100
    pl = pd.Series(_pivot(lo, -1, k), index=c.index)
    ph = pd.Series(_pivot(h, 1, k), index=c.index)
    le = pl & (c > c.rolling(k).min()) & (wpr < -80)
    se = ph & (c < c.rolling(k).max()) & (wpr > -20)
    b, rr = float(p["buffer"]), float(p["rr_mult"])
    lvl = {"l_sl": lo * (1 - b), "l_tp": c * (1 + rr), "s_sl": h * (1 + b), "s_tp": c * (1 - rr)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le & ~se, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    le = le & ~se
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
