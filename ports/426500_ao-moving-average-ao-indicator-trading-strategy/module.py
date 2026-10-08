"""MA & AO, long only: EMA 8 crossing above SMA 20 with the close above SMA 20 and the AO
(SMA 5 - SMA 8 of hl2) rising goes long; EMA 8 and the close below SMA 20 with the AO falling
closes the long.
Port of FMZ strategy #426500 "AO Moving Average AO Indicator Trading Strategy".

Source
    https://www.fmz.com/strategy/426500 (PineScript v4, FMZ last modified 2023-09-12 16:09:01).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 119-141), EMA 8, SMA 20, AO 5 / 8
    dif = sma(hl2, 5) - sma(hl2, 8)
    AO = dif >= 0 ? (dif > dif[1] ? 1 : 2) : (dif > dif[1] ? -1 : -2)
    crossover(ema8, sma20) and close > sma20 and abs(AO) == 1 -> entry long
    ema8 < sma20 and close < sma20 and abs(AO) == 2           -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only (no short entry). dif > na is false, so the first bar reads |AO| = 2.
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426500_ma_ao_long"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_ma": [8, 13],
    "slow_ma": [20, 34],
}
DEFAULT_PARAMS = {"fast_ma": 8, "slow_ma": 20, "ao_fast": 5, "ao_slow": 8}


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
    c = bars_df["close"]
    hl2 = (bars_df["high"] + bars_df["low"]) / 2
    fast = c.ewm(span=int(p["fast_ma"]), adjust=False).mean()
    slow = c.rolling(int(p["slow_ma"])).mean()
    dif = hl2.rolling(int(p["ao_fast"])).mean() - hl2.rolling(int(p["ao_slow"])).mean()
    rising = dif > dif.shift(1)  # |AO| == 1; otherwise |AO| == 2
    le = (fast > slow) & (fast.shift(1) <= slow.shift(1)) & (c > slow) & rising
    lx = (fast < slow) & (c < slow) & ~rising
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
