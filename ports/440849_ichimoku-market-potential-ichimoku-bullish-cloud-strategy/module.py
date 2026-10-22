"""Ichimoku crosses above the lead lines, 1-hour bars, long only: from flat, the conversion line (9) crossing over the base line (26) with the close above both lead lines goes long; the base line crossing
over the conversion line with the close below both lead lines closes.
Port of FMZ strategy #440849 "市场潜力量Ichimoku多头云策略Market-Potential-Ichimoku-Bullish-Cloud-Strategy" (Ichimoku Cloud Strategy (long only)).

FMZ source id: 440849

Source
    https://www.fmz.com/strategy/440849 (PineScript v4, FMZ last modified 2024-02-02 16:57:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 167-218), conversion 9, base 26, span B 52, delta 26 (plot offset only); custom dates on (testPeriod() is true)
    long_signal = crossover(conversion, base) and close > lead_a and close > lead_b;  short_signal = crossover(base, conversion) and close below both;  opentrades == 0 and long_signal -> entry LONG;  opentrades > 0 and short_signal -> close LONG

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lead lines are compared on the current bar (the displacement only shifts their plot), so the
      test uses past and current bars only. testPeriod() returns true, so the date block never closes
      anything. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku lines.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440849_ichimoku_cross_above_leads_long"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conversion": [9, 20],
    "base": [26, 60],
}
DEFAULT_PARAMS = {"conversion": 9, "base": 26, "lagging": 52}


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

    def avg(n):
        return (lo.rolling(n).min() + h.rolling(n).max()) / 2

    conv, base = avg(int(p["conversion"])), avg(int(p["base"]))
    la, lb = (conv + base) / 2, avg(int(p["lagging"]))
    up = (conv > base) & (conv.shift(1) <= base.shift(1)) & (c > la) & (c > lb)
    dn = (base > conv) & (base.shift(1) <= conv.shift(1)) & (c < la) & (c < lb)
    false = pd.Series(False, index=c.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
