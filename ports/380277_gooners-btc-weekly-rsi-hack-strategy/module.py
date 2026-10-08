"""Gooners BTC weekly RSI hack (Zer3192): RSI 14 crossing above 52 goes long; crossing below 52 closes
it. Long only.
Port of FMZ strategy #380277 "Gooners BTC Weekly RSI Hack Strategy".

Source
    https://www.fmz.com/strategy/380277 (PineScript v5, author Zer3192, FMZ last modified
    2022-08-27 21:19:13). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 35-46), RSI 14, buy level 52, sell level 52
    crossover(rsi, 52) -> entry long;  crossunder(rsi, 52) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only, as written (rule 6). Opposite entries cannot occur; portfolio_kwargs returns
      upon_opposite_entry="ignore".
    * The title says "weekly" but the backtest header runs it on 4-hour bars: FREQ = "4h" from the
      header (the source's own setting).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_380277_rsi_52_long_only"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [7, 14, 21],
    "level": [50, 52, 55],
}
DEFAULT_PARAMS = {"length": 14, "level": 52}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    rsi = _rsi(bars_df["close"], int(p["length"]))
    lv = p["level"]
    le = ((rsi > lv) & (rsi.shift(1) <= lv)).to_numpy()
    lx = ((rsi < lv) & (rsi.shift(1) >= lv)).to_numpy()
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
