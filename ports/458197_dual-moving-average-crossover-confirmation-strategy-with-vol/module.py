"""Close crossings of the SMA 20 on the bar that also crosses the SMA 50, 2-hour bars: the close crossing over the SMA 20 while moving from at or under to over the SMA 50 goes long, the mirror goes short; reversing.
Port of FMZ strategy #458197 "Dual Moving Average Crossover Confirmation Strategy with Volume Price Integration Optimization Model" (Customizable SMA Crossover Strategy with Confirmation).

FMZ source id: 458197

Source
    https://www.fmz.com/strategy/458197 (PineScript v5, FMZ last modified 2024-07-30 17:12:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 164-215), SMA 20 / 50 (choices); the "confirmed" conditions are computed but not traded
    crossover(close, sma20) and close > sma50 and close[1] <= sma50 -> entry Buy;  crossunder(close, sma20) and close < sma50 and close[1] >= sma50 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The orders use buySignal / sellSignal; the confirmation conditions are never used (and can never
      hold together with the signals). There is no exit: positions end at the opposite entry. REVERSAL
      INTENDED. No sizing code. FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, double SMA crossings on one bar.
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

NAME = "fmz_458197_close_cross_sma20_and_sma50_same_bar_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [20, 10],
    "long_len": [50, 100],
}
DEFAULT_PARAMS = {"short_len": 20, "long_len": 50}


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
    s, l = c.rolling(int(p["short_len"])).mean(), c.rolling(int(p["long_len"])).mean()
    le = (c > s) & (c.shift(1) <= s.shift(1)) & (c > l) & (c.shift(1) <= l)
    se = (c < s) & (c.shift(1) >= s.shift(1)) & (c < l) & (c.shift(1) >= l)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
