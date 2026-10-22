"""Breakouts of a "Shark-32" double inside-bar pattern, 2-hour bars: after two narrowing bars inside a first bar, a close crossing over that bar's high goes long and a close crossing under its low goes short (one trade per pattern), with a target one pattern range beyond the break; reversing. The 1 % stop re-sent every bar from the latest close is not ported (pending).
Port of FMZ strategy #471691 "E9鲨鱼32形态量化价格突破策略-E9-Shark-32-Pattern-Quantitative-Price-Breakout-Strategy" (E9 Shark-32 Pattern Strategy with Target Lines).

FMZ source id: 471691

Source
    https://www.fmz.com/strategy/471691 (PineScript v5, FMZ last modified 2024-11-12 14:51:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-211), pattern = low[2] < low[1] < low and high[2] > high[1] > high; levels high[2] / low[2]; targets +- one range; stop 1 % of the current close
    shark32 -> patternHigh = high[2], patternLow = low[2], targets = high + range / low - range, tradeTaken = false
    crossover(close, patternHigh) and not tradeTaken -> entry Long;  crossunder(close, patternLow) and not tradeTaken -> entry Short;  tradeTaken = true
    long: exit(limit = upperTarget, stop = close x 0.99);  short: exit(limit = lowerTarget, stop = close x 1.01)  (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pattern levels are var values kept until the next pattern. The target is the pattern's level
      in force on the signal bar, sent as a fraction of the fill open (shifted into the fill bar; a
      target at or through the fill is closed one bar late). The stop is re-sent on every bar from that
      bar's close and the target moves when a new pattern forms during the trade: neither can be
      expressed by stops(), so they are described and kept pending (mark trailing_stop_pending).
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark
      coarse_bar_stop. No sizing code. FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the pattern target as a fraction of the fill.
    2 generic: PASS, inside-bar pattern breakouts with a range target; per-bar stop described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent stop inputs stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_471691_shark32_inside_pattern_breakout_range_target_reversal"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "target_mult": [1.0, 0.5],
}
DEFAULT_PARAMS = {"target_mult": 1.0}


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


def _parts(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    shark = ((lo.shift(2) < lo.shift(1)) & (lo.shift(1) < lo) & (h.shift(2) > h.shift(1)) & (h.shift(1) > h)).to_numpy()
    h2, l2 = h.shift(2).to_numpy(dtype=float), lo.shift(2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    k = float(p["target_mult"])
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tgt = np.full(m, np.nan)
    ph = pl = up_t = dn_t = np.nan
    ph1 = pl1 = np.nan                           # the levels on the bar before
    taken = False
    for i in range(m):
        if shark[i]:
            ph, pl = h2[i], l2[i]
            up_t, dn_t = ph + k * (ph - pl), pl - k * (ph - pl)
            taken = False
        c1 = cv[i - 1] if i > 0 else np.nan
        if not taken and cv[i] > ph and c1 <= ph1:
            le[i], taken, tgt[i] = True, True, up_t
        if not taken and cv[i] < pl and c1 >= pl1:
            se[i], taken, tgt[i] = True, True, dn_t
        ph1, pl1 = ph, pl
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(se, index=ix), pd.Series(tgt, index=ix)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, tgt = _parts(bars_df, p)
    o = bars_df["open"]
    t1 = tgt.shift(1)
    lx = le.shift(1, fill_value=False) & (t1 <= o) & ~se   # target through the fill: closed at the next open
    sx = se.shift(1, fill_value=False) & (t1 >= o) & ~le
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, tgt = _parts(bars_df, p)
    o = bars_df["open"]
    t1 = tgt.shift(1)                                         # the signal bar's target, read at the fill
    f = (t1 / o - 1).where(le.shift(1, fill_value=False), 1 - t1 / o)
    return {"tp_stop": f.where(f > 0)}


def portfolio_kwargs(**params):
    return {}
