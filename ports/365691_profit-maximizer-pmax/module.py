"""Profit Maximizer (PMax, KivancOzbilgic): an ATR stop that ratchets around EMA 10 of hl2 (not
around price); the EMA crossing above PMax goes long, below goes short (always in).
Port of FMZ strategy #365691 "Profit Maximizer".

Source
    https://www.fmz.com/strategy/365691 (PineScript v4, FMZ last modified 2022-05-25 17:13:45).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 101-210), source hl2, ATR 10 x 3 (ta.atr), EMA 10
    longStop = MA - 3 atr; prev = nz(longStop[1], longStop)
    longStop := MA > prev ? max(longStop, prev) : longStop;  shortStop mirrors
    dir flips to 1 when MA > shortStopPrev, to -1 when MA < longStopPrev (starts 1)
    PMax = dir == 1 ? longStop : shortStop
    crossover(MA, PMax) -> entry long; else crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * MA type default EMA; "Normalize ATR" defaults to false.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "15min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365691_pmax_ema_cross"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_len": [10, 14],
    "mult": [2.0, 3.0],
    "ma_len": [10, 20],
}
DEFAULT_PARAMS = {"atr_len": 10, "mult": 3.0, "ma_len": 10}


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
    src = (bars_df["high"] + bars_df["low"]) / 2
    ma = src.ewm(span=int(p["ma_len"]), adjust=False).mean().to_numpy()
    atr = _atr_pine(bars_df, int(p["atr_len"])).to_numpy()
    m = len(ma)
    pmax = np.full(m, np.nan)
    ls_prev = ss_prev = np.nan
    d = 1
    for i in range(m):
        ls, ss = ma[i] - p["mult"] * atr[i], ma[i] + p["mult"] * atr[i]
        lsp = ls if np.isnan(ls_prev) else ls_prev
        ssp = ss if np.isnan(ss_prev) else ss_prev
        if ma[i] > lsp:
            ls = max(ls, lsp)
        if ma[i] < ssp:
            ss = min(ss, ssp)
        d = 1 if (d == -1 and ma[i] > ssp) else (-1 if (d == 1 and ma[i] < lsp) else d)
        pmax[i] = ls if d == 1 else ss
        ls_prev, ss_prev = ls, ss
    ma1 = np.concatenate([[np.nan], ma[:-1]])
    pm1 = np.concatenate([[np.nan], pmax[:-1]])
    up = (ma > pmax) & (ma1 <= pm1)
    dn = (ma < pmax) & (ma1 >= pm1)
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
