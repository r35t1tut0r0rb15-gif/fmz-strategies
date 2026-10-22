"""One-bar Awesome Oscillator divergences filtered by the stochastic, 4-hour bars: a higher close with a falling AO while %K and %D are both under 20 goes long, a lower close with a rising AO while both are
over 80 goes short; reversing.
Port of FMZ strategy #442946 "Awesome Oscillator Double Stochastic Filtered Divergence Trading Strategy" (Fixed AO Divergence Strategy (Fixed AO+Stoch)).

FMZ source id: 442946

Source
    https://www.fmz.com/strategy/442946 (PineScript v5, FMZ last modified 2024-02-27 15:51:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 165-203), AO 5 / 34 of hl2; stochastic 14, D 3; levels 80 / 20
    bull = close > close[1] and ao < ao[1] and K < 20 and D < 20 -> entry Long;  bear = close < close[1] and ao > ao[1] and K > 80 and D > 80 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, AO divergence with a stochastic filter.
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

NAME = "fmz_442946_ao_one_bar_divergence_stoch_filter_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stoch_len": [14, 9],
    "oversold": [20, 30],
}
DEFAULT_PARAMS = {"stoch_len": 14, "oversold": 20, "d_len": 3}


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
    hl2 = (h + lo) / 2
    ao = hl2.rolling(5).mean() - hl2.rolling(34).mean()
    n = int(p["stoch_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    d = k.rolling(int(p["d_len"])).mean()
    os_ = float(p["oversold"])
    le = (c > c.shift(1)) & (ao < ao.shift(1)) & (k < os_) & (d < os_)
    se = (c < c.shift(1)) & (ao > ao.shift(1)) & (k > 100.0 - os_) & (d > 100.0 - os_)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
