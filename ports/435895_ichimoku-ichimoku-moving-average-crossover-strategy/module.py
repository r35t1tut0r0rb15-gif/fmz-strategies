"""Kijun line side with candle filters, 1-hour bars: a bar entirely over the Kijun that is a red candle with a body over a third of the average body
goes long; a bar entirely under it that is a green candle with that body goes short (reversing).
Port of FMZ strategy #435895 "Ichimoku均线交叉策略Ichimoku-Moving-Average-Crossover-Strategy" (Noro's Ichimoku Strategy v1.0).

FMZ source id: 435895

Source
    https://www.fmz.com/strategy/435895 (PineScript v3, FMZ last modified 2023-12-19 15:40:53).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 106-163), conversion 9, base 26, lagging span 52; body filter and colour filter on
    baseLine = donchian(26);  body = |close - open| > sma(|close - open|, 10) / 3;  up = low > baseLine and (close < open) and body -> entry long;  dn = high < baseLine and (close > open) and body -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The colour filter requires a candle AGAINST the entry (a red bar for the long, a green bar for
      the short), as written: a pullback entry on the trend side of the Kijun. The conditions are
      states re-sent every bar; vbt ignores a same-side signal. The date window is the default
      1900-2100. strategy.entry reverses: REVERSAL INTENDED. The full-equity size is sizing. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel midpoint and candle filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_435895_kijun_side_pullback_candle"
FAMILY = "ichimoku"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "base": [26, 52],
    "use_body_filter": [True, False],
}
DEFAULT_PARAMS = {"base": 26, "use_body_filter": True}


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
    n = int(p["base"])
    base_line = (lo.rolling(n).min() + h.rolling(n).max()) / 2
    nbody = (c - o).abs()
    body = (nbody > nbody.rolling(10).mean() / 3) | (not p["use_body_filter"])
    up = ((lo > base_line) & (c < o) & body).fillna(False).astype(bool)
    dn = ((h < base_line) & (c > o) & body).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
