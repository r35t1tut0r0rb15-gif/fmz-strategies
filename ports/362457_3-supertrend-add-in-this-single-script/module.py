"""Three SuperTrends (1x21, 2x14, 3x7) in agreement: long when all point up, short when all point
down (no other exit).
Port of FMZ strategy #362457 "3-Supertrend-Add-In-This-Single-Script".

Source
    https://www.fmz.com/strategy/362457 (PineScript v5, FMZ last modified 2022-05-11 17:04:21).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 49-93)
    direction_1..3 = ta.supertrend(1.0, 21), (2.0, 14), (3.0, 7)
    all < 0 -> entry long;  else all > 0 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend as in Pine v5. strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362457_three_supertrend_agree"
FAMILY = "supertrend"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "f1": [1.0, 1.5],
    "f2": [2.0, 2.5],
    "f3": [3.0, 4.0],
}
DEFAULT_PARAMS = {"f1": 1.0, "p1": 21, "f2": 2.0, "p2": 14, "f3": 3.0, "p3": 7}


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


def _supertrend(bars, factor, atr_period):
    """ta.supertrend(factor, atrPeriod) as in Pine v5: returns (supertrend, direction);
    direction < 0 is an up-trend."""
    atr = _atr_pine(bars, atr_period).to_numpy()
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    hl2 = (h + lo) / 2
    m = len(c)
    st, dirn = np.full(m, np.nan), np.full(m, np.nan)
    lower_prev = upper_prev = 0.0      # nz(...[1])
    st_prev = np.nan
    for i in range(m):
        lower, upper = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        if i > 0:
            if not (lower > lower_prev or c[i - 1] < lower_prev):
                lower = lower_prev
            if not (upper < upper_prev or c[i - 1] > upper_prev):
                upper = upper_prev
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif st_prev == upper_prev:
            d = -1 if c[i] > upper else 1
        else:
            d = 1 if c[i] < lower else -1
        st[i] = lower if d == -1 else upper
        dirn[i] = d
        lower_prev = 0.0 if np.isnan(lower) else lower
        upper_prev = 0.0 if np.isnan(upper) else upper
        st_prev = st[i]
    return pd.Series(st, index=bars.index), pd.Series(dirn, index=bars.index)


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
    d = [_supertrend(bars_df, p[f"f{k}"], int(p[f"p{k}"]))[1].to_numpy() for k in (1, 2, 3)]
    warm = np.arange(len(bars_df)) >= int(max(p["p1"], p["p2"], p["p3"]))
    up = warm & (d[0] < 0) & (d[1] < 0) & (d[2] < 0)
    dn = warm & (d[0] > 0) & (d[1] > 0) & (d[2] > 0)
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
