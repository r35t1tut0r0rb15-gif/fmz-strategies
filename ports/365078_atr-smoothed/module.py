"""ATR trailing stop (21, x 6.3) flips: close crossing above the trailing stop goes long, crossing
below goes short (always in).
Port of FMZ strategy #365078 "ATR Smoothed (By dysrupt)_BuySell version".

Source
    https://www.fmz.com/strategy/365078 (PineScript v3, FMZ last modified 2022-05-23 14:12:08).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 46-121), ATR period 21, multiplier 6.3
    nLoss = 6.3 * atr(21); stop ratchets with the close (nz(stop[1], 0) seeds)
    pos = close crosses above stop[1] ? 1 : crosses below ? -1 : pos[1]
    LONG = not isLong and pos == 1 -> entry long; else SHORT = not isShort and pos == -1 -> short

Interpretation choices (Pine rules in SURVEY_README.md)
    * isLong / isShort latch the last signal, so LONG / SHORT are the first bars of a new pos.
    * The VWMA "smooth" line (needs volume) only draws; it is not ported and no volume is used.
    * The alert titles are swapped in the source (LONG titled "Sell"); the orders are as coded.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365078_atr_trailing_stop_flip"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_period": [14, 21, 28],
    "mult": [3.0, 4.5, 6.3],
}
DEFAULT_PARAMS = {"atr_period": 21, "mult": 6.3}


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


def _atr_trail_pos(close, atr_mult_series):
    """Classic ATR trailing stop (nz(prev, 0) seeds) and its position: 1 when close crosses above
    the previous stop, -1 when it crosses below, else the previous position."""
    c = np.asarray(close, dtype=float)
    loss = np.asarray(atr_mult_series, dtype=float)
    m = len(c)
    stop = np.full(m, np.nan)
    pos = np.zeros(m)
    for i in range(m):
        ps = stop[i - 1] if i and not np.isnan(stop[i - 1]) else 0.0
        c1 = c[i - 1] if i else np.nan
        if c[i] > ps and c1 > ps:
            stop[i] = max(ps, c[i] - loss[i])
        elif c[i] < ps and c1 < ps:
            stop[i] = min(ps, c[i] + loss[i])
        elif c[i] > ps:
            stop[i] = c[i] - loss[i]
        else:
            stop[i] = c[i] + loss[i]
        prev = pos[i - 1] if i else 0.0
        pos[i] = 1.0 if (c1 < ps and c[i] > ps) else (-1.0 if (c1 > ps and c[i] < ps) else prev)
    return stop, pos


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
    loss = p["mult"] * _atr_pine(bars_df, int(p["atr_period"]))
    _, pos = _atr_trail_pos(bars_df["close"], loss)
    return _always_in(pos == 1, pos == -1, bars_df.index)


def portfolio_kwargs(**params):
    return {}
