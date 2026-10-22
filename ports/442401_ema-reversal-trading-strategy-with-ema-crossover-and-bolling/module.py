"""EMA 50 / 200 crossings and Bollinger band breaks, 1-hour bars: the EMA 50 crossing over the EMA 200 or the close crossing under the lower band (20, 2) goes long; the EMA cross under or the close crossing
over the upper band goes short; reversing.
Port of FMZ strategy #442401 "双EMA穿越与布林带回转策略Reversal-Trading-Strategy-with-EMA-Crossover-and-Bollinger-Bands" (RP-EMABB).

FMZ source id: 442401

Source
    https://www.fmz.com/strategy/442401 (PineScript v4, FMZ last modified 2024-02-21 16:12:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 164-204), EMA 50 / 200; BB 20 / 2
    emaCrossover or crossunder(close, bbLower) -> entry Buy;  emaCrossunder or crossover(close, bbUpper) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * When both fire on one bar the later call (Sell) wins (as #437773). Pine's stdev is the population
      deviation. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings and band breaks.
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

NAME = "fmz_442401_ema50_200_cross_band_break_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_short": [50, 20],
    "bb_length": [20, 50],
}
DEFAULT_PARAMS = {"ema_short": 50, "bb_length": 20, "ema_long": 200, "bb_mult": 2.0}


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
    es = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    el = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    c1 = c.shift(1)
    buy = ((es > el) & (es.shift(1) <= el.shift(1))) | ((c < dn) & (c1 >= dn.shift(1)))
    sell = ((es < el) & (es.shift(1) >= el.shift(1))) | ((c > up) & (c1 <= up.shift(1)))
    false = pd.Series(False, index=c.index)
    return buy & ~sell, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
