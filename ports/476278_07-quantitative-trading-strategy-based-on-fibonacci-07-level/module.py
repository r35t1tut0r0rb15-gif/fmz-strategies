"""Close crossings of the 0.7 retracement of the 20-bar range, hourly bars: the cross up goes long, the cross down goes short, each with a 1.2 % stop and 1.8 % target from the entry price; reversing.
Port of FMZ strategy #476278 "基于斐波那契07水平的趋势突破量化交易策略-Quantitative-Trading-Strategy-Based-on-Fibonacci-07-Level-Trend-Breakthrough" (Fibonacci 0.7 Strategy - 60% Win Rate).

FMZ source id: 476278

Source
    https://www.fmz.com/strategy/476278 (PineScript v5, FMZ last modified 2024-12-27 15:51:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 81-133), Fibonacci lookback 20; stop 1.2 %, target 1.8 % of strategy.position_avg_price
    change(highest(high, 20)) -> high_level := highest;  change(lowest(low, 20)) -> low_level := lowest;  fib = high_level - 0.7 (high_level - low_level)
    close > fib and close[1] <= fib -> entry Buy;  close < fib and close[1] >= fib -> entry Sell;  in a position: exit(stop = avg x (1 -/+ 1.2 %), limit = avg x (1 +/- 1.8 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * high_level (low_level) is set whenever the 20-bar high (low) changes, so after its first change it
      always equals the current 20-bar high (low); before that it is na (as #476243). The cross test
      compares the previous close with the CURRENT level, as written. The bracket is sent from the
      position's average price while it is held: a scalar fraction of the entry fill, active from the
      fill (as #440797). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; avg-price bracket as fractions of the fill.
    2 generic: PASS, range-retracement crossings with a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored.
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

NAME = "fmz_476278_fib07_range_cross_pct_bracket_reversal"
FAMILY = "channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [20, 50],
    "tp_pct": [0.018, 0.036],
}
DEFAULT_PARAMS = {"lookback": 20, "tp_pct": 0.018, "sl_pct": 0.012}


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


def _set_on_change(x):
    """var level := x whenever ta.change(x) is non-zero: na until the first change, then x."""
    d = x.diff()
    started = ((d != 0) & d.notna()).cummax()
    return x.where(started)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["lookback"])
    hl = _set_on_change(h.rolling(n).max())
    ll = _set_on_change(lo.rolling(n).min())
    fib = hl - (hl - ll) * 0.7
    le = (c > fib) & (c.shift(1) <= fib)
    se = (c < fib) & (c.shift(1) >= fib)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
