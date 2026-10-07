"""Triple SuperTrend agreement: long when all three point up, short when all three point down;
the fastest one flipping against the position closes it.
Port of FMZ strategy #361880 "Triple-Supertrend-with-EMA-and-ADX" (kunjandetroja).

Source
    https://www.fmz.com/strategy/361880 (PineScript v5, FMZ last modified 2022-05-08 21:16:55).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 61-128), ST (1,10), (2,15), (3,20); filter off; reentry on
    sum_dir = dir1 + dir2 + dir3
    sum_dir == -3 -> entry BUY;  sum_dir == 3 -> entry SELL
    dir1 turns to 1 -> close BUY;  dir1 turns to -1 -> close SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend as in Pine v5. The ADX/EMA filter is off by default and not ported.
    * A reversing entry on the same bar as a close of the old side: the entry wins (the close
      finds no position). strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361880_triple_supertrend_agree"
FAMILY = "supertrend"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "m1": [1.0, 2.0],
    "m2": [2.0, 3.0],
    "m3": [3.0, 4.0],
}
DEFAULT_PARAMS = {"m1": 1.0, "m2": 2.0, "m3": 3.0, "p1": 10, "p2": 15, "p3": 20}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    d1 = _supertrend(bars_df, p["m1"], int(p["p1"]))[1]
    d2 = _supertrend(bars_df, p["m2"], int(p["p2"]))[1]
    d3 = _supertrend(bars_df, p["m3"], int(p["p3"]))[1]
    s = (d1 + d2 + d3).to_numpy()
    x_long = ((d1 == 1) & (d1 != d1.shift(1))).to_numpy()
    x_short = ((d1 == -1) & (d1 != d1.shift(1))).to_numpy()
    warm = np.arange(len(s)) >= int(max(p["p1"], p["p2"], p["p3"]))

    m = len(s)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        if not warm[i]:
            continue
        if s[i] == -3 and pos != 1:
            le[i], pos = True, 1
        elif s[i] == 3 and pos != -1:
            se[i], pos = True, -1
        elif pos == 1 and x_long[i]:
            lx[i], pos = True, 0
        elif pos == -1 and x_short[i]:
            sx[i], pos = True, 0

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
