"""Bollinger 20 x 2 breakouts with a 2 % / 5 % bracket, 3-hour bars: the close crossing above the upper band goes long,
below the lower band goes short; each trade has a 2 % stop and a 5 % target from the entry price.
Port of FMZ strategy #488541 "动态布林带突破趋势追踪策略-Dynamic-Bollinger-Bands-Breakout-Trend-Tracking-Strategy" (Bollinger Bands Breakout Strategy).

FMZ source id: 488541

Source
    https://www.fmz.com/strategy/488541 (PineScript v6, FMZ last modified 2025-03-28 17:24:35).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 118-156), BB 20 x 2, TP 5 %, SL 2 %
    crossover(close, upper) -> entry long;  crossunder(close, lower) -> entry short
    every bar: exit(limit = avg price x (1 +- 5 %), stop = avg price x (1 -+ 2 %)) per side

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is relative to the position's average price (the fill), fixed for the trade: sl_stop 2 %, tp_stop
      5 % of the fill (scalars, exact).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "3h" from the backtest
      header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the fill.
    2 generic: PASS, bands and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_488541_bb_breakout_pct_bracket"
FAMILY = "bollinger_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "mult": [2.0, 1.5],
    "sl_pct": [2.0, 4.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "tp_pct": 5.0, "sl_pct": 2.0}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = p["mult"] * c.rolling(n).std(ddof=0)
    up, lo = basis + dev, basis - dev
    long_e = ((c > up) & (c.shift(1) <= up.shift(1))).astype(bool)
    short_e = ((c < lo) & (c.shift(1) >= lo.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
