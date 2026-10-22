"""Three growing candles of one colour with a wide range on the EMA 50 side, 2-hour bars: three rising green candles (the last body larger than the middle one, the first larger too) above the EMA with a range over 1.5 x its EMA 50 go long, the red mirror below goes short; reversing.
Port of FMZ strategy #478707 "Multi EMA Trend Following Strategy with Dynamic Volatility Filter" (Scalp Slayer (I)).

FMZ source id: 478707

Source
    https://www.fmz.com/strategy/478707 (PineScript v5, FMZ last modified 2025-01-17 15:00:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 79-201), filter 1.5 x EMA 50 of the range; trend EMA 50; lookback 20 (labels only); scalp mode
    buy = close > ema50 and 3 green candles with |body[2]| > |body[1]| < |body| and rising closes and range > 1.5 ema(range, 50) -> entry Enter Long;  else sell (red mirror) -> entry Enter Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The tracked entry prices, targets and stops only draw labels and alerts; no exit order is sent, so
      positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "2h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, three-candle momentum patterns with a range and trend filter.
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

NAME = "fmz_478707_three_candle_growth_range_filter_ema50_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "filter_number": [1.5, 1.0],
    "ema_trend": [50, 100],
}
DEFAULT_PARAMS = {"filter_number": 1.5, "ema_trend": 50}


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
    rng = h - lo
    wide = rng > float(p["filter_number"]) * rng.ewm(span=50, adjust=False).mean()
    trend = c.ewm(span=int(p["ema_trend"]), adjust=False).mean()
    b = (c - o).abs()
    sizes = (b.shift(2) > b.shift(1)) & (b > b.shift(1))
    g = c > o
    r = c < o
    le = (c > trend) & g.shift(2, fill_value=False) & g.shift(1, fill_value=False) & g & sizes \
        & (c > c.shift(1)) & (c.shift(1) > c.shift(2)) & wide
    se = (c < trend) & r.shift(2, fill_value=False) & r.shift(1, fill_value=False) & r & sizes \
        & (c < c.shift(1)) & (c.shift(1) < c.shift(2)) & wide
    false = pd.Series(False, index=c.index)
    return le, false, se & ~le, false.copy()


def portfolio_kwargs(**params):
    return {}
