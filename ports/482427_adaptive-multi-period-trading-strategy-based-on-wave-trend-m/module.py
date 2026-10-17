"""WaveTrend (10, 21) crossing up through its SMA 4 at or below -60 goes long, crossing down at or above 60 goes
short, always in, two-hour bars.
Port of FMZ strategy #482427 "基于波浪趋势动量突破的自适应多周期交易策略-Adaptive-Multi-Period-Trading-Strategy-Based-on-Wave-Trend-Momentum-Breakout" (WaveTrend [LazyBear] Strategy).

FMZ source id: 482427

Source
    https://www.fmz.com/strategy/482427 (PineScript v6, FMZ last modified 2025-02-18 13:52:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 100-139), channel 10, average 21, levels 60 / -60
    esa = ema(hlc3, 10); d = ema(|hlc3 - esa|, 10); ci = (hlc3 - esa) / (0.015 d); wt1 = ema(ci, 21); wt2 = sma(wt1, 4)
    crossover(wt1, wt2) and wt1 <= -60 -> close short, entry long; crossunder and wt1 >= 60 -> close long, entry
    short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes repeat the reversal (REVERSAL INTENDED); always in. Signal module, no stops. FREQ = "2h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, the WaveTrend oscillator.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
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

NAME = "fmz_482427_wavetrend_extreme_cross_always_in"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "level": [60.0, 53.0],
    "n2": [21, 34],
}
DEFAULT_PARAMS = {"n1": 10, "n2": 21, "level": 60.0}


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
    ci = (ap - esa) / (0.015 * d)
    wt1 = ci.ewm(span=int(p["n2"]), adjust=False).mean()
    wt2 = wt1.rolling(4).mean()
    lvl = p["level"]
    long_e = ((wt1 > wt2) & (wt1.shift(1) <= wt2.shift(1)) & (wt1 <= -lvl)).astype(bool)
    short_e = ((wt1 < wt2) & (wt1.shift(1) >= wt2.shift(1)) & (wt1 >= lvl)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
