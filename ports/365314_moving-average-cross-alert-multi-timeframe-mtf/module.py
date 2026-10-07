"""ChartArt MA cross: EMA 50 crossing above EMA 100 on an up-close bar goes long; crossing below on
a down-close bar goes short (always in).
Port of FMZ strategy #365314 "Moving Average Cross Alert, Multi-Timeframe Option (MTF) (by ChartArt)".

Source
    https://www.fmz.com/strategy/365314 (PineScript v2/v3 syntax, FMZ last modified 2022-05-24 11:23:02).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 81-137), current resolution, EMA 50 / 100 (type 2)
    Uptrend = short > long and (short < long)[1];  Buy = Uptrend and close > close[1]
    Downtrend mirrors;  Sell = Downtrend and close < close[1]
    Buy -> entry long; else Sell -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Use Current Timeframe As Resolution" defaults to true: security() returns the chart series.
    * MA type default 2 (EMA).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "15min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365314_ema_cross_close_confirm"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short": [20, 50],
    "long": [100, 200],
}
DEFAULT_PARAMS = {"short": 50, "long": 100}


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
    s = c.ewm(span=int(p["short"]), adjust=False).mean()
    l = c.ewm(span=int(p["long"]), adjust=False).mean()
    buy = ((s > l) & (s.shift(1) < l.shift(1)) & (c > c.shift(1))).to_numpy()
    sell = ((s < l) & (s.shift(1) > l.shift(1)) & (c < c.shift(1))).to_numpy()
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
