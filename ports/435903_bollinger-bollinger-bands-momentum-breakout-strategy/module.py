"""Bollinger basis crossings, 1-hour bars: the close crossing over the SMA 20 goes long, under it goes short (reversing). The band-based
closes sit inside the same-bar entry blocks and never fire (as written).
Port of FMZ strategy #435903 "Bollinger带动量突破策略Bollinger-Bands-Momentum-Breakout-Strategy" (NoScoobies Bollinger Bands).

FMZ source id: 435903

Source
    https://www.fmz.com/strategy/435903 (PineScript v4, FMZ last modified 2023-12-19 16:24:24).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 114-135), Bollinger 20 / 1.5 sd
    long = crossover(close, basis);  short = crossunder(close, basis);  close_long = crossunder(close, upper);  close_short = crossover(close, lower)
    if long: entry long, close long when close_long;  if short: entry short, close short when close_short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes are called only on the bar of the matching entry, where the band cross cannot
      hold (a close crossing over the basis is not crossing under the upper band), so the strategy is a
      basis-cross reversal. The deviation input only feeds those dead closes (it is not searched).
      strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average cross.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435903_bollinger_basis_cross"
FAMILY = "bollinger_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 30, 40],
}
DEFAULT_PARAMS = {"length": 20}


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
    basis = c.rolling(int(p["length"])).mean()
    le = ((c > basis) & (c.shift(1) <= basis.shift(1))).fillna(False).astype(bool)
    se = ((c < basis) & (c.shift(1) >= basis.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
