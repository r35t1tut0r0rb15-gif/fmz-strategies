"""LazyBear WaveTrend crosses at the extremes, 1-hour bars: WT1 crossing above WT2 with WT2 under -60 goes long (and closes a
short); WT1 crossing under WT2 with WT2 over 60 goes short (and closes a long).
Port of FMZ strategy #433966 "Multi Take Profit and Stop Loss WaveTrend Trend Following Strategy" (WaveTrend Strategy [LazyBear] with Secondary Stop Loss).

FMZ source id: 433966

Source
    https://www.fmz.com/strategy/433966 (PineScript v4, FMZ last modified 2023-12-01 18:09:12).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 142-192), channel 10, average 21; levels 60 / -60; EMA filter off; trade mode Both; secondary stop off
    wt1 = ema(ci, 21) with ci = (hlc3 - ema(hlc3, 10)) / (0.015 ema(|hlc3 - esa|, 10));  wt2 = sma(wt1, 4)
    crossover(wt1, wt2) and wt2 < -60 -> entry long / close short;  crossunder(wt1, wt2) and wt2 > 60 -> entry short / close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The EMA filter (a 60-minute security, off by default) and the secondary percent stop (off) are
      not used. Each cross that closes one side opens the other: REVERSAL INTENDED. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator crosses at levels.
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

NAME = "fmz_433966_wavetrend_extreme_cross"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "level": [60, 53],
    "n1": [10, 20],
}
DEFAULT_PARAMS = {"level": 60, "n1": 10, "n2": 21}


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
    ap = (bars_df["high"] + bars_df["low"] + bars_df["close"]) / 3
    n1 = int(p["n1"])
    esa = ap.ewm(span=n1, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    wt1 = ((ap - esa) / (0.015 * d)).ewm(span=int(p["n2"]), adjust=False).mean()
    wt2 = wt1.rolling(4).mean()
    lv = float(p["level"])
    le = ((wt1 > wt2) & (wt1.shift(1) <= wt2.shift(1)) & (wt2 < -lv)).astype(bool)
    se = ((wt1 < wt2) & (wt1.shift(1) >= wt2.shift(1)) & (wt2 > lv)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
