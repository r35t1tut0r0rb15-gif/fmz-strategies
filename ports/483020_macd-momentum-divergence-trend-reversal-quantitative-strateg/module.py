"""Fading MACD 12 / 26 / 9 histogram against a bigger candle, hourly bars: a bullish candle larger than the last while the histogram falls two bars running goes short, a bearish larger candle while it rises goes long; reversing, no other exit.
Port of FMZ strategy #483020 "动量背离趋势反转量化策略基于MACD柱状图-Momentum-Divergence-Trend-Reversal-Quantitative-Strategy-Based-on-MACD-Histogram" (MACD Momentum Reversal Strategy).

FMZ source id: 483020

Source
    https://www.fmz.com/strategy/483020 (PineScript v5, FMZ last modified 2025-02-21 09:25:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-150), MACD 12 / 26 / 9 histogram; candle body vs the previous body; 10 % of equity, capital 100000
    close > open and body > body[1] and hist[2] > hist[1] > hist -> entry Short;  close < open and body > body[1] and hist[2] < hist[1] < hist -> entry Long
    long and enterShort -> close Long;  short and enterLong -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes coincide with the opposite entries, so each signal is a reversal (REVERSAL INTENDED); no
      other exit. A bullish and a bearish candle cannot share a bar. The 10 % of equity size and the
      capital are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD histogram fades against a bigger candle.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity and capital stored, not ported.
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

NAME = "fmz_483020_macd_hist_fade_bigger_candle_contrarian_reversal"
FAMILY = "macd_momentum"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_length": [12, 8],
    "signal_length": [9, 5],
}
DEFAULT_PARAMS = {"fast_length": 12, "signal_length": 9, "slow_length": 26}


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
    o, c = bars_df["open"], bars_df["close"]

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    macd = ema(c, p["fast_length"]) - ema(c, p["slow_length"])
    hist = macd - ema(macd, p["signal_length"])
    body = (c - o).abs()
    bigger = body > body.shift(1)
    falling = (hist.shift(2) > hist.shift(1)) & (hist.shift(1) > hist)
    rising = (hist.shift(2) < hist.shift(1)) & (hist.shift(1) < hist)
    se = (c > o) & bigger & falling
    le = (c < o) & bigger & rising
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
