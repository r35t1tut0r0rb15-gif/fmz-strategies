"""Lower Bollinger band entries, no bar size of its own, long only: a close under the lower band (20, 2 sd) goes long; the script has no
exit, so the long is held (the StochRSI lines are computed and not used).
Port of FMZ strategy #435698 "基于布林带和-StochRSI-指标的高频交易策略High-Frequency-Trading-Strategy-Based-on-Bollinger-Bands-and-StochRSI-Indicators" (High Frequency Strategy).

FMZ source id: 435698

Source
    https://www.fmz.com/strategy/435698 (PineScript v5, FMZ last modified 2023-12-18 10:16:49).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 140-165), Bollinger 20 / 2 sd; StochRSI 14 / 3 / 3 computed only to plot
    buy_condition = close < sma(close, 20) - 2 stdev(close, 20);  buy_condition -> entry long ("Buy")

Interpretation choices (Pine rules in SURVEY_README.md)
    * No exit exists in the script (no close, no exit order): the long stays open until the end, as
      written (the intended version with an exit is owed). The StochRSI K and D are only plotted. The
      source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1).
      precompute builds the bars with the house bar_sizes.build_bars(raw_1m_df, params["bar_size"]); the
      driver supplies bar_size (never in GRID / DEFAULT_PARAMS). Long only.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger band.
    3 crypto-exchange-only: no.
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_435698_lower_bollinger_long_hold"
FAMILY = "bollinger_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "bar_size_pending"
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "dev": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "dev": 2.0}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    lower = c.rolling(n).mean() - float(p["dev"]) * c.rolling(n).std(ddof=0)
    le = (c < lower).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
