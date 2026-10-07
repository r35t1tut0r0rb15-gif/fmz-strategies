"""RSI(14) oversold buy / overbought sell, long only, on 4-hour bars ("practice 01 RSI").
Port of FMZ strategy #288889 "练习01RSI".

Source
    https://www.fmz.com/strategy/288889 (Python, author "3028165668", FMZ last modified
    2021-06-09 10:24:00). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 18-42)
    r = GetRecords(PERIOD_H1 * 4); rsi = TA.RSI(r, 14)
    rsi[-1] > 70 and coins held  -> sell 1 % of the coins
    rsi[-1] < 30 and cash held   -> buy with 1 % of the cash
    (no sleep in the loop; 4 minutes' pause after an order)

Interpretation choices
    * The bot re-trades 1 % slices on every loop while the RSI stays beyond a threshold: the
      slice size and repetition are sizing (criterion 4). The signal is: in the market from an
      RSI < 30 bar, out at an RSI > 70 bar.
    * It reads the forming 4-hour bar; the port evaluates on completed bar t ([-1] -> t).
      RSI is Wilder's (TA.RSI).
    * Long only (spot); shorts are never emitted, so opposite entries cannot occur.
    * FREQ = "4h" (code requests PERIOD_H1 * 4). No backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_288889_rsi_30_70_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # code requests PERIOD_H1 * 4
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_period": [7, 14, 21],
    "zone": [20, 30],
}
DEFAULT_PARAMS = {"rsi_period": 14, "zone": 30}


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
    rsi = _rsi(bars_df["close"], int(p["rsi_period"])).to_numpy()
    lo, hi = p["zone"], 100 - p["zone"]

    m = len(rsi)
    entries, exits = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    in_pos = False
    for i in range(m):
        if not in_pos and rsi[i] < lo:
            entries[i], in_pos = True, True
        elif in_pos and rsi[i] > hi:
            exits[i], in_pos = True, False

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(entries, index=idx), pd.Series(exits, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
