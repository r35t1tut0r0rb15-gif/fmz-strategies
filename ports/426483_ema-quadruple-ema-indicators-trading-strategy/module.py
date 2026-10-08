"""DEMA-change EMA cross with unit orders: EMA 44 of the 14-bar DEMA's change crossing above its
EMA 72 buys one unit, crossing below sells one unit. The crosses alternate, so the position
alternates between one unit and flat on the side of the first cross in the data.
Port of FMZ strategy #426483 "Quadruple EMA Indicators Trading Strategy".

Source
    https://www.fmz.com/strategy/426483 (PineScript v5, FMZ last modified 2023-09-12 14:53:22).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 108-132), slow 44, fast 72, period 14, res "120"
    closeSeries = security(res, 2 ema(close, 14) - ema(ema(close, 14), 14))
    openSeries  = security(res, 2 ema(close[1], 14) - ema(ema(close[1], 14), 14))
    slowema = ema(closeSeries - openSeries, 44); fastema = ema(closeSeries - openSeries, 72)
    crossover(slowema, fastema)  -> strategy.order BUY 1
    crossunder(slowema, fastema) -> strategy.order SELL 1

Interpretation choices (Pine rules in SURVEY_README.md)
    * res "120" equals the 2h header bars, so security() returns the chart series itself.
    * strategy.order does not reverse: each order adds +-1 unit to the net position. As the
      crosses alternate, the position is +1 / 0 when the first cross is up and -1 / 0 when it is
      down: the side depends on where the data starts (decision owed, as #366388 / #370711).
    * Opposite entries cannot occur: every second order is an exit to flat.
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426483_dema_change_ema_cross_units"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_slow": [44, 21],
    "ema_fast": [72, 100],
    "length": [14, 21],
}
DEFAULT_PARAMS = {"ema_slow": 44, "ema_fast": 72, "length": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    n = int(p["length"])
    ema = lambda x, k: x.ewm(span=int(k), adjust=False).mean()
    c = bars_df["close"]
    c1 = c.shift(1)
    close_s = 2 * ema(c, n) - ema(ema(c, n), n)
    open_s = 2 * ema(c1, n) - ema(ema(c1, n), n)
    x = close_s - open_s
    d = ema(x, p["ema_slow"]) - ema(x, p["ema_fast"])
    d1 = d.shift(1)
    up = ((d > 0) & (d1 <= 0)).to_numpy()
    dn = ((d < 0) & (d1 >= 0)).to_numpy()
    target = np.zeros(len(c), dtype=int)
    pos = 0
    for i in range(len(c)):
        pos += int(up[i]) - int(dn[i])
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
