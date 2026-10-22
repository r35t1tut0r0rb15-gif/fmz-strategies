"""Bollinger 20 / 2 band closes, bar size from the search: a close under the lower band goes long, a close over the upper band goes short; reversing.
Port of FMZ strategy #458192 "Bollinger Bands Breakout Quantitative Trading Strategy" (Bollinger Bands Breakout Strategy).

FMZ source id: 458192

Source
    https://www.fmz.com/strategy/458192 (PineScript v5, FMZ last modified 2024-07-30 16:55:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 165-198), BB 20, 2 sd (population)
    close < lower -> entry Buy;  close > upper -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1);
      precompute builds the bars with the house bar_sizes.build_bars with the driver's bar_size. Despite
      the name the entries fade the bands. The tests are states: repeated entries while held do
      nothing. There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band fades.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_458192_bb20_band_close_fade_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # no backtest header: the driver supplies bar_size
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n, k = int(p["length"]), float(p["mult"])
    basis = c.rolling(n).mean()
    dev = k * c.rolling(n).std(ddof=0)
    false = pd.Series(False, index=bars_df.index)
    return c < basis - dev, false, c > basis + dev, false.copy()


def portfolio_kwargs(**params):
    return {}
