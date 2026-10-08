"""Swing calls: EMA 5 crossing above SMA 50 with the high above the SMA goes long; EMA 5 crossing
below SMA 50 on a down bar goes short (always in).
Port of FMZ strategy #365907 "SMA call buy/sale" (SWING CALLS).

Source
    https://www.fmz.com/strategy/365907 (PineScript v4, FMZ last modified 2022-05-26 17:28:12).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 49-87), EMA 5, SMA 50
    buycall  = crossunder(sma, ema) and high > sma -> entry long
    else sellcall = crossover(sma, ema) and open > close -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The RSI 80 / 20 "reversal" markers only draw and alert.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365907_ema_sma_swing_cross"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [5, 10],
    "sma_len": [20, 50, 100],
}
DEFAULT_PARAMS = {"ema_len": 5, "sma_len": 50}


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
    o, h, c = bars_df["open"], bars_df["high"], bars_df["close"]
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    s = c.rolling(int(p["sma_len"])).mean()
    buy = ((s < e) & (s.shift(1) >= e.shift(1)) & (h > s)).to_numpy()
    sell = ((s > e) & (s.shift(1) <= e.shift(1)) & (o > c)).to_numpy()
    return _always_in(buy, sell, bars_df.index)


def portfolio_kwargs(**params):
    return {}
