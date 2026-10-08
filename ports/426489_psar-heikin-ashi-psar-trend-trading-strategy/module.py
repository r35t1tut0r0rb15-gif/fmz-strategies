"""Heikin-Ashi PSAR (QuantNomad, always in): a parabolic SAR run on Heikin-Ashi values; its flip
from short to long goes long, from long to short goes short.
Port of FMZ strategy #426489 "PSAR Heikin Ashi PSAR Trend Trading Strategy".

Source
    https://www.fmz.com/strategy/426489 (PineScript v4, FMZ last modified 2023-09-12 15:16:17).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 135-191), start 0.02, increment 0.02, max 0.2
    HA: haclose = ohlc4, haopen = (haopen[1] + haclose[1]) / 2 (seed (open + close) / 2),
        hahigh = max(high, haopen, haclose), halow = min(low, haopen, haclose)
    long_to_short = dir[1] == 1 and haclose <= psar[1];  short_to_long mirrors
    change = isfirst[1] or a flip
    dir = second bar: haclose[1] > haopen[1] ? 1 : -1; flips set it; else nz(dir[1])
    af  = change ? start : (dir == 1 and hahigh > ep[1]) or (dir == -1 and low < ep[1])
          ? min(max, af[1] + inc) : af[1]
    ep  = change ? (dir == 1 ? hahigh : halow) : dir == 1 ? max(ep[1], hahigh) : min(ep[1], halow)
    psar = second bar: halow[1] / hahigh[1]; change ? ep[1] : psar[1] +- af * (ep - psar[1])
    short_to_long -> entry long;  long_to_short -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written, the short side's acceleration test reads the raw low (not halow).
    * The first bar's values are na (no previous bar); the SAR starts on the second bar.
    * The date window (2018-2100) is a backtest window: dropped.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426489_heikin_ashi_psar"
FAMILY = "parabolic_sar"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "start": [0.01, 0.02],
    "increment": [0.01, 0.02],
    "maximum": [0.2],
}
DEFAULT_PARAMS = {"start": 0.02, "increment": 0.02, "maximum": 0.2}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _heikin_ashi(bars):
    """heikinashi(): HA close = ohlc4; HA open = (HA open[1] + HA close[1]) / 2, seeded (open + close) / 2."""
    o, h, l, c = (bars[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    hc = (o + h + l + c) / 4
    ho = np.full(len(c), np.nan)
    for i in range(len(c)):
        ho[i] = (o[i] + c[i]) / 2 if i == 0 or np.isnan(ho[i - 1]) else (ho[i - 1] + hc[i - 1]) / 2
    hh = np.maximum(h, np.maximum(ho, hc))
    hl = np.minimum(l, np.minimum(ho, hc))
    return pd.DataFrame({"open": ho, "high": hh, "low": hl, "close": hc}, index=bars.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ha = _heikin_ashi(bars_df)
    ho, hh, hl, hc = (ha[k].to_numpy() for k in ("open", "high", "low", "close"))
    low = bars_df["low"].to_numpy(dtype=float)
    m = len(hc)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    nan = np.nan
    psar_p, af_p, dir_p, ep_p = nan, nan, nan, nan  # previous bar's values (na on bar 0)
    for i in range(m):
        first_prev = i == 1
        l2s = dir_p == 1 and hc[i] <= psar_p
        s2l = dir_p == -1 and hc[i] >= psar_p
        change = first_prev or l2s or s2l
        if first_prev:
            d = 1 if hc[i - 1] > ho[i - 1] else -1
        elif l2s:
            d = -1
        elif s2l:
            d = 1
        else:
            d = 0 if np.isnan(dir_p) else dir_p
        if change:
            af = p["start"]
        elif (d == 1 and hh[i] > ep_p) or (d == -1 and low[i] < ep_p):
            af = min(p["maximum"], af_p + p["increment"])
        else:
            af = af_p
        if change and d == 1:
            ep = hh[i]
        elif change and d == -1:
            ep = hl[i]
        elif d == 1:
            ep = max(ep_p, hh[i]) if not np.isnan(ep_p) else nan
        else:
            ep = min(ep_p, hl[i]) if not np.isnan(ep_p) else nan
        if first_prev:
            ps = hl[i - 1] if hc[i - 1] > ho[i - 1] else hh[i - 1]
        elif change:
            ps = ep_p
        elif d == 1:
            ps = psar_p + af * (ep - psar_p)
        else:
            ps = psar_p - af * (psar_p - ep)
        le[i], se[i] = s2l, l2s
        psar_p, af_p, dir_p, ep_p = ps, af, d, ep
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
