"""Close vs MA20 entries with a close-vs-MA10 exit, both sides ("MA, simple version").
Port of FMZ strategy #318486 "均线傻瓜版".

Source
    https://www.fmz.com/strategy/318486 (JavaScript, author "sabar", FMZ last modified
    2021-09-23 17:15:26). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 40-96), once per new bar on records[-1]
    long:  Bar.Close < MA10 -> close (idle);  short: Bar.Close > MA10 -> close (idle)
    then, if idle: Bar.Close > MA20 -> buy;  Bar.Close < MA20 -> sell short

Interpretation choices
    * The bot acts on the first poll of each new bar, reading the new (forming) bar as
      records[-1]; the port evaluates on completed bar t ([-1] -> t; MAs include t).
    * The exit and the idle check run in the same pass, so an exit can be followed at once by an
      entry: the opposite side is a one-bar reversal (REVERSAL INTENDED; portfolio_kwargs {}),
      and the same side means the position simply stays open (no signal).
    * FREQ = "5min" from the backtest header (GetRecords() default period).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_318486_ma20_entry_ma10_exit"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_exit": [5, 10, 20],
    "ma_entry": [10, 20, 40],
}
DEFAULT_PARAMS = {"ma_exit": 10, "ma_entry": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    close = bars_df["close"]
    c = close.to_numpy(dtype=float)
    mx = close.rolling(int(p["ma_exit"])).mean().to_numpy()
    me = close.rolling(int(p["ma_entry"])).mean().to_numpy()

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        was = pos
        if pos == 1 and c[i] < mx[i]:
            pos = 0
        elif pos == -1 and c[i] > mx[i]:
            pos = 0
        if pos == 0:
            if c[i] > me[i]:
                pos = 1
            elif c[i] < me[i]:
                pos = -1
        if pos != was:
            if pos == 1:
                le[i] = True
            elif pos == -1:
                se[i] = True
            elif was == 1:
                lx[i] = True
            else:
                sx[i] = True

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
