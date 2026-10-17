"""Dual-speed stochastics, 1-hour bars: the slow K (54, smoothed 36) crossing above 50 with the fast K (smoothed 12) above
50 and its D, and the slow K above the slow D, goes long; the mirror (slow D crossing under 50) goes short. The source's
exits are a 100-tick trailing stop without an offset, not emitted.
Port of FMZ strategy #431396 "Dual Stochastics Strategy" (stoch startegy).

FMZ source id: 431396

Source
    https://www.fmz.com/strategy/431396 (PineScript v3, FMZ last modified 2023-11-07 15:25:19).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 211-252), stoch 54, K 12, D 3, slow x3, lines 80 / 30, trail 100
    k = sma(stoch(54), 12); d = sma(k, 3); mtfK = sma(stoch(54), 36); mtfD = sma(k, 9)
    crossover(mtfK, 50) and k > 50 and k > d and mtfK > mtfD -> entry long
    crossunder(mtfD, 50) and k < 50 and k < d and mtfK < mtfD -> entry short
    crossunder(mtfD, 80) -> exit(trail_points = 100);  crossover(mtfK, 30) -> exit(trail_points = 100) for shorts

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are strategy.exit with trail_points only (no trail_offset; Pine needs both to arm a
      trail, so as written they may never arm): rule 2, mark trailing_stop_pending, not emitted
      (as #426794). The positions change only by the opposite entry.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND431396 (2 members, best partner #443110, Jaccard 0.718); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_431396_dual_speed_stochastics"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [54, 27],
    "smooth_k": [12, 6],
}
DEFAULT_PARAMS = {"length": 54, "smooth_k": 12, "smooth_d": 3}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, sk, sd = int(p["length"]), int(p["smooth_k"]), int(p["smooth_d"])
    st = 100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min()).replace(0.0, np.nan)
    k, mk = st.rolling(sk).mean(), st.rolling(sk * 3).mean()
    d = k.rolling(sd).mean()
    md = k.rolling(sd * 3).mean()
    lg = ((mk > 50) & (mk.shift(1) <= 50) & (k > 50) & (k > d) & (mk > md)).to_numpy()
    sh = ((md < 50) & (md.shift(1) >= 50) & (k < 50) & (k < d) & (mk < md)).to_numpy()
    m = len(lg)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if lg[i]:
            pos = 1
        if sh[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
