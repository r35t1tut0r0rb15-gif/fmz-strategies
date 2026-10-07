"""Smoothed Heikin-Ashi market bias traded as written: LONG when the smoothed HA open is above
the smoothed HA close (a bearish bias), SHORT when below (always in).
Port of FMZ strategy #361996 "HA-Market-Bias".

Source
    https://www.fmz.com/strategy/361996 (PineScript v5, FMZ last modified 2022-05-09 14:16:37).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 62-117), Period 100, Smoothing 100
    o,c,h,l = ema(open/close/high/low, 100)
    haclose = (o+h+l+c)/4; xhaopen = (o+c)/2
    haopen = na(xhaopen[1]) ? (o+c)/2 : (xhaopen[1] + haclose[1])/2
    o2 = ema(haopen, 100); c2 = ema(haclose, 100)
    o2 > c2 -> entry long;  else o2 < c2 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The higher-timeframe input is empty (''), i.e. the chart timeframe: no request needed.
    * haopen uses xhaopen[1] (the plain (o+c)/2 of the previous bar), not haopen[1], as written.
    * The indicator colours o2 > c2 red (bearish); the added orders go long on it. Ported as
      written (flagged in PORT_NOTES).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "10min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361996_ha_bias_faded"
FAMILY = "heikin_ashi_trend"  # proposed 2026-10-07, user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ha_len": [50, 100],
    "ha_len2": [50, 100],
}
DEFAULT_PARAMS = {"ha_len": 100, "ha_len2": 100}


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
    n, n2 = int(p["ha_len"]), int(p["ha_len2"])
    o, c, h, lo = (bars_df[k].ewm(span=n, adjust=False).mean() for k in ("open", "close", "high", "low"))
    haclose = (o + h + lo + c) / 4
    xhaopen = (o + c) / 2
    haopen = ((xhaopen.shift(1) + haclose.shift(1)) / 2).fillna(xhaopen)
    o2 = haopen.ewm(span=n2, adjust=False).mean().to_numpy()
    c2 = haclose.ewm(span=n2, adjust=False).mean().to_numpy()
    warm = np.arange(len(o2)) >= n + n2
    return _always_in(warm & (o2 > c2), warm & (o2 < c2), bars_df.index)


def portfolio_kwargs(**params):
    return {}
