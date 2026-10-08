"""Three SuperTrends (always in): any of three SuperTrends (7 x 1.5, 10 x 2, 20 x 3) turning up goes
long, turning down goes short; when several flip on one bar the last one in source order stands.
Port of FMZ strategy #426928 "Supertrend Three Supertrend Strategy".

Source
    https://www.fmz.com/strategy/426928 (PineScript v4, FMZ last modified 2023-09-15 15:59:15).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 157-193), ATR 7 / 10 / 20, factor 1.5 / 2 / 3
    for k in 1..3: change(direction_k) < 0 -> entry long; change(direction_k) > 0 -> entry short
    (close_all / cancel_all inputs off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's supertrend direction is -1 in an up-trend, so a fall in direction is a turn up.
      Same-bar entries fill in source order at the next open: the last one stands.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426928_three_supertrends"
FAMILY = "supertrend"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor_scale": [0.75, 1.0, 1.5],
}
DEFAULT_PARAMS = {"factor_scale": 1.0}  # multiplies the three factors 1.5 / 2 / 3
SETS = ((7, 1.5), (10, 2.0), (20, 3.0))


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


def _emit(target, index):
    """Signals from the position each bar's orders leave (1 / 0 / -1): a change to +-1 is an
    entry (reversing an opposite position), a change to 0 an exit of the side held."""
    m = len(target)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    prev = 0
    for i in range(m):
        n = target[i]
        if n != prev:
            if n == 1:
                le[i] = True
            elif n == -1:
                se[i] = True
            elif prev == 1:
                lx[i] = True
            else:
                sx[i] = True
        prev = n
    return tuple(pd.Series(x, index=index) for x in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    flips = []
    for atr_p, fac in SETS:
        d = _supertrend(bars_df, fac * p["factor_scale"], atr_p)[1]
        ch = d.diff().to_numpy()
        flips.append(ch)
    m = len(bars_df)
    target = np.zeros(m, dtype=int)
    pos = 0
    for i in range(m):
        for ch in flips:
            if ch[i] < 0:
                pos = 1
            elif ch[i] > 0:
                pos = -1
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
