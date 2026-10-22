"""Range-extreme bars, 15-minute bars: when the previous high is at (or within 0.01 % of) the highest high of the last 51 bars and the bar is red, the script goes LONG; when the previous low is at the lowest low and
the bar is green, it goes SHORT (names swapped as written); reversing.
Port of FMZ strategy #439233 "Quant Trading Support and Resistance Cloud Indicator" ([IND] rang3r).

FMZ source id: 439233

Source
    https://www.fmz.com/strategy/439233 (PineScript v3, FMZ last modified 2024-01-18 15:30:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 145-195), entry period 50 (bars 1 to 51), exit period 25 (unused), sensitivity 0.9999
    periodHigh = max(high[1] .. high[51]);  periodLow = min(low[1] .. low[51])
    s = high[1] > periodHigh * 0.9999 and open > close;  l = low[1] < periodLow / 0.9999 and close > open;  entry long when s;  entry short when l

Interpretation choices (Pine rules in SURVEY_README.md)
    * The loops run i = 1 to entP + 1, so the window is the 51 bars before the current one. As written,
      the "s" setup (a red bar after a range high) opens the LONG and the "l" setup the SHORT; the
      intended version (the names suggest the opposite) is owed. The two setups cannot share a bar (bar
      colours). The exit period and the cloud lines feed nothing. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, range highs and lows with a ratio.
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

NAME = "fmz_439233_rang3r_range_extreme_as_written"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "entry_period": [50, 25],
    "sensitivity": [0.9999, 0.999],
}
DEFAULT_PARAMS = {"entry_period": 50, "sensitivity": 0.9999}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["entry_period"]) + 1
    sens = float(p["sensitivity"])
    ph = h.shift(1).rolling(n).max()
    pl = lo.shift(1).rolling(n).min()
    s = (h.shift(1) > ph * sens) & (o > c)
    l_ = (lo.shift(1) < pl * (1 / sens)) & (c > o)
    false = pd.Series(False, index=c.index)
    return s, false, l_, false.copy()


def portfolio_kwargs(**params):
    return {}
