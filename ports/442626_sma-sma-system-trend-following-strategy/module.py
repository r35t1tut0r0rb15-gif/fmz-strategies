"""The close crossing its SMA 3 (an SMA 1 against an SMA 3), 1-hour bars: crossing over goes long, under goes short; the stop as written sits below zero on the BTC reading and never acts; reversing.
Port of FMZ strategy #442626 "基于SMA均线系统的趋势跟踪策略SMA-System-Trend-Following-Strategy" (Estrategia SMA y Ganancias Acumuladas con Stop Loss (SMA_Ganancias)).

FMZ source id: 442626

Source
    https://www.fmz.com/strategy/442626 (PineScript v5, FMZ last modified 2024-02-23 12:29:51).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 115-153), SMA 1 / 3; stop loss 5000 "pips"
    crossover(sma1, sma3) -> entry Buy;  crossunder -> entry Sell;  exit(SL, Buy, stop = avg x (1 - 5000 x mintick))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop multiplies the average price by 1 - 5000 x mintick: at mintick 0.1 on the BTC reading
      that is 1 - 500, a negative price, so the stop never acts and is not ported. The profit counters
      only record strategy.netprofit. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, the tick-scaled stop never acts on the BTC reading.
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

NAME = "fmz_442626_close_sma3_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow": [3, 10],
    "fast": [1, 2],
}
DEFAULT_PARAMS = {"slow": 3, "fast": 1}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
