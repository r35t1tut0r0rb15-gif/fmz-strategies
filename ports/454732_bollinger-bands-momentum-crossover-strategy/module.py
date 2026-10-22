"""Bollinger 20 / 2 band states, 1-hour bars: a close under the lower band goes long, a close over the upper band goes short; reversing.
Port of FMZ strategy #454732 "Bollinger Bands Momentum Crossover Strategy" (Bollinger Bands Strategy (band states with side flags)).

FMZ source id: 454732

Source
    https://www.fmz.com/strategy/454732 (PineScript v5, FMZ last modified 2024-06-21 14:12:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 150-194), Bollinger 20 / 2; in_long / in_short flags
    close < lower and not in_long -> entry Buy, in_long;  close > upper and not in_short -> entry Sell, in_short
    in_long and close > upper -> close Buy, not in_long;  in_short and close < lower -> close Sell, not in_short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flags only skip repeat entries on the held side. On a sell bar the short entry reverses the
      long first and the long's close then finds it reversed (one reversal), clearing its flag; the
      mirror on a buy bar. So every band state is a plain reversing entry. REVERSAL INTENDED. No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band states.
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

NAME = "fmz_454732_bollinger20_band_state_flag_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    false = pd.Series(False, index=bars_df.index)
    return c < basis - dev, false, c > basis + dev, false.copy()


def portfolio_kwargs(**params):
    return {}
