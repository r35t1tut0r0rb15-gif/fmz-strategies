"""Closes far from the two-bar mid price, 4-hour bars: a close more than k x gamma x sigma^2 x T + M under the mid of this and the previous close goes long, the same distance above goes short; reversing.
Port of FMZ strategy #449942 "Khaled Tamims Avellaneda Stoikov Strategy Khaled Tamims Avellaneda Stoikov Strategy" (Khaled Tamim's Avellaneda-Stoikov Strategy).

FMZ source id: 449942

Source
    https://www.fmz.com/strategy/449942 (PineScript v5, FMZ last modified 2024-04-30 15:54:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-147), gamma 2, sigma 8, T 0.0833, k 5, M 0.5 (price units); fee 0
    mid = (close + close[1]) / 2;  bid = mid - k gamma sigma^2 T;  ask = mid + k gamma sigma^2 T;  close < bid - M -> entry Buy;  close > ask + M -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the band half-width k gamma sigma^2 T + M = 53.82 price units is a fraction of the
      price, 0.00128 against BTC near 42000, applied to the mid price. The condition is a one-bar move of
      more than twice that width. No exit: positions end at the opposite entry. REVERSAL INTENDED. No
      sizing code. FREQ = "4h" from the backtest header (UTC-aligned 4-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, one-bar moves beyond a fixed band around the mid price.
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

NAME = "fmz_449942_avellaneda_stoikov_mid_band_reversion_reversal"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "band_frac": [0.00128, 0.005],
}
DEFAULT_PARAMS = {"band_frac": 0.00128}


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
    mid = (c + c.shift(1)) / 2
    w = mid * float(p["band_frac"])                 # the script adds a fee of 0
    le = c < mid - w
    se = c > mid + w
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
