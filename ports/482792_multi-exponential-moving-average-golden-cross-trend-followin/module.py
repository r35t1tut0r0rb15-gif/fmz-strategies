"""EMA 20 / 50 golden crosses from flat, closed at the death cross, long only, hourly bars.
Port of FMZ strategy #482792 "多重指数移动平均线黄金交叉趋势跟踪策略-Multi-Exponential-Moving-Average-Golden-Cross-Trend-Following-Strategy" (EMA2050150 Crossover Strategy#ganges).

FMZ source id: 482792

Source
    https://www.fmz.com/strategy/482792 (PineScript v6, FMZ last modified 2025-02-27 17:48:40).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 96-131), EMA 20 / 50 (EMA 150 only drawn)
    crossover(ema20, ema50) and flat -> entry long; crossunder(ema20, ema50) and long -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The crosses alternate, so the flat / long tests change nothing: entries on golden crosses, exits on death
      crosses. The EMA 150 crosses feed only drawings.
    * Long only. Signal module, no stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, two EMAs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity; commission and slippage settings are costs, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482792_ema20_50_cross_long"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    long_x = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
