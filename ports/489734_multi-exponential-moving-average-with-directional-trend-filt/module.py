"""EMA 5 / 8 crossings, hourly bars: the up-cross goes long, the down-cross goes short; a close back through the EMA 13 closes the held side; reversing.
Port of FMZ strategy #489734 "Multi Exponential Moving Average with Directional Trend Filter Trading System" ([SM-042] EMA 5-8-13 with ADX Filter).

FMZ source id: 489734

Source
    https://www.fmz.com/strategy/489734 (PineScript v5, FMZ last modified 2025-04-08 10:13:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 195-240), EMA 5 / 8 / 13; ADX filter off; 100 % of equity
    crossover(ema5, ema8) -> entry Long;  crossunder -> entry Short;  long and close < ema13 -> close Long;  short and close > ema13 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ADX filter is off by default. The EMA 13 closes act on a held position (from the bar after the
      entry signal). An entry on the other side reverses (REVERSAL INTENDED). MPL 2.0 source (the notice is
      kept: Mozilla Public License 2.0, © sebamarghella). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with an EMA exit.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: capital 1000, 100 % of equity stored, not ported.
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

NAME = "fmz_489734_ema5_8_cross_ema13_exit_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 3],
    "slow": [8, 13],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 8, "exit": 13}


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

    def ema(n):
        return c.ewm(span=int(n), adjust=False).mean()

    f, s, x = ema(p["fast"]), ema(p["slow"]), ema(p["exit"])
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    lx = (c < x) & ~le & ~se
    sx = (c > x) & ~se & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
