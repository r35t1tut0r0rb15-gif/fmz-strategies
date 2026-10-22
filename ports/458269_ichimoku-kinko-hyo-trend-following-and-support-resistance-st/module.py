"""Close against the Ichimoku Span B (the 52-bar mid line), 1-hour bars: a close over it holds long, a close under it holds short; reversing.
Port of FMZ strategy #458269 "Ichimoku Kinko Hyo Trend Following and Support Resistance Strategy" (Ichimoku-based Strategy).

FMZ source id: 458269

Source
    https://www.fmz.com/strategy/458269 (PineScript v5, FMZ last modified 2024-07-31 14:25:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 168-204), mid line (lowest low + highest high) / 2 over 52 bars, undisplaced; conversion / base lines unused
    close > leadLine2 -> entry Buy;  close < leadLine2 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Span B is used undisplaced, as written. The tests are states: repeated entries while held do
      nothing. There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close vs the 52-bar mid line.
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

NAME = "fmz_458269_close_vs_span_b_mid52_state_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "span_b": [52, 26],
}
DEFAULT_PARAMS = {"span_b": 52}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["span_b"])
    sb = (lo.rolling(n).min() + h.rolling(n).max()) / 2
    false = pd.Series(False, index=bars_df.index)
    return c > sb, false, c < sb, false.copy()


def portfolio_kwargs(**params):
    return {}
