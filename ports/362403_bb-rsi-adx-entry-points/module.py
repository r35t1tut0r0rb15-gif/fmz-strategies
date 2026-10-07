"""Bollinger touch entries filtered by RSI band and ADX strength: long on a low below the lower
band with RSI 30-50, short on a high above the upper band with RSI 50-70 (always in).
Port of FMZ strategy #362403 "BB-RSI-ADX-Entry-Points".

Source
    https://www.fmz.com/strategy/362403 (PineScript v5, FMZ last modified 2022-05-11 12:42:28).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 80-150), BB 9 x 2, RSI 14, ADX 14/14 > 25
    bbr = (close - lowerMinOne) / (upperMinOne - lowerMinOne)   (bands at 1 stdev)
    long  = low < lower and bbr > 0 and 30 < rsi < 50 and adx > 25
    short = high > upper and bbr < 1 and 50 < rsi < 70 and adx > 25
    long -> entry long;  else short -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * RSI from ta.rma of gains/losses (Wilder); ADX as Pine's dirmov/adx.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362403_bb_touch_rsi_adx"
FAMILY = "bollinger_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_len": [9, 20],
    "adx_min": [20, 25, 30],
}
DEFAULT_PARAMS = {"bb_len": 9, "bb_mult": 2.0, "rsi_len": 14, "adx_len": 14, "di_len": 14, "adx_min": 25}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(close, n):
    d = close.diff()
    return 100.0 - 100.0 / (1.0 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


def _adx_pine(bars, di_len, adx_len):
    """Pine's built-in-style dirmov/adx: RMA smoothing, fixnan on DI+/DI-."""
    h, lo, c = bars["high"], bars["low"], bars["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = np.where(up.isna(), np.nan, np.where((up > down) & (up > 0), up, 0.0))
    minus_dm = np.where(down.isna(), np.nan, np.where((down > up) & (down > 0), down, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    trs = _rma(tr, di_len)
    plus = _fixnan((100 * _rma(pd.Series(plus_dm, index=h.index), di_len) / trs).to_numpy())
    minus = _fixnan((100 * _rma(pd.Series(minus_dm, index=h.index), di_len) / trs).to_numpy())
    s = plus + minus
    dx = pd.Series(np.abs(plus - minus) / np.where(s == 0, 1, s), index=h.index)
    return pd.Series(plus, index=h.index), pd.Series(minus, index=h.index), 100 * _rma(dx, adx_len)


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
    n = int(p["bb_len"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    m1 = p["bb_mult"] - 1 if p["bb_mult"] > 1 else 1
    upper, lower = basis + p["bb_mult"] * sd, basis - p["bb_mult"] * sd
    bbr = (c - (basis - m1 * sd)) / (2 * m1 * sd)
    rsi = _rsi(c, int(p["rsi_len"]))
    adx = _adx_pine(bars_df, int(p["di_len"]), int(p["adx_len"]))[2]
    strong = adx > p["adx_min"]
    long_c = ((bars_df["low"] < lower) & (bbr > 0) & (rsi > 30) & (rsi < 50) & strong).to_numpy()
    short_c = ((bars_df["high"] > upper) & (bbr < 1) & (rsi > 50) & (rsi < 70) & strong).to_numpy()
    return _always_in(long_c, short_c, bars_df.index)


def portfolio_kwargs(**params):
    return {}
