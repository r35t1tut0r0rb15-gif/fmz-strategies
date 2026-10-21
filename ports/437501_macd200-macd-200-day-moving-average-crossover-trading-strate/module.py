"""MACD side with an SMA 200 test, 1-minute bars: the MACD above its signal but below zero with the close above the SMA 200 is long; the MACD below its signal but above zero with the close under the SMA 200 is
short; entries are sent on every qualifying bar, reversing.
Port of FMZ strategy #437501 "MacD200日均线信号交叉交易策略MACD-200-Day-Moving-Average-Crossover-Trading-Strategy" (MacD 200 Day Moving Average Signal Crossover Strategy).

FMZ source id: 437501

Source
    https://www.fmz.com/strategy/437501 (PineScript v4, FMZ last modified 2024-01-03 11:50:56).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 146-182), MACD 12 / 26 / 9 (EMA), SMA 200
    macd > signal and macd < 0 and close > sma(close, 200) -> entry buy;  close < sma 200 and macd < signal and macd > 0 -> entry sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are levels, so the entry is sent on every qualifying bar; a same-side entry while in
      the position is ignored (pyramiding 0). REVERSAL INTENDED. The 100 % of equity size and commission
      are sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD side and SMA test.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and commission stored.
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

NAME = "fmz_437501_macd_side_sma200"
FAMILY = "macd_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "ma_length": [200, 100],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "ma_length": 200}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    ma = c.rolling(int(p["ma_length"])).mean()
    lc = (macd > sig) & (macd < 0) & (c > ma)
    sc = (c < ma) & (macd < sig) & (macd > 0)
    false = pd.Series(False, index=bars_df.index)
    return lc, false, sc, false.copy()


def portfolio_kwargs(**params):
    return {}
