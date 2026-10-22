"""Gap candles, 1-hour bars: a green candle opening above the previous close goes long, a red candle opening below it short; reversing (as written the supertrend direction does not change which entry is
sent).
Port of FMZ strategy #440537 "Supertrend BarUpDn Fusion Strategy" (Supertrend and BarUpDn Indicator Fusion).

FMZ source id: 440537

Source
    https://www.fmz.com/strategy/440537 (PineScript v5, FMZ last modified 2024-01-31 14:43:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 159-193), supertrend ATR 10, factor 3
    barUpDn = close > open and open > close[1] ? 1 : close < open and open < close[1] ? -1 : 0;  lastBar = barUpDn (reset each bar);  long = direction > 0 and barUpDn == 1 -> entry Long, else short = direction < 0 and barUpDn == -1 -> entry Short
    direction < 0 and barUpDn > 0 -> entry Long;  direction > 0 and barUpDn < 0 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * lastBar is declared each bar (not var), so it equals barUpDn. The two pairs of rules cover both
      supertrend directions: an up gap candle always enters long and a down one short, whatever the
      direction, so the supertrend is not needed (it is defined from the first bars). strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, gap candles.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440537_gap_candle_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "gap_lag": [1],
}
DEFAULT_PARAMS = {"gap_lag": 1}


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
    pc = c.shift(int(p["gap_lag"]))
    up = (c > o) & (o > pc)
    dn = (c < o) & (o < pc)
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
