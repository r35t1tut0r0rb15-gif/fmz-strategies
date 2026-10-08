"""MACD above signal, long only: as written, any bar with the MACD line above its signal goes long;
SMA 9 crossing under SMA 26 closes the long.
Port of FMZ strategy #426816 "MACD Moving Average Crossover Strategy".

Source
    https://www.fmz.com/strategy/426816 (PineScript v4, FMZ last modified 2023-09-14 17:03:47).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 164-183), MACD 12 / 26 / 9, SMA 9 / 26
    if (macd > signal) and window()
        (longCondition)                      <- a bare expression, no effect
        strategy.entry("LONG", long)
    if (crossunder(sma9, sma26)) and window()
        (SMacdcondition)                     <- a bare expression, no effect
        strategy.close("LONG")

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the SMA crossover and the MACD-below condition are statements that do nothing,
      so the entry is "MACD above signal" and the exit "SMA 9 crosses under SMA 26" (decision
      owed: the author likely meant `and`). The date window is dropped.
    * Same bar: from flat the entry stands (the close finds no position at the close); while
      long the entry is refused and the close goes flat.
    * Long only. FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426816_macd_above_signal_long"
FAMILY = "macd_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 21],
    "exit_pair": [(9, 26), (5, 20)],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "exit_pair": (9, 26)}


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
    c = bars_df["close"]
    ema = lambda x, n: x.ewm(span=int(n), adjust=False).mean()
    macd = ema(c, p["fast"]) - ema(c, p["slow"])
    entry = (macd > ema(macd, p["signal"])).to_numpy()
    d = c.rolling(int(p["exit_pair"][0])).mean() - c.rolling(int(p["exit_pair"][1])).mean()
    out = ((d < 0) & (d.shift(1) >= 0)).to_numpy()
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
