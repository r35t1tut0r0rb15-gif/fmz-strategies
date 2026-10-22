"""Ichimoku leading spans on log prices, 1-hour bars: span A (the mean of the 9 and 26 log Donchian mid-lines) crossing over span B (the 52 log mid-line) goes long, under goes short; reversing.
Port of FMZ strategy #442507 "Log Ichimoku Cross Variety Strategy" (Log Ichimoku Strategy).

FMZ source id: 442507

Source
    https://www.fmz.com/strategy/442507 (PineScript v3, FMZ last modified 2024-02-22 13:53:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 123-160), conversion 9, base 26, span B 52, displacement 26 (plots only)
    loglows = log(drop1st(low));  loghighs = log(drop1st(high));  donchian(n) = avg(lowest(loglows, n), highest(loghighs, n))
    leadLine1 = avg(donchian(9), donchian(26));  leadLine2 = donchian(52);  crossover -> entry Ichi-LE;  crossunder -> entry Ichi-SE (oca "Ichi")

Interpretation choices (Pine rules in SURVEY_README.md)
    * The spans are compared undisplaced, as written (the displacement only shifts the plots). drop1st
      blanks the first bar. The oca group does not act on market entries. strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, log-price span crossings.
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

NAME = "fmz_442507_log_ichimoku_span_cross_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conversion": [9, 20],
    "span_b": [52, 120],
}
DEFAULT_PARAMS = {"conversion": 9, "span_b": 52, "base": 26}


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
    h, lo = bars_df["high"], bars_df["low"]
    ll = np.log(lo.where(lo.shift(1).notna()))
    lh = np.log(h.where(h.shift(1).notna()))

    def don(n):
        return (ll.rolling(n).min() + lh.rolling(n).max()) / 2

    a = (don(int(p["conversion"])) + don(int(p["base"]))) / 2
    b = don(int(p["span_b"]))
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=h.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
