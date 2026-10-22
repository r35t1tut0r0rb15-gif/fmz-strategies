"""EMA 10 / 50 crossings in the EMA 200 trend, hourly bars: the cross up with the close and EMA 50 above the EMA 200 goes long, the mirror goes short; any opposite crossing closes; reversing.
Port of FMZ strategy #477977 "多重EMA交叉趋势跟踪量化交易策略-Multi-EMA-Crossover-Trend-Following-Quantitative-Trading-Strategy" (EMA Crossover Strategy (Enhanced Debug)).

FMZ source id: 477977

Source
    https://www.fmz.com/strategy/477977 (PineScript v5, FMZ last modified 2025-01-10 16:33:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-152), EMA 10 / 50 / 200; debug labels only
    close > ema200 and crossover(ema10, ema50) and ema50 > ema200 -> entry Long;  mirror -> entry Short;  crossunder(ema10, ema50) -> close Long;  crossover -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close acts only on the held position and leaves a same-bar reversal standing (as #441963). The
      debug labels only draw. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings in an EMA 200 trend.
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

NAME = "fmz_477977_ema10_50_cross_ema200_trend_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_ema": [10, 20],
    "medium_ema": [50, 100],
}
DEFAULT_PARAMS = {"short_ema": 10, "medium_ema": 50, "long_ema": 200}


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
    a = c.ewm(span=int(p["short_ema"]), adjust=False).mean()
    b = c.ewm(span=int(p["medium_ema"]), adjust=False).mean()
    t = c.ewm(span=int(p["long_ema"]), adjust=False).mean()
    up = (a > b) & (a.shift(1) <= b.shift(1))
    dn = (a < b) & (a.shift(1) >= b.shift(1))
    le = (c > t) & up & (b > t)
    se = (c < t) & dn & (b < t)
    return le, dn & ~se, se, up & ~le


def portfolio_kwargs(**params):
    return {}
