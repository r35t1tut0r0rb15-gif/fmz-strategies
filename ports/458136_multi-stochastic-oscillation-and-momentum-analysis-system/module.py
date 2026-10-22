"""Eight smoothed hlc3 stochastics stacked in order, 1-hour bars: all eight in rising order (the slowest also rising) goes long, all in falling order goes short; reversing.
Port of FMZ strategy #458136 "Multi Stochastic Oscillation and Momentum Analysis System" (Stochaholic Strategy).

FMZ source id: 458136

Source
    https://www.fmz.com/strategy/458136 (PineScript v5, FMZ last modified 2024-07-30 11:04:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-195), stochastic 14 of hlc3 against high / low; k1-k8 = EMA 3 of SMA 3..10 of it
    k1 >= k2 >= ... >= k8 and k8 >= k8[1] -> entry Buy;  k1 < k2 < ... < k8 and k8 < k8[1] -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.stoch(hlc3, high, low, 14) = 100 x (hlc3 - lowest low) / (highest high - lowest low). The
      stacking tests are states: repeated entries while held do nothing. There is no exit: positions
      end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stacked smoothed stochastics.
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

NAME = "fmz_458136_stacked_smoothed_stochastics_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
}
DEFAULT_PARAMS = {"length": 14}


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
    n = int(p["length"])
    src = (h + lo + c) / 3
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    st = 100 * (src - ll) / (hh - ll)
    ks = [st.rolling(w).mean().ewm(span=3, adjust=False).mean() for w in range(3, 11)]
    up = ks[7] >= ks[7].shift(1)
    dn = ks[7] < ks[7].shift(1)
    for a, b in zip(ks[:-1], ks[1:]):
        up = up & (a >= b)
        dn = dn & (a < b)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
