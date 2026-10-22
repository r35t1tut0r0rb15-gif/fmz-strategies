"""EMA 14 candle breaks, hourly bars: a green candle crossing over the EMA 14 with at least half its body above it and wicks at most 40 % of its range goes long; a red candle closing under the EMA after a bar whose low was above it goes short; reversing.
Port of FMZ strategy #475606 "EMA均线动态突破与反转策略-Dynamic-EMA-Breakthrough-and-Reversal-Strategy" (Buy and Sell Signals with EMA).

FMZ source id: 475606

Source
    https://www.fmz.com/strategy/475606 (PineScript v6, FMZ last modified 2024-12-20 15:00:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 122-181), EMA 14; body >= 50 % over the EMA; wicks <= 40 %; lower-wick test <= 20 %
    green and crossover(close, ema14) and (close - open) x 0.5 <= close - ema14 and wicks / range <= 0.4 -> entry Buy;  close < ema14 and red and low[1] > ema14[1] and (low - min(open, close)) / range <= 0.2 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The sell's wick test (low - min(open, close)) / range is never positive, so it always holds, as
      written. There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA candle breaks.
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

NAME = "fmz_475606_ema14_candle_break_body_wick_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [14, 21],
}
DEFAULT_PARAMS = {"ema_length": 14}


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
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    e14 = c.ewm(span=14, adjust=False).mean()                # the sell side uses the fixed 14 EMA
    rng = h - lo
    wick = ((h - c) + (o - lo)) / rng
    le = (c > o) & (c > e) & (c.shift(1) <= e.shift(1)) & ((c - o) * 0.5 <= c - e) & (wick <= 0.4)
    se = (c < e14) & (c < o) & (lo.shift(1) > e14.shift(1)) & ((lo - np.minimum(o, c)) / rng <= 0.2)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
