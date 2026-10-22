"""Close against the mid-line of the previous 20-bar closing channel, 4-hour bars: the close above the mid-line holds long, below holds short; reversing (the channel-low and mid-line closes repeat the
reversals). Same rules as #442842 (near-duplicate group, rule 7).
Port of FMZ strategy #443123 "Trend Following Moving Average Strategy" (dc (stock version)).

FMZ source id: 443123

Source
    https://www.fmz.com/strategy/443123 (PineScript v3, FMZ last modified 2024-02-29 14:00:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 107-152), period 20 (constant); 20 % of equity, commission 0.005 per contract; dates (testPeriod true)
    dcUpper = highest(close, 20)[1];  dcLower = lowest(close, 20)[1];  dcAverage = mid;  close > dcAverage -> entry simpleBuy;  close < dcLower -> close simpleBuy
    close < dcAverage -> entry simpleSell;  close > dcAverage -> close simpleSell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The rules are those of #442842 (the period is a constant here and the sizing differs). A close
      under the channel low is also under the mid-line, and the short's close condition is the long
      entry's condition, so both closes only repeat the reversals. The entries are level tests, refused
      while held. strategy.entry reverses: REVERSAL INTENDED. The 20 % of equity size and the
      per-contract commission are sizing and costs. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close vs channel mid-line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and per-contract commission stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: ND427308 (3 members, best partner #427308, Jaccard 0.790); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443123_close_vs_prior_channel_mid_reversal_stock"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [20, 50],
}
DEFAULT_PARAMS = {"period": 20}


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
    n = int(p["period"])
    avg = (c.rolling(n).max().shift(1) + c.rolling(n).min().shift(1)) / 2
    le = c > avg
    se = c < avg
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
