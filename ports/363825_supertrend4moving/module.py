"""SuperTrend (close, ATR 20 x 3) flips: up-flip long, down-flip short (always in); the four SMAs
only draw.
Port of FMZ strategy #363825 "Supertrend+4moving".

Source
    https://www.fmz.com/strategy/363825 (PineScript v5, FMZ last modified 2022-05-17 15:35:18).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 55-117), source close, ATR period 20, multiplier 3,
ta.atr (changeATR true)
    up = close - 3 * atr; up1 = nz(up[1], up); up := close[1] > up1 ? max(up, up1) : up
    dn mirrors;  trend flips to 1 when close > dn1, to -1 when close < up1
    buySignal -> entry long; else sellSignal -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Classic SuperTrend recursion on close (not hl2); trend starts at 1. SMA 5/10/20/30 draw.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363825_close_supertrend_flip"
FAMILY = "supertrend"  # proposed 2026-10-07, user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [10, 20, 30],
    "mult": [2.0, 3.0, 4.0],
}
DEFAULT_PARAMS = {"period": 20, "mult": 3.0}


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


def _st_classic(bars, src, period, mult):
    """Classic (KivancOzbilgic) SuperTrend trend: up/dn ratchet on close[1]; trend starts at 1."""
    s = np.asarray(src, dtype=float)
    c = bars["close"].to_numpy(dtype=float)
    atr = _atr_pine(bars, period).to_numpy()
    m = len(c)
    trend = np.ones(m)
    up_prev = dn_prev = np.nan
    for i in range(m):
        up, dn = s[i] - mult * atr[i], s[i] + mult * atr[i]
        up_a = up if np.isnan(up_prev) else up_prev
        dn_a = dn if np.isnan(dn_prev) else dn_prev
        if i and c[i - 1] > up_a:
            up = max(up, up_a)
        if i and c[i - 1] < dn_a:
            dn = min(dn, dn_a)
        t = trend[i - 1] if i else 1.0
        trend[i] = 1.0 if (t == -1 and c[i] > dn_a) else (-1.0 if (t == 1 and c[i] < up_a) else t)
        up_prev, dn_prev = up, dn
    return trend


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
    tr = _st_classic(bars_df, bars_df["close"], int(p["period"]), float(p["mult"]))
    prev = np.concatenate([[np.nan], tr[:-1]])
    return _always_in((tr == 1) & (prev == -1), (tr == -1) & (prev == 1), bars_df.index)


def portfolio_kwargs(**params):
    return {}
