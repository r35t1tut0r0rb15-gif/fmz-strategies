"""EMA 12 crossings of four slower EMAs, 30-minute bars: the EMA 12 having crossed over the EMA 26, 50, 100 or 200 on the previous bar and still above it goes long; the mirror goes short; reversing.
Port of FMZ strategy #437665 "多重EMA均线交叉趋势跟踪策略Multi-EMA-Crossover-Trend-Following-Strategy" (EMA Trades).

FMZ source id: 437665

Source
    https://www.fmz.com/strategy/437665 (PineScript v2, FMZ last modified 2024-01-04 16:22:07).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 106-172), EMA 12 against 26 / 50 / 100 / 200 (89 and 144 unused); pyramiding 4
    longN = crossover(ema12[1], emaN[1]) and ema12 > emaN -> entry BuyN, exit(SellN) without levels;  shortN = crossunder(ema12[1], emaN[1]) and ema12 < emaN -> entry SellN, exit(BuyN)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit calls name ids and give no stop, limit or trail, so they place no order. The four ids per
      side are adds that pyramiding 4 allows (sizing): the port holds one position, long when any long
      setup fires and short when any short setup fires (the short calls come last, so a bar with both ends
      short). REVERSAL INTENDED. No sizing code beyond pyramiding. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 4 stored.
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

NAME = "fmz_437665_ema12_multi_cross"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "shortest": [12, 8],
    "shorter": [26, 20],
}
DEFAULT_PARAMS = {"shortest": 12, "shorter": 26, "short": 50, "middle": 100, "long": 200}


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
    f = c.ewm(span=int(p["shortest"]), adjust=False).mean()
    lc = pd.Series(False, index=c.index)
    sc = pd.Series(False, index=c.index)
    for k in ("shorter", "short", "middle", "long"):
        e = c.ewm(span=int(p[k]), adjust=False).mean()
        f1, e1 = f.shift(1), e.shift(1)
        lc = lc | ((f1 > e1) & (f1.shift(1) <= e1.shift(1)) & (f > e))
        sc = sc | ((f1 < e1) & (f1.shift(1) >= e1.shift(1)) & (f < e))
    false = pd.Series(False, index=bars_df.index)
    return lc & ~sc, false, sc, false.copy()


def portfolio_kwargs(**params):
    return {}
