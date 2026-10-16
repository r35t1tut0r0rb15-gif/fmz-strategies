"""ATR trailing-stop line (Vervoort), long only, hourly bars: the close crossing above the line goes long, the
close crossing below it closes the long.
Port of FMZ strategy #428813 "ATR Trailing Stops Strategy" (ATR Trailing Stops Strategy).

FMZ source id: 428813

Source
    https://www.fmz.com/strategy/428813 (PineScript v3, FMZ last modified 2023-10-09 16:59:57).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 149-181), ATR 5 x 3.5, shorts off
    ts := close and close[1] above ts[1] ? max(ts[1], close - nLoss) : both below ? min(ts[1], close + nLoss)
          : close > ts[1] ? close - nLoss : close + nLoss            (nLoss = 3.5 x atr(5), ts[1] nz 0)
    crossover(close, ts) -> entry long; crossunder(close, ts) -> close long (shorts: "Test w/Shorts?" false)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The line is a signal checked on closes, not a stop order (no mark).
    * isWithinTimeBounds (the last 360 days before "now") is the author's backtest window: dropped.
    * Long only (useShorts defaults to false). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428813_atr_trailing_line_long"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_period": [5, 10],
    "mult": [3.5, 2.5],
}
DEFAULT_PARAMS = {"atr_period": 5, "mult": 3.5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    nl = (p["mult"] * _rma(tr, int(p["atr_period"]))).to_numpy()
    s = c.to_numpy()
    m = len(s)
    ts = np.full(m, np.nan)
    for i in range(m):
        prev = ts[i - 1] if i >= 1 and not np.isnan(ts[i - 1]) else 0.0
        s1 = s[i - 1] if i >= 1 else np.nan
        if np.isnan(nl[i]):
            continue
        if s[i] > prev and s1 > prev:
            ts[i] = max(prev, s[i] - nl[i])
        elif s[i] < prev and s1 < prev:
            ts[i] = min(prev, s[i] + nl[i])
        else:
            ts[i] = s[i] - nl[i] if s[i] > prev else s[i] + nl[i]
    t = pd.Series(ts, index=bars_df.index)
    long_e = ((c > t) & (c.shift(1) <= t.shift(1))).astype(bool)
    long_x = ((c < t) & (c.shift(1) >= t.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
