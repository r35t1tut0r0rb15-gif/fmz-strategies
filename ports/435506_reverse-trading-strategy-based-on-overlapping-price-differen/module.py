"""Overlapping price-difference reversal, 10-minute bars, long only, with a bracket: a 30-bar price change below zero turning up
through its 15-bar weighted average (both under zero, the move over a minimum size) goes long with a target and stop of about
1 % of the price; the opposite turn closes the long.
Port of FMZ strategy #435506 "Reverse Trading Strategy Based on Overlapping Price Differentials" (Fst).

FMZ source id: 435506

Source
    https://www.fmz.com/strategy/435506 (PineScript v3, FMZ last modified 2023-12-15 15:47:23).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 160-184), sum 30, signal WMA 15, minimum |sum| 20 price units; profit and loss 95 / 1000 of the close in ticks
    f = close - close[1];  ff = sum(f, 30) (= close - close[30]);  dd1 = wma(ff, 15);  bull = ff < 0 and dd1 < 0 and ff[1] < dd1 and ff > dd1 and |ff| > 20;  bear = the mirror
    bull -> entry long;  exit(profit = close 95 / 1000 ticks, loss = close 95 / 1000 ticks);  bear -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the sum of the 30 changes is the 30-bar price change; the 20 price units
      become a fraction of the close, min_move (0.0005 is the reading on BTC at about 40000). The
      tick bracket close x 0.095 ticks is a fraction of the price equal to 0.095 x the tick size
      (0.0095 for a 0.1 tick); the port uses sl_stop = tp_stop = a fixed fraction of the fill price
      (0.0095, or 0.02). The author's levels follow the current close each bar; the port fixes them
      at the entry fill. Long only; the bear signal only closes.
    * Stop module: portfolio_kwargs {} (driver D4). Stops on 10-minute bars: not coarse. FREQ =
      "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, price-unit move and tick bracket -> fractions of the price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the initial capital input stored; the tick bracket quoted in original_sizing.txt.
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

NAME = "fmz_435506_price_change_reversal_bracket"
FAMILY = "reversal_pattern"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bracket": [0.0095, 0.02],
    "min_move": [0.0005, 0.005],
}
DEFAULT_PARAMS = {"length": 30, "signal": 15, "bracket": 0.0095, "min_move": 0.0005}


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
    ff = c.diff().rolling(int(p["length"])).sum()
    n = int(p["signal"])
    w = np.arange(1, n + 1, dtype=float)
    dd1 = ff.rolling(n).apply(lambda a: float(np.dot(a, w) / w.sum()), raw=True)
    big = ff.abs() > float(p["min_move"]) * c
    bull = (ff < 0) & (dd1 < 0) & (ff.shift(1) < dd1) & (ff > dd1) & big
    bear = (ff > 0) & (dd1 > 0) & (ff.shift(1) > dd1) & (ff < dd1) & big
    false = pd.Series(False, index=bars_df.index)
    return bull.fillna(False).astype(bool), bear.fillna(False).astype(bool), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["bracket"]), "tp_stop": float(p["bracket"])}


def portfolio_kwargs(**params):
    return {}
