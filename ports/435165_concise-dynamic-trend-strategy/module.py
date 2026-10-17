"""Traders Dynamic Index alerts, 2-hour bars: with the RSI 13 price line (SMA 2) above its trade line (SMA 7) inside 22-78, a
green bar whose high clears the 5-bar smoothed-high channel gives a strong or medium buy (by the lines' place against the
volatility-band mid); the first such alert of a sequence goes long; the bearish mirror goes short (reversing).
Port of FMZ strategy #435165 "Concise Dynamic Trend Strategy" ([BACKTEST]Traders Dynamic Index Indicator Alert by JustUncleL).

FMZ source id: 435165

Source
    https://www.fmz.com/strategy/435165 (PineScript v4, FMZ last modified 2023-12-12 18:03:39).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 168-463), RSI 13, band 34 x 1.6185, price line 2, trade line 7; PAC 5; levels 22 / 78; strength 2; MACD filter off; HA off; TP / SL 0 (off)
    long = mab > mbb and 22 < mab < 78 and high > smma(high, 5) and close > open ? (mbb > mid ? 1 : mab > mid and mbb < mid ? 2 : mab < mid and mbb < mid ? 3 : 0) : 0
    longCond = long > 0 and long != long[1] and long <= 2 -> entry long;  shortCond (mirror) -> entry short;  exits with TP / SL 0 (none)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The security calls with Heikin-Ashi off read the chart's own prices. The MACD filter is off.
      The take profit / stop are 0 (disabled). strategy.entry reverses: REVERSAL INTENDED. The date
      window is the author's: dropped. Population stdev, Wilder RSI, SMMA seeded by its SMA. FREQ =
      "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI bands and a smoothed price channel.
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

NAME = "fmz_435165_traders_dynamic_index_alerts"
FAMILY = "rsi_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "strength": [2, 1],
    "lenh": [5, 10],
}
DEFAULT_PARAMS = {"lrsi": 13, "lband": 34, "lpl": 2, "ltsl": 7, "lenh": 5, "osl": 22, "obl": 78, "strength": 2}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _smma(v, n):
    sma = pd.Series(v).rolling(n).mean().to_numpy()
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        out[i] = (out[i - 1] * (n - 1) + v[i]) / n if i > 0 and not np.isnan(out[i - 1]) else sma[i]
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ch = c.diff()
    n = int(p["lrsi"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(up.notna())
    mid = r.rolling(int(p["lband"])).mean().to_numpy()
    mab = r.rolling(int(p["lpl"])).mean().to_numpy()
    mbb = r.rolling(int(p["ltsl"])).mean().to_numpy()
    lh = int(p["lenh"])
    sh, sl = _smma(h.to_numpy(dtype=float), lh), _smma(lo.to_numpy(dtype=float), lh)
    hv, lv, cv, ov = (x.to_numpy(dtype=float) for x in (h, lo, c, o))
    osl, obl, stg = float(p["osl"]), float(p["obl"]), int(p["strength"])
    m = len(cv)
    lng, sht = np.zeros(m, dtype=int), np.zeros(m, dtype=int)
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if mab[i] > mbb[i] and osl < mab[i] < obl and hv[i] > sh[i] and cv[i] > ov[i]:
                lng[i] = 1 if mbb[i] > mid[i] else (2 if (mab[i] > mid[i] and mbb[i] < mid[i]) else
                                                   (3 if (mab[i] < mid[i] and mbb[i] < mid[i]) else 0))
            if mab[i] < mbb[i] and osl < mab[i] < obl and lv[i] < sl[i] and cv[i] < ov[i]:
                sht[i] = 1 if mbb[i] < mid[i] else (2 if (mab[i] < mid[i] and mbb[i] > mid[i]) else
                                                   (3 if (mab[i] > mid[i] and mbb[i] > mid[i]) else 0))
    l1, s1 = np.concatenate(([0], lng[:-1])), np.concatenate(([0], sht[:-1]))
    le = (lng > 0) & (lng != l1) & (lng <= stg)
    se = (sht > 0) & (sht != s1) & (sht <= stg)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le & ~se, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
