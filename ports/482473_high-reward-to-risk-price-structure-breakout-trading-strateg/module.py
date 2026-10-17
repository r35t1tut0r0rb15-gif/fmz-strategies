"""Closes crossing the prior 20-bar high (low) go long (short) with the stop at the 10-bar extreme and a 5 R target,
three-hour bars.
Port of FMZ strategy #482473 "基于价格结构的高比例回报突破交易策略-High-Reward-to-Risk-Price-Structure-Breakout-Trading-Strategy" (Filtered Price Action Breakout).

FMZ source id: 482473

Source
    https://www.fmz.com/strategy/482473 (PineScript v6, FMZ last modified 2025-02-18 15:42:01).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 120-181), look-back 20, stop look-back 10, RR 5, max 5 trades a day
    crossover(close, highest(high, 20)[1]) and risk = close - lowest(low, 10) > 0 -> entry long with
    exit(stop = lowest(low, 10), limit = close + 5 risk); short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * tradeCount is not a var: it is 0 or 1 on every bar, so the 5-a-day cap never binds (dropped as inert).
    * The bracket is placed with the entry from the signal bar: risk / close and 5 x that, picked by the signal's
      side, shifted one bar inside stops() and re-based on the fill (house rule); risk <= 0 emits no entry.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "3h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, rolling extremes and R multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG482473 representative (partner #482797 DUPLICATE, Jaccard 0.859); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the daily trade cap is inert).
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482473_prior_extreme_cross_swing_stop_rr5"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [20, 40],
    "rr": [5.0, 2.0],
}
DEFAULT_PARAMS = {"lookback": 20, "stop_lookback": 10, "rr": 5.0}


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


def _parts(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, k = int(p["lookback"]), int(p["stop_lookback"])
    hh, ll = h.rolling(n).max().shift(1), lo.rolling(n).min().shift(1)
    sl_l = (c - lo.rolling(k).min()) / c
    sl_s = (h.rolling(k).max() - c) / c
    long_e = ((c > hh) & (c.shift(1) <= hh.shift(1)) & (sl_l > 0)).astype(bool)
    short_e = ((c < ll) & (c.shift(1) >= ll.shift(1)) & (sl_s > 0)).astype(bool)
    return long_e, short_e, sl_l.where(long_e, sl_s)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _ = _parts(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl = _parts(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": (p["rr"] * sl).shift(1)}


def portfolio_kwargs(**params):
    return {}
