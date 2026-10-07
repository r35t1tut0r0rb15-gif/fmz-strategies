"""Scalping Swing (JustUncleL): an up candle closing back above the PAC upper line (EMA 10 of
highs) while the PAC midline is above EMA 180 goes long; a down candle closing below the PAC
lower line while the midline is below EMA 180 goes short (always in).
Port of FMZ strategy #365642 "Scalping Swing Trading Tool R1-6 by JustUncleL".

Source
    https://www.fmz.com/strategy/365642 (PineScript v2/v3 syntax, FMZ last modified 2022-05-25 15:58:26).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 175-397), PAC length 10, EMA200 filter on
    pacC / pacL / pacU = ema(close / low / high, 10);  emaMedium = EMA 180 (intraday chart)
    isup   = close > open and close > pacU and close[1] < pacU[1] and pacC > emaMedium
    isdown = close < open and close < pacL and close[1] > pacL[1] and pacC < emaMedium
    isup -> entry long; else isdown -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * timeframe.isintraday is true on the 2-hour chart, so the medium EMA is 180 (200 on daily).
    * Fractals, pivots and EMA ribbons only draw.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365642_pac_break_ema_filter"
FAMILY = "ma_envelope_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pac_len": [10, 20, 34],
    "ema_medium": [180, 200],
}
DEFAULT_PARAMS = {"pac_len": 10, "ema_medium": 180}


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
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ema = lambda x, n: x.ewm(span=int(n), adjust=False).mean()
    n = p["pac_len"]
    pc, pl, pu = ema(c, n), ema(l, n), ema(h, n)
    med = ema(c, p["ema_medium"])
    up = ((c > o) & (c > pu) & (c.shift(1) < pu.shift(1)) & (pc > med)).to_numpy()
    dn = ((c < o) & (c < pl) & (c.shift(1) > pl.shift(1)) & (pc < med)).to_numpy()
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
