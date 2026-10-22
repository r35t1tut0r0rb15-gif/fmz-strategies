"""EMA 21 / 371 crossings, long only, 4-hour bars: the EMA 21 crossing over the EMA 371 goes long, crossing under closes.
Port of FMZ strategy #439899 "双向EMA交叉量化交易策Bidirectional-EMA-Cross-Quant-Trading-Strategy" (© Investoz trendvarningar).

FMZ source id: 439899

Source
    https://www.fmz.com/strategy/439899 (PineScript v4, FMZ last modified 2024-01-24 17:31:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 176-306), EMA ribbon 21 / 34 / 55 / 89 / 141 / 230 / 371; 5 % of equity
    PositivTrend = crossover(ema21, ema371) -> entry "Ta position" (long);  NegativTrend = crossunder(ema21, ema371) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trend-day counts and labels feed no order; the other ribbon lines are plots. The two crossings
      cannot share a bar. Long only. The 5 % of equity size is sizing. FREQ = "4h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439899_investoz_ema21_371_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema1": [21, 50],
    "ema7": [371, 200],
}
DEFAULT_PARAMS = {"ema1": 21, "ema7": 371}


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
    a = c.ewm(span=int(p["ema1"]), adjust=False).mean()
    g = c.ewm(span=int(p["ema7"]), adjust=False).mean()
    up = (a > g) & (a.shift(1) <= g.shift(1))
    dn = (a < g) & (a.shift(1) >= g.shift(1))
    false = pd.Series(False, index=c.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
