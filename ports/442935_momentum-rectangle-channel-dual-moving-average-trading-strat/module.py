"""Close against a TEMA 5, 4-hour bars: the close above the TEMA holds long, below holds short; reversing.
Port of FMZ strategy #442935 "Momentum Rectangle Channel Dual Moving Average Trading Strategy" (TEMA_System_SAR).

FMZ source id: 442935

Source
    https://www.fmz.com/strategy/442935 (PineScript v2, FMZ last modified 2024-02-27 14:54:07).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 146-194), fast TEMA 5; slow TEMA 50 (plot only); dates (window true)
    fastTEMA = 3 (ema1 - ema2) + ema3 of close, length 5;  close > fastTEMA -> entry long;  close < fastTEMA -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The slow TEMA only plots (and is built from the fast EMAs, as written). The entries are level
      tests, refused while held. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "4h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close vs TEMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442935_close_vs_tema5_reversal"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_period": [5, 10],
}
DEFAULT_PARAMS = {"fast_period": 5}


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
    n = int(p["fast_period"])
    e1 = c.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    e3 = e2.ewm(span=n, adjust=False).mean()
    tema = 3 * (e1 - e2) + e3
    false = pd.Series(False, index=c.index)
    return c > tema, false, c < tema, false.copy()


def portfolio_kwargs(**params):
    return {}
