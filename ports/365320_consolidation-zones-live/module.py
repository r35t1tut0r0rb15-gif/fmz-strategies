"""Consolidation Zones (LonesomeTheBlue): after at least five bars of consolidation (zigzag swing
points staying inside the zone), a new swing point above the zone goes long, below it short.
Port of FMZ strategy #365320 "Consolidation Zones - Live".

Source
    https://www.fmz.com/strategy/365320 (PineScript v4, FMZ last modified 2022-05-24 11:43:02).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 53-131), loopback 10, min consolidation 5
    hb = high is the 10-bar high; lb = low is the 10-bar low; dir; zz = the swing value
    pp = extreme zz (max if dir 1, min if dir -1) since dir last changed
    on change(pp): if conscnt > 5: pp > condhigh -> breakout up, pp < condlow -> breakout down;
                   conscnt = conscnt + 1 if conscnt > 0 and condlow <= pp <= condhigh else 0
    otherwise conscnt += 1
    conscnt == 5: zone = highest(high, 5) / lowest(low, 5); conscnt > 5: zone widened by high / low
    breakout up -> entry long; else breakout down -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * highestbars(10) == 0 is read as high equal to the 10-bar high (ties go to the current bar).
    * The 1000-bar look-back loop is the current dir run; pp is na until a swing exists in it,
      and change(pp) is false when either value is na.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "45min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365320_consolidation_zone_breakout"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "prd": [5, 10, 20],
    "conslen": [3, 5, 8],
}
DEFAULT_PARAMS = {"prd": 10, "conslen": 5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    prd, cl = int(p["prd"]), int(p["conslen"])
    hs, ls = bars_df["high"], bars_df["low"]
    h, l = hs.to_numpy(dtype=float), ls.to_numpy(dtype=float)
    is_h = (hs >= hs.rolling(prd).max()).to_numpy()
    is_l = (ls <= ls.rolling(prd).min()).to_numpy()
    hh, ll = hs.rolling(cl).max().to_numpy(), ls.rolling(cl).min().to_numpy()
    m = len(h)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    d = 0
    d_prev = None
    pp = pp_prev = np.nan
    cnt = 0
    c_hi = c_lo = np.nan
    for i in range(m):
        hb = h[i] if is_h[i] else np.nan
        lb = l[i] if is_l[i] else np.nan
        if not np.isnan(hb) and np.isnan(lb):
            d = 1
        elif not np.isnan(lb) and np.isnan(hb):
            d = -1
        if not np.isnan(hb) and not np.isnan(lb):
            zz = hb if d == 1 else lb
        else:
            zz = hb if not np.isnan(hb) else lb
        if d_prev is not None and d != d_prev:
            pp = np.nan
        if not np.isnan(zz) and zz != 0:
            if np.isnan(pp) or (d == 1 and zz > pp) or (d == -1 and zz < pp):
                pp = zz
        d_prev = d
        changed = not np.isnan(pp) and not np.isnan(pp_prev) and pp != pp_prev
        if changed:
            if cnt > cl:
                le[i] = pp > c_hi
                se[i] = pp < c_lo
            cnt = cnt + 1 if (cnt > 0 and c_lo <= pp <= c_hi) else 0
        else:
            cnt += 1
        if cnt >= cl:
            if cnt == cl:
                c_hi, c_lo = hh[i], ll[i]
            else:
                c_hi, c_lo = max(c_hi, h[i]), min(c_lo, l[i])
        pp_prev = pp
    return _always_in(le, se & ~le, bars_df.index)


def portfolio_kwargs(**params):
    return {}
