"""Volume spikes split by candle colour, 45-minute bars: an up bar's volume crossing over 3.1 times its 14-bar average of up-bar volume goes long, otherwise a down bar's volume crossing over 3.1 times its average goes short; reversing.
Port of FMZ strategy #365085 "Volume Flow v3" (Volume Flow v3 [DepthHouse]).

FMZ source id: 365085

Source
    https://www.fmz.com/strategy/365085 (PineScript v4, FMZ last modified 2022-05-23 14:40:50).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 49-107), MA Simple 14; breakout factor 3.1
    bull = close > open ? volume : 0;  bear = open > close ? volume : 0;  gsig = crossover(bull, sma(bull, 14) x 3.1) ? volume : na;  rsig mirror
    gsig -> entry Long;  else rsig -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A study() script sending strategy orders on FMZ; the moving-average menu takes its default
      (Simple). A signal value of the bar's volume counts as true when it is not zero. REVERSAL INTENDED.
      No sizing code. FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, colour-split volume spikes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) split into up-bar / down-bar volume and its 14-bar SMA spikes; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365085_bull_bear_volume_spike_x3_reversal"
FAMILY = "momentum_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 30],
    "x": [3.1, 2.0],
}
DEFAULT_PARAMS = {"length": 14, "x": 3.1}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    n, x = int(p["length"]), float(p["x"])
    bull = v.where(c > o, 0.0)
    bear = v.where(o > c, 0.0)
    bt, rt = bull.rolling(n).mean() * x, bear.rolling(n).mean() * x
    le = (bull > bt) & (bull.shift(1) <= bt.shift(1)) & (v != 0)
    se = (bear > rt) & (bear.shift(1) <= rt.shift(1)) & (v != 0) & ~le
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
