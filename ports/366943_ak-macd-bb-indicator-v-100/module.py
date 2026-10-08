"""AK MACD BB: MACD (12 / 26) above a 10-bar Bollinger band of itself (1 sd) goes long; below the
lower band goes short (always in).
Port of FMZ strategy #366943 "AK MACD BB v 1.00".

Source
    https://www.fmz.com/strategy/366943 (PineScript v2/v3 syntax, FMZ last modified 2022-05-31 19:05:37).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 47-89), BB periods 10, deviations 1, MACD 12 / 26
    Upper / Lower = sma(macd, 10) +- 1 * stdev(macd, 10)
    macd > Upper -> entry long; else macd < Lower -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Population stdev. The signal length input (9) is unused.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "45min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366943_macd_bollinger_break"
FAMILY = "macd_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "dev": [1.0, 1.5, 2.0],
}
DEFAULT_PARAMS = {"length": 10, "dev": 1.0, "fast": 12, "slow": 26}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    n = int(p["length"])
    mid, sd = macd.rolling(n).mean(), macd.rolling(n).std(ddof=0)
    up = (macd > mid + p["dev"] * sd).to_numpy()
    dn = (macd < mid - p["dev"] * sd).to_numpy()
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
