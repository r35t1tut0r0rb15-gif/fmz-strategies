"""Two-candle reversal patterns, 1-hour bars: a green bar closing over the high of a red bar with a long lower half goes long with a stop at that bar's low and a 1.5R target; the mirror goes short with a stop at its high; entries only when not already on that side; reversing.
Port of FMZ strategy #451401 "漢越-基於多EMAATR和RSI的趨勢順勢交易策略-Han-Yue-Trend-Following-Trading-Strategy-Based-on-Multiple-EMAs-ATR-and-RSI" (Win ha (Han Yue trend following, engulf-through candles)).

FMZ source id: 451401

Source
    https://www.fmz.com/strategy/451401 (PineScript v4, FMZ last modified 2024-05-14 16:37:52).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-224), stop low[1] / high[1] of the signal bar; target 1.5 x the risk; risk 0.5 % of the capital per trade
    mua = open[1] > close[1] and close[1] - low[1] > high[1] - close[1] and close > open and close > high[1]
    ban = close[1] > open[1] and high[1] - close[1] > close[1] - low[1] and open > close and close < low[1]
    mua and position <= 0 -> entry Long, exit(stop = low[1], limit = close + 1.5 x (close - low[1]))
    ban and position >= 0 -> entry Short, exit(stop = high[1], limit = close - 1.5 x (high[1] - close))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop and target are price levels fixed on the signal bar (fixnan keeps them until the next
      accepted signal), so the port states them as fractions of the signal close: the stop distance
      (close - low[1]) / close for a long, (high[1] - close) / close for a short, the target 1.5 times
      it; read at the fill bar from the signal bar (known at the fill's open). A repeat signal on the
      held side is refused by the source's position test and changes nothing. The two patterns cannot
      occur on one bar (green against red). An opposite pattern reverses. The 'Khung thoi gian' session
      only colours the background. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      The quantity is risk sizing (stored). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the signal-bar levels as fractions of the signal close.
    2 generic: PASS, two-candle reversal patterns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based quantity stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the session input only colours the background).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451401_two_candle_reversal_prior_extreme_stop_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [1.5, 2.0],
}
DEFAULT_PARAMS = {"rr": 1.5}


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


def _patterns(bars_df):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    o1, h1, l1, c1 = o.shift(1), h.shift(1), lo.shift(1), c.shift(1)
    mua = (o1 > c1) & ((c1 - l1) > (h1 - c1)) & (c > o) & (c > h1)
    ban = (c1 > o1) & ((h1 - c1) > (c1 - l1)) & (o > c) & (c < l1)
    return mua, ban


def simulate(bars_df, **params):
    mua, ban = _patterns(bars_df)
    false = pd.Series(False, index=bars_df.index)
    return mua, false, ban, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    mua, ban = _patterns(bars_df)
    dist = pd.Series(np.nan, index=bars_df.index)
    dist = dist.mask(mua, (c - lo.shift(1)) / c).mask(ban, (h.shift(1) - c) / c)
    sl = dist.shift(1)                       # the signal bar's levels, read at the fill bar
    return {"sl_stop": sl, "tp_stop": sl * float(p["rr"])}


def portfolio_kwargs(**params):
    return {}
