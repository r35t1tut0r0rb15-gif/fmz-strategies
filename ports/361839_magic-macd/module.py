"""Standard MACD(12,26,9) signal-line cross, stop-and-reverse, on hourly bars (the orders of
"MAGIC MACD" use ta.macd(close,12,26,9), not the indicator's custom MACD).
Port of FMZ strategy #361839 "MAGIC-MACD".

Source
    https://www.fmz.com/strategy/361839 (PineScript v5, FMZ last modified 2022-05-08 17:16:51).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 167-180)
    [macd2, signal2, hist2] = ta.macd(close, 12, 26, 9)
    ta.crossover(macd2, signal2) -> entry long;  else ta.crossunder(...) -> entry short
    (the 5/50/30 ohlc4 MACD, the EMA50 filter and the EMA1/EMA2 lines colour the plots only)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.crossover = a > b and a[1] <= b[1].
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361839_macd_cross_reverse_1h"
FAMILY = "macd_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 12, 16],
    "slow": [21, 26, 34],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


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
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    warm = np.arange(len(c)) >= int(p["slow"])
    up = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy() & warm
    dn = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy() & warm
    return _always_in(up, dn, bars_df.index)


def portfolio_kwargs(**params):
    return {}
