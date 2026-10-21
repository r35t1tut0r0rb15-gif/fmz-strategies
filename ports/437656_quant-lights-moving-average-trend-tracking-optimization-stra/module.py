"""Stochastic Optimized Trend Tracker, 3-minute bars: a VIDYA-smoothed 250-bar stochastic (+1000) crossing over its OTT line from two bars back goes long, crossing under goes short; reversing.
Port of FMZ strategy #437656 "Quant Lights Moving Average Trend Tracking Optimization Strategy" (SOTT).

FMZ source id: 437656

Source
    https://www.fmz.com/strategy/437656 (PineScript v4, FMZ last modified 2024-01-04 15:44:23).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 179-250), %K 250, smoothing 50 (VIDYA), OTT period 3, percent 0.618; date window 2005-9999
    k = VAR(stoch(close, high, low, 250), 50);  src = k + 1000;  MAvg = VAR(src, 3) (VIDYA with a 9-bar CMO);  OTT = trailing long / short stops of MAvg at 0.618 %, scaled by (200 +- 0.618) / 200
    buySignalc = crossover(src, OTT[2]) -> entry Long;  sellSignallc = crossunder(src, OTT[2]) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * VAR is the script's VIDYA (alpha 2 / (length + 1) scaled by |CMO 9|, nz seeds at 0, so it starts
      from 0 and converges), as written. The stochastic is offset by +1000 so the percent stops work on a
      positive line. OTT[2] is the OTT two bars back. The date window covers everything: dropped.
      REVERSAL INTENDED. No sizing code. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic against its own trailing line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_437656_stochastic_ott_cross"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period_k": [250, 100],
    "smooth_k": [50, 20],
}
DEFAULT_PARAMS = {"period_k": 250, "smooth_k": 50, "ott_length": 3, "percent": 0.618}


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


def _var(src, n):
    """The script's VAR (VIDYA): alpha 2 / (n + 1) x |CMO over 9 bars|, nz seeds."""
    a = 2.0 / (n + 1)
    d = src.diff()
    ud = d.where(d > 0, 0.0).rolling(9).sum()
    dd = (-d).where(d < 0, 0.0).rolling(9).sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        cmo = ((ud - dd) / (ud + dd)).to_numpy()
    cmo = np.where(np.isnan(cmo), 0.0, cmo)
    v = src.to_numpy(dtype=float)
    out = np.zeros(len(v))
    prev = 0.0
    for i in range(len(v)):
        t = a * abs(cmo[i]) * v[i]
        out[i] = (0.0 if np.isnan(t) else t) + (1 - a * abs(cmo[i])) * prev
        prev = out[i]
    return pd.Series(out, index=src.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["period_k"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    k = _var(st, int(p["smooth_k"]))
    src = k + 1000
    mav = _var(src, int(p["ott_length"])).to_numpy()
    pct = float(p["percent"])
    m = len(mav)
    ott = np.full(m, np.nan)
    ls_p = ss_p = np.nan
    d = 1
    for i in range(m):
        fark = mav[i] * pct * 0.01
        ls, ss = mav[i] - fark, mav[i] + fark
        lsp = ls if np.isnan(ls_p) else ls_p
        ssp = ss if np.isnan(ss_p) else ss_p
        ls = max(ls, lsp) if mav[i] > lsp else ls
        ss = min(ss, ssp) if mav[i] < ssp else ss
        if d == -1 and mav[i] > ssp:
            d = 1
        elif d == 1 and mav[i] < lsp:
            d = -1
        mt = ls if d == 1 else ss
        ott[i] = mt * (200 + pct) / 200 if mav[i] > mt else mt * (200 - pct) / 200
        ls_p, ss_p = ls, ss
    o2 = pd.Series(ott, index=c.index).shift(2)
    up = (src > o2) & (src.shift(1) <= o2.shift(1))
    dn = (src < o2) & (src.shift(1) >= o2.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
