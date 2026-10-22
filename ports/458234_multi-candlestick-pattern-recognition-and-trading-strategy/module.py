"""Bullish engulfing candles, 1-hour bars, long only: the first bullish engulfing candle (default pattern) buys and the long is never closed.
Port of FMZ strategy #458234 "Multi Candlestick Pattern Recognition and Trading Strategy" (Crude Oil Candlestick Pattern Strategy).

FMZ source id: 458234

Source
    https://www.fmz.com/strategy/458234 (PineScript v5, FMZ last modified 2024-07-31 11:10:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-200), pattern choice "Bullish Engulfing" (default; bearish engulfing, hammer, shooting star optional); 10 % of equity
    pattern Bullish Engulfing: close[1] < open[1] and close > open and open <= close[1] and close >= open[1] -> entry Buy;  (other choices: Sell / Buy / Sell entries)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the default pattern is ported, so only long entries exist and nothing ever closes them: the
      first engulfing candle opens a long held to the end of the data, as written (as #451391). The
      title names crude oil; the rules are generic. The 10 % of equity size is not ported. Long only.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, engulfing candles.
    3 crypto-exchange-only: no (exchange pair in the header only (crude oil named in the title)).
    4 signals only: percent-of-equity size stored, not ported.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458234_bullish_engulfing_no_exit_long"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    o, c = bars_df["open"], bars_df["close"]
    o1, c1 = o.shift(1), c.shift(1)
    le = (c1 < o1) & (c > o) & (o <= c1) & (c >= o1)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
