"""Hourly bars: the stochastic 20 K crossing over its D 3 with the Chaikin money flow 10 above 0.1 goes long, crossing under with the flow under 0.08 goes short; a long closes on a cross down with the flow under -0.1, a short on a cross up with the flow above 0.06; reversing.
Port of FMZ strategy #437024 "Momentum and Money Flow Crossroad Cashing Strategy" (Stochastic and CMF Strategy (jawauntb)).

FMZ source id: 437024

Source
    https://www.fmz.com/strategy/437024 (PineScript v5, FMZ last modified 2023-12-29 16:12:35).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 171-204), stochastic 20 / 1 / 3; CMF 10; levels 0.1 / 0.08 / -0.1 / 0.06
    enterLong = crossover(k, d) and mf > 0.1;  enterShort = crossunder(k, d) and mf < 0.08;  exitLong = crossunder(k, d) and mf < -0.1;  exitShort = crossover(k, d) and mf > 0.06
    entry Long, close Long, entry Short, close Short (in that order)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The money flow is the loop sum of the close-location volume over 10 bars divided by the volume sum
      (a ratio, so the units cancel). A close acts only on a position the bar's entries leave unchanged
      (call order). REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic crossings with a money-flow filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the Chaikin money flow 10; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437024_stoch20_cross_cmf10_filter_reversal"
FAMILY = "stochastic_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period_k": [20, 14],
    "cmf_len": [10, 20],
}
DEFAULT_PARAMS = {"period_k": 20, "smooth_k": 1, "period_d": 3, "cmf_len": 10}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["period_k"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).where(hh != ll)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["period_d"])).mean()
    ad = pd.Series(np.where(((c == h) & (c == lo)) | (h == lo), 0.0,
                            (2 * c - lo - h) / (h - lo).where(h != lo)), index=c.index) * v
    nm = int(p["cmf_len"])
    sv = v.rolling(nm).sum()
    mf = ad.rolling(nm).sum() / sv.where(sv != 0)
    up = (k > d) & (k.shift(1) <= d.shift(1))
    dn = (k < d) & (k.shift(1) >= d.shift(1))
    el, es = (up & (mf > 0.1)).to_numpy(), (dn & (mf < 0.08)).to_numpy()
    xl, xs = (dn & (mf < -0.1)).to_numpy(), (up & (mf > 0.06)).to_numpy()
    m = len(el)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if el[i] and pos != 1:
            le[i], pos = True, 1
        elif es[i] and pos != -1:
            se[i], pos = True, -1
        elif pos == 1 and xl[i]:
            lx[i], pos = True, 0
        elif pos == -1 and xs[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
