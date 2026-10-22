"""Double sevens, 1-hour bars, long only: above the SMA 200, a close under the lowest of the previous 7 closes goes long; a close over the highest of the previous 7 closes closes.
Port of FMZ strategy #440451 "双7日突破策略Double-7-Days-Breakout-Strategy" (Double 7's Strategy).

FMZ source id: 440451

Source
    https://www.fmz.com/strategy/440451 (PineScript v4, FMZ last modified 2024-01-30 16:49:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 142-170), entry look-back 7, exit look-back 7; SMA 200; 100 % of equity; test period 2009-2020 (testPeriod() returns true)
    entry = lowest(close[1], 7);  exit = highest(close[1], 7);  close > sma200 and close < entry -> entry RsiLE;  close > exit -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both bands use the closes before the current bar. The test-period function returns true, so no
      window is applied. Long only. The 100 % of equity size is sizing. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close bands and SMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity is sizing.
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

NAME = "fmz_440451_double_sevens_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "value1": [7, 5],
    "value2": [7, 10],
}
DEFAULT_PARAMS = {"value1": 7, "value2": 7, "ma_len": 200}


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
    lo7 = c.shift(1).rolling(int(p["value1"])).min()
    hi7 = c.shift(1).rolling(int(p["value2"])).max()
    ma = c.rolling(int(p["ma_len"])).mean()
    buy = (c > ma) & (c < lo7)
    sell = c > hi7
    false = pd.Series(False, index=c.index)
    return buy, sell & ~buy, false, false.copy()


def portfolio_kwargs(**params):
    return {}
