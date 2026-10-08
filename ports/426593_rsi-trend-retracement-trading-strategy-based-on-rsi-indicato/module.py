"""RSI(2) extremes: RSI above 96 goes short, below 4 goes long; a short is closed when RSI falls
under 20, a long when it rises over 80. The source's tick trailing stop is pending (rule 2).
Port of FMZ strategy #426593 "RSI Trend Retracement Trading Strategy Based on RSI Indicator".

Source
    https://www.fmz.com/strategy/426593 (PineScript v5, FMZ last modified 2023-09-13 15:33:26).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 74-125), RSI 2, 96 / 4, take profit 20 / 80, trail 100
    rsi > 96 -> entry short;  rsi < 20 -> close short
    rsi < 4  -> entry long;   rsi > 80 -> close long
    while in a position: exit(trail_price = extreme since entry, trail_offset = 100 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Orders fill at the next open in issue order: an entry that reverses an opposite position
      is not undone by that bar's close of the other side (which then finds nothing).
    * The trailing stop (activation at the highest high / lowest low since the entry signal,
      100-tick offset; criterion 2 would make the offset an ATR multiple) moves after entry: rule
      2, mark trailing_stop_pending, not emitted. See PORT_NOTES.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_426593_rsi2_extremes"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [2, 3],
    "extreme": [4, 8],
    "take": [20, 30],
}
DEFAULT_PARAMS = {"rsi_len": 2, "extreme": 4, "take": 20}  # levels 100 - extreme / extreme, 100 - take / take


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


def _rsi_pine(close, n):
    """rsi() as Pine defines it: 100 when the average loss is 0, 0 when the average gain is 0."""
    d = close.diff()
    up, down = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = 100.0 - 100.0 / (1.0 + up / down)
    return rsi.mask(up == 0, 0.0).mask(down == 0, 100.0).where(up.notna() & down.notna())


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
    rsi = _rsi_pine(bars_df["close"], int(p["rsi_len"])).to_numpy()
    sell_lvl, buy_lvl = 100 - p["extreme"], p["extreme"]
    tp_sell, tp_buy = p["take"], 100 - p["take"]
    target = np.zeros(len(rsi), dtype=int)
    pos = 0
    for i in range(len(rsi)):
        before = pos
        if rsi[i] > sell_lvl:
            pos = -1
        elif rsi[i] < buy_lvl:
            pos = 1
        elif before == -1 and rsi[i] < tp_sell:
            pos = 0
        elif before == 1 and rsi[i] > tp_buy:
            pos = 0
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
