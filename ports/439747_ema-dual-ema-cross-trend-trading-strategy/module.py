"""EMA 30 reclaims in an EMA 30 / 60 uptrend, long only, 1-hour bars: the close crossing back over the EMA 30 from between the two EMAs, with the EMA 30 above the EMA 60, goes long with a stop at the EMA 60
and a target at the 10-bar high of the signal bar.
Port of FMZ strategy #439747 "基于EMA指标的双线交叉趋势交易策略Dual-EMA-Cross-Trend-Trading-Strategy" (EMA Cross Strategy).

FMZ source id: 439747

Source
    https://www.fmz.com/strategy/439747 (PineScript v5, FMZ last modified 2024-01-23 14:43:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 135-165), EMA 30 / 60
    buy = crossover(close, ema30) and close[1] < ema30[1] and close[1] > ema60[1] and close > ema30 > ema60 -> entry Long, exit(stop = ema60, limit = highest(high, 10))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is sent on the signal bar with that bar's EMA 60 and 10-bar high and stays in force:
      sl_stop = (close - EMA 60) / close and tp_stop = (10-bar high - close) / close of the signal bar,
      shifted one bar inside stops() and re-based on the fill (a level not beyond the close places no
      order). A new signal while long would move the levels; the port keeps the first. Long only. Stop
      module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, EMA crossings and levels from the signal bar.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439747_ema30_reclaim_ema60_stop_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema30_length": [30, 20],
    "ema60_length": [60, 100],
}
DEFAULT_PARAMS = {"ema30_length": 30, "ema60_length": 60, "tp_len": 10}


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


def _setup(bars_df, p):
    c = bars_df["close"]
    a = c.ewm(span=int(p["ema30_length"]), adjust=False).mean()
    b = c.ewm(span=int(p["ema60_length"]), adjust=False).mean()
    buy = (c > a) & (c.shift(1) <= a.shift(1)) & (c.shift(1) < a.shift(1)) & (c.shift(1) > b.shift(1)) & (a > b)
    sl = ((c - b) / c).where(buy)
    tp = ((bars_df["high"].rolling(int(p["tp_len"])).max() - c) / c).where(buy)
    return buy, sl.where(sl > 0), tp.where(tp > 0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, _, _ = _setup(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, sl, tp = _setup(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
