"""Chandelier Exit flips: close above the ratcheted short stop (lowest close + 3 ATR) turns long,
below the ratcheted long stop (highest close - 3 ATR) turns short (always in).
Port of FMZ strategy #363848 "Chandelier Exit".

Source
    https://www.fmz.com/strategy/363848 (PineScript v4, FMZ last modified 2022-05-17 17:14:58).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 50-98), ATR period 22, multiplier 3, extremes on close
    longStop = highest(close, 22) - 3 * atr(22); prev = nz(longStop[1], longStop)
    longStop := close[1] > prev ? max(longStop, prev) : longStop;  shortStop mirrors
    dir := close > shortStopPrev ? 1 : close < longStopPrev ? -1 : dir   (var, starts 1)
    buySignal (dir -1 -> 1) -> entry long; else sellSignal -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Use Close Price for Extremums" defaults to true (highest/lowest of close).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363848_chandelier_exit_flip"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 22, 34],
    "mult": [2.0, 3.0, 4.0],
}
DEFAULT_PARAMS = {"length": 22, "mult": 3.0}


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


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


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
    n = int(p["length"])
    cs = bars_df["close"]
    atr = (p["mult"] * _atr_pine(bars_df, n)).to_numpy()
    hh, ll = cs.rolling(n).max().to_numpy(), cs.rolling(n).min().to_numpy()
    c = cs.to_numpy(dtype=float)
    m = len(c)
    d = np.ones(m)
    ls_prev_v = ss_prev_v = np.nan
    for i in range(m):
        ls, ss = hh[i] - atr[i], ll[i] + atr[i]
        lsp = ls if np.isnan(ls_prev_v) else ls_prev_v
        ssp = ss if np.isnan(ss_prev_v) else ss_prev_v
        if i and c[i - 1] > lsp:
            ls = max(ls, lsp)
        if i and c[i - 1] < ssp:
            ss = min(ss, ssp)
        prev = d[i - 1] if i else 1.0
        d[i] = 1.0 if c[i] > ssp else (-1.0 if c[i] < lsp else prev)
        ls_prev_v, ss_prev_v = ls, ss
    prev = np.concatenate([[np.nan], d[:-1]])
    return _always_in((d == 1) & (prev == -1), (d == -1) & (prev == 1), bars_df.index)


def portfolio_kwargs(**params):
    return {}
