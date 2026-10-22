"""Williams-style fractals, 1-hour bars: a confirmed bullish fractal (the bar two back is the highest of five and over both neighbours) goes long, otherwise a confirmed bearish fractal (the mirror on lows) goes short; reversing.
Port of FMZ strategy #455357 "Dynamic Reversal Point Strategy Based on Bollinger Bands and Fractal Breakouts" (Breakdown and Breakup Strategy (fractal entries)).

FMZ source id: 455357

Source
    https://www.fmz.com/strategy/455357 (PineScript v5, FMZ last modified 2024-06-28 15:06:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 175-254), fractal: highest(high, 5)[2] == high[2] and high[2] > high[1] and high[2] > high[3] (mirror on lows); Bollinger 20 / 2 only for the plotted signals
    bullish fractal -> entry Enter Long;  else bearish fractal -> entry Enter Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The fractal tests use the bars up to the current one (the fractal bar is two back and its right
      neighbour is checked only one bar to the right, as written). The Bollinger breakdown / breakup
      flags only drive the plotted icons. The bullish test wins a bar with both. There is no exit:
      positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, fractal entries.
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

NAME = "fmz_455357_fractal_entries_reversal"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "window": [5, 7],
}
DEFAULT_PARAMS = {"window": 5}


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
    w = int(p["window"])
    h1, h2, h3 = h.shift(1), h.shift(2), h.shift(3)
    l1, l2, l3 = lo.shift(1), lo.shift(2), lo.shift(3)
    bull = (h.rolling(w).max().shift(2) == h2) & (h2 > h1) & (h2 > h3)
    bear = (lo.rolling(w).min().shift(2) == l2) & (l2 < l1) & (l2 < l3)
    false = pd.Series(False, index=bars_df.index)
    return bull, false, bear & ~bull, false.copy()


def portfolio_kwargs(**params):
    return {}
