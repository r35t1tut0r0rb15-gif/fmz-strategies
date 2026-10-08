"""Winners breakout, long only: the close crossing above the 10-bar average of the 200-bar highest
high goes long; crossing under that level minus 2 ATR(14) closes it.
Port of FMZ strategy #426879 "Trend Following Strategy Based on Dynamic Support and Resistance".

Source
    https://www.fmz.com/strategy/426879 (PineScript v4, FMZ last modified 2023-09-15 11:28:00).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 132-146), highest 200, average 10, ATR 14 x 2
    h = sma(highest(high, 200), 10); l = h - 2 atr(14)
    crossover(close, h) -> entry long;  crossunder(close, l) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Same bar: from flat the entry stands; while long the close goes flat (Pine order).
    * Long only. Daily bars are broker days (session ending 17:00 New York), stamped with the
      session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426879_highest_average_breakout_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "highest_length": [100, 200],
    "atr_multiplier": [2, 3],
}
DEFAULT_PARAMS = {"highest_length": 200, "highest_average": 10, "atr_length": 14, "atr_multiplier": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
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
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    hline = bars_df["high"].rolling(int(p["highest_length"])).max().rolling(int(p["highest_average"])).mean()
    lline = hline - p["atr_multiplier"] * _atr_pine(bars_df, int(p["atr_length"]))
    entry = ((c > hline) & (c.shift(1) <= hline.shift(1))).to_numpy()
    out = ((c < lline) & (c.shift(1) >= lline.shift(1))).to_numpy()
    target = np.zeros(len(c), dtype=int)
    pos = 0
    for i in range(len(c)):
        if pos == 0 and entry[i]:
            pos = 1
        elif pos == 1 and out[i]:
            pos = 0
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
