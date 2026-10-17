"""Ichimoku kumo twists, 3-minute bars: lead line 1 (preset 20 / 60) crossing above lead line 2 (120) goes long, crossing
below goes short; always in after the first twist.
Port of FMZ strategy #433574 "Ichimoku Kumo Twist Gold Absorbing Strategy" (Ichimoku Kumo Twist Strategy (Presets)).

FMZ source id: 433574

Source
    https://www.fmz.com/strategy/433574 (PineScript v3, FMZ last modified 2023-11-28 16:12:09).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 125-238), preset "Cpt 20 60 120 30"; linear scaling; drop first 1 candle
    lead1 = avg(donchian(20), donchian(60));  lead2 = donchian(120)  (current bar; the displacement only shifts the plot)
    crossover(lead1, lead2) -> entry long;  crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Donchian helpers use the bars available while the history is shorter than the window
      (xlowest / xhighest), as written; the first candle is dropped. Log scaling is off.
    * strategy.entry reverses: REVERSAL INTENDED. The date window is open from 2017. FREQ = "3min" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku line crosses.
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

NAME = "fmz_433574_kumo_twist"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "preset": ["Cpt 20 60 120 30", "Std 9 26 52 26"],
}
DEFAULT_PARAMS = {"preset": "Cpt 20 60 120 30"}
PRESETS = {"Cpt 20 60 120 30": (20, 60, 120), "Cpt 10 30 60 30": (10, 30, 60), "Std 18 52 104 26": (18, 52, 104),
           "Std 9 26 52 26": (9, 26, 52)}


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
    cn, bn, sn = PRESETS[str(p["preset"])]
    lows = bars_df["low"].copy()
    highs = bars_df["high"].copy()
    lows.iloc[:1] = np.nan                     # dropn(low, 1): the first candle is dropped
    highs.iloc[:1] = np.nan

    def don(n):
        return (lows.rolling(n, min_periods=1).min() + highs.rolling(n, min_periods=1).max()) / 2

    l1 = (don(cn) + don(bn)) / 2
    l2 = don(sn)
    le = ((l1 > l2) & (l1.shift(1) <= l2.shift(1))).astype(bool)
    se = ((l1 < l2) & (l1.shift(1) >= l2.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
