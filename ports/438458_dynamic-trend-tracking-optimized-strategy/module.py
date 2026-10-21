"""Optimized Trend Tracker (support line crossings), 45-minute bars: the CMO-adaptive support line crossing over the OTT line of two bars back goes long, crossing under goes short; reversing.
Port of FMZ strategy #438458 "Dynamic Trend Tracking Optimized Strategy" (OTT-Strategy).

FMZ source id: 438458

Source
    https://www.fmz.com/strategy/438458 (PineScript v4, FMZ last modified 2024-01-12 11:20:04).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 139-204), source close; OTT period 1, percent 0.1; condition Support Line Crossing Signals; dates from 2020; commission 0.1 %
    ud1 = src > src[1] ? src - src[1] : src;  dd1 = src < src[1] ? src[1] - src : src;  CMO = (sum(ud1, 9) - sum(dd1, 9)) / (sum(ud1, 9) + sum(dd1, 9));  Var := alpha |CMO| src + (1 - alpha |CMO|) Var[1]
    longStop / shortStop = Var -/+ Var x 0.1 %, ratcheted;  dir flips on Var crossing the previous stops;  MT = dir 1 ? longStop : shortStop;  OTT = MT x (200 +/- 0.1) / 200
    crossover(Var, OTT[2]) -> entry BUY;  crossunder(Var, OTT[2]) -> entry SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * The up / down terms take the price itself (not 0) on the other bars, as written (the published OTT
      uses 0; owed). With period 1, alpha is 1. The date window starts 2020-01-01 and never ends; it is
      treated as always true (as #436533). strategy.entry reverses: REVERSAL INTENDED. The size, capital
      and commission are sizing / costs. FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, adaptive support line and OTT crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital, commission and quantity 1 stored.
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

NAME = "fmz_438458_ott_support_line_cross"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "percent": [0.1, 0.5],
    "pds": [1, 2],
}
DEFAULT_PARAMS = {"percent": 0.1, "pds": 1, "cmo_len": 9}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    src = bars_df["close"]
    s1 = src.shift(1)
    ud1 = np.where(src > s1, src - s1, src)
    dd1 = np.where(src < s1, s1 - src, src)
    n = int(p["cmo_len"])
    ud = pd.Series(ud1, index=src.index).rolling(n).sum()
    dd = pd.Series(dd1, index=src.index).rolling(n).sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        k = ((ud - dd) / (ud + dd)).abs().to_numpy()
    alpha = 2.0 / (int(p["pds"]) + 1)
    pct = float(p["percent"])
    sv = src.to_numpy(dtype=float)
    m = len(sv)
    var = np.full(m, np.nan)
    ott = np.full(m, np.nan)
    ls_prev = ss_prev = np.nan
    d = 1
    for i in range(m):
        pv = var[i - 1] if i > 0 and not np.isnan(var[i - 1]) else 0.0   # nz(Var[1])
        a = alpha * k[i]
        var[i] = a * sv[i] + (1 - a) * pv
        v = var[i]
        fark = v * pct * 0.01
        ls, ss = v - fark, v + fark
        lp = ls_prev if not np.isnan(ls_prev) else ls          # nz(longStop[1], longStop)
        sp = ss_prev if not np.isnan(ss_prev) else ss
        if v > lp:
            ls = max(ls, lp)
        if v < sp:
            ss = min(ss, sp)
        if d == -1 and v > sp:
            d = 1
        elif d == 1 and v < lp:
            d = -1
        mt = ls if d == 1 else ss
        ott[i] = mt * (200 + pct) / 200 if v > mt else mt * (200 - pct) / 200
        ls_prev, ss_prev = ls, ss
    vs =pd.Series(var, index=src.index)
    o2 = pd.Series(ott, index=src.index).shift(2)
    up = (vs > o2) & (vs.shift(1) <= o2.shift(1))
    dn = (vs < o2) & (vs.shift(1) >= o2.shift(1))
    false = pd.Series(False, index=src.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
