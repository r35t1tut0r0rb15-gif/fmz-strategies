"""EMA high / low channel, 1-hour bars, long only: the close crossing over the EMA 20 of the highs goes long, crossing under the EMA 20 of the lows closes.
Port of FMZ strategy #440429 "基于20日EMA通道的交易策略All-about-EMA-Channel-Trading-Strategy" (EMA Channel Strategy with Alerts).

FMZ source id: 440429

Source
    https://www.fmz.com/strategy/440429 (PineScript v4, FMZ last modified 2024-01-30 15:24:07).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 115-140), EMA length 20 on high and low
    buyCondition = crossover(close, ema(high, 20)) -> entry Buy;  sellCondition = crossunder(close, ema(low, 20)) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two crossings cannot happen on one bar. Long only. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA channel crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440429_ema20_high_low_channel_long"
FAMILY = "ma_envelope_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [20, 50],
}
DEFAULT_PARAMS = {"ema_len": 20}


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
    n = int(p["ema_len"])
    eh = bars_df["high"].ewm(span=n, adjust=False).mean()
    el = bars_df["low"].ewm(span=n, adjust=False).mean()
    buy = (c > eh) & (c.shift(1) <= eh.shift(1))
    sell = (c < el) & (c.shift(1) >= el.shift(1))
    false = pd.Series(False, index=c.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
