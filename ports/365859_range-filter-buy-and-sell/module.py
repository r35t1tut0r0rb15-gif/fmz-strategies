"""Range Filter buy and sell: close on the right side of a trending range filter (50 / 3x), after
the opposite state, goes long or short (always in).
Port of FMZ strategy #365859 "Range Filter Buy and Sell 5min [Strategy]".

Source
    https://www.fmz.com/strategy/365859 (PineScript v2/v3 syntax, FMZ last modified 2022-05-26 12:25:38).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 68-168), source close, period 50, multiplier 3,
HA candles off, stop / target off
    smrng = ema(ema(|close - close[1]|, 50), 99) * 3;  filt = range filter of close by smrng
    longCond = close > filt and close != close[1] and upward > 0;  shortCond mirrors
    CondIni latch; longCond and CondIni[1] == -1 -> entry long; shortCond and CondIni[1] == 1 -> short

Interpretation choices (Pine rules in SURVEY_README.md)
    * window() returns true (date inputs unused). The optional stop / take-profit defaults to off.
    * Same mechanics as #363562 with other defaults.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "10min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365859_range_filter_flip"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "per": [25, 50, 100],
    "mult": [2.0, 3.0, 4.0],
}
DEFAULT_PARAMS = {"per": 50, "mult": 3.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _smoothrng(x, t, m):
    avrng = (x - x.shift(1)).abs().ewm(span=t, adjust=False).mean()
    return avrng.ewm(span=t * 2 - 1, adjust=False).mean() * m


def _rngfilt(x, r):
    """Range filter: follows x only when it moves more than r away; nz(prev) = 0 at the start."""
    xv, rv = x.to_numpy(dtype=float), r.to_numpy(dtype=float)
    out = np.full(len(xv), np.nan)
    for i in range(len(xv)):
        prev = out[i - 1] if i and not np.isnan(out[i - 1]) else 0.0
        if xv[i] > prev:
            out[i] = prev if xv[i] - rv[i] < prev else xv[i] - rv[i]
        else:
            out[i] = prev if xv[i] + rv[i] > prev else xv[i] + rv[i]
    return pd.Series(out, index=x.index)


def _up_down_counts(f):
    fv = f.to_numpy(dtype=float)
    up, dn = np.zeros(len(fv)), np.zeros(len(fv))
    for i in range(1, len(fv)):
        if fv[i] > fv[i - 1]:
            up[i], dn[i] = up[i - 1] + 1, 0
        elif fv[i] < fv[i - 1]:
            up[i], dn[i] = 0, dn[i - 1] + 1
        else:
            up[i], dn[i] = up[i - 1], dn[i - 1]
    return up, dn


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
    c = bars_df["close"]
    filt = _rngfilt(c, _smoothrng(c, int(p["per"]), float(p["mult"])))
    up, dn = _up_down_counts(filt)
    moved = (c != c.shift(1)).to_numpy()
    long_c = (c > filt).to_numpy() & moved & (up > 0)
    short_c = (c < filt).to_numpy() & moved & (dn > 0)
    m = len(c)
    ini = np.zeros(m)
    for i in range(m):
        ini[i] = 1.0 if long_c[i] else (-1.0 if short_c[i] else (ini[i - 1] if i else 0.0))
    ini1 = np.concatenate([[0.0], ini[:-1]])
    return _always_in(long_c & (ini1 == -1), short_c & (ini1 == 1), bars_df.index)


def portfolio_kwargs(**params):
    return {}
