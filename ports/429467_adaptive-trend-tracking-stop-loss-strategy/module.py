"""Wilder volatility trailing line, 1-minute bars: the close crossing above the line goes long, crossing below
goes short (the line is a signal, not a stop order).
Port of FMZ strategy #429467 "Adaptive Trend Tracking Stop Loss Strategy" (Wilder's Volatility Trailing Stop Strategy with various MA's).

FMZ source id: 429467

Source
    https://www.fmz.com/strategy/429467 (PineScript v4, FMZ last modified 2023-10-17 14:04:28).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 169-205), ATR 7 (RMA) x 3, significant close = close
    upper = lowest(close, 7) + 3 atr; lower = highest(close, 7) - 3 atr
    TS := close < TS[1] ? upper[1] : close > TS[1] ? lower[1] : TS (0)
    crossover(close, TS) -> entry long; crossunder(close, TS) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * `float TS = 0` is re-declared each bar, so the "else" branch gives 0 (as written; only when the close
      equals the previous line or the previous line is na).
    * The ATR average type defaults to RMA (Wilder). The commented closes are not ported.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429467_wilder_volatility_line"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_mult": [3.0, 2.0],
    "atr_length": [7, 14],
}
DEFAULT_PARAMS = {"atr_mult": 3.0, "atr_length": 7}


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
    n = int(p["atr_length"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, n)
    upper = (c.rolling(n).min() + p["atr_mult"] * atr).to_numpy()
    lower = (c.rolling(n).max() - p["atr_mult"] * atr).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ts = np.zeros(m)
    for i in range(m):
        prev = ts[i - 1] if i >= 1 else np.nan
        if cv[i] < prev:
            ts[i] = upper[i - 1]
        elif cv[i] > prev:
            ts[i] = lower[i - 1]
        else:
            ts[i] = 0.0
    t = pd.Series(ts, index=bars_df.index)
    long_e = ((c > t) & (c.shift(1) <= t.shift(1))).astype(bool)
    short_e = ((c < t) & (c.shift(1) >= t.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
