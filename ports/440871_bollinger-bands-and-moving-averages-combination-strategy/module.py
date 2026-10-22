"""Band breakouts on a golden cross, 2-minute bars: the close crossing over the upper band (20, 2) on the same bar as the SMA 50 crosses over the SMA 200 goes long, the mirror short; reversing.
Port of FMZ strategy #440871 "Bollinger Bands and Moving Averages Combination Strategy" (Bollinger Bands and Moving Averages Strategy).

FMZ source id: 440871

Source
    https://www.fmz.com/strategy/440871 (PineScript v4, FMZ last modified 2024-02-02 17:47:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 147-172), BB 20 / 2; SMA 50 / 200
    longCondition = crossover(close, upper) and crossover(sma50, sma200) -> entry Long;  shortCondition mirrored -> entry Short;  close Long on shortCondition, close Short on longCondition

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes come with the opposite entries and leave the reversals standing (as #438020). Pine's
      stdev is the population deviation. strategy.entry reverses: REVERSAL INTENDED. No sizing code.
      FREQ = "2min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band breakout with an SMA cross.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440871_band_breakout_on_golden_cross"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1_length": [50, 20],
    "ma2_length": [200, 100],
}
DEFAULT_PARAMS = {"ma1_length": 50, "ma2_length": 200, "length": 20, "mult": 2.0}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, lo = basis + dev, basis - dev
    a = c.rolling(int(p["ma1_length"])).mean()
    b = c.rolling(int(p["ma2_length"])).mean()

    def xo(x, y):
        return (x > y) & (x.shift(1) <= y.shift(1))

    lg = xo(c, up) & xo(a, b)
    sh = xo(lo, c) & xo(b, a)
    false = pd.Series(False, index=c.index)
    return lg, false, sh, false.copy()


def portfolio_kwargs(**params):
    return {}
