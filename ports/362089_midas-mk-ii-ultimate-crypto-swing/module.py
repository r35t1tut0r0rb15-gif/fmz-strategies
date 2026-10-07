"""EMA21 / SMA55 cross confirmed by a slow MACD(55,89,9) histogram (non-negative or rising two
bars for longs; mirror for shorts), stop-and-reverse.
Port of FMZ strategy #362089 "Midas-Mk-II-Ultimate-Crypto-Swing".

Source
    https://www.fmz.com/strategy/362089 (PineScript v5, FMZ last modified 2022-05-09 23:22:05).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 44-67)
    hist = macd(close, 55, 89, 9) histogram
    long  = crossover(ema(close,21), sma(close,55)) and (hist >= 0 or (hist > hist[1] and hist[1] > hist[2]))
    short = crossunder(...) and (hist <= 0 or (hist < hist[1] and hist[1] < hist[2]))
    long -> entry long;  else short -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "15min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362089_ema_sma_cross_macd_confirm"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [13, 21, 34],
    "sma_len": [34, 55, 89],
}
DEFAULT_PARAMS = {"ema_len": 21, "sma_len": 55, "macd_fast": 55, "macd_slow": 89, "macd_signal": 9}


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
    macd = c.ewm(span=int(p["macd_fast"]), adjust=False).mean() - c.ewm(span=int(p["macd_slow"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["macd_signal"]), adjust=False).mean()
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    s = c.rolling(int(p["sma_len"])).mean()
    xo = (e > s) & (e.shift(1) <= s.shift(1))
    xu = (e < s) & (e.shift(1) >= s.shift(1))
    rising = (hist > hist.shift(1)) & (hist.shift(1) > hist.shift(2))
    falling = (hist < hist.shift(1)) & (hist.shift(1) < hist.shift(2))
    warm = np.arange(len(c)) >= int(p["macd_slow"])
    long_c = (xo & ((hist >= 0) | rising)).to_numpy() & warm
    short_c = (xu & ((hist <= 0) | falling)).to_numpy() & warm
    return _always_in(long_c, short_c, bars_df.index)


def portfolio_kwargs(**params):
    return {}
