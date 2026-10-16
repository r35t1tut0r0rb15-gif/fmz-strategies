"""Wyckoff range crosses, 2-hour bars: the close crossing above its SMA 32 together with the low crossing above its SMA 10
goes long (and closes a short); the close crossing below its SMA 35 together with the high crossing below its SMA 20
goes short (and closes a long); a 10 % stop, fixed at the fill (the source re-sizes it from each bar's close).
Port of FMZ strategy #430169 "Gradual Accumulation Breakout Trading Strategy" (Wyckoff Range Strategy).

FMZ source id: 430169

Source
    https://www.fmz.com/strategy/430169 (PineScript v5, FMZ last modified 2023-10-25 17:34:41).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 159-203), accumulation 32, distribution 35, spring 10, upthrust 20, stop 10 %
    enterLong = crossover(close, sma(close, 32)) and crossover(low, sma(low, 10))   (= exitShort)
    enterShort = crossunder(close, sma(close, 35)) and crossunder(high, sma(high, 20)) (= exitLong)
    strategy.exit(stop = close x 0.90) for longs, (stop = close x 1.10) for shorts, re-issued every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stops are re-issued every bar at 10 % from the CURRENT close, so the level moves after
      entry (both ways): rule 2, mark trailing_stop_pending. The port fixes the stop at 10 % of the
      fill price (sl_stop 0.10), as #426604.
    * Each entry signal is also the other side's exit, so every signal reverses: REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving stop fixed at the fill (rule 2).
    2 generic: PASS, moving-average crosses and a percentage stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430169_wyckoff_range_crosses"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "accumulation": [32, 50],
    "stop_pct": [10.0, 5.0],
}
DEFAULT_PARAMS = {"accumulation": 32, "distribution": 35, "spring": 10, "upthrust": 20, "stop_pct": 10.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def _xu(a, b):
    return (a < b) & (a.shift(1) >= b.shift(1))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    acc = _xo(c, c.rolling(int(p["accumulation"])).mean())
    dist = _xu(c, c.rolling(int(p["distribution"])).mean())
    spring = _xo(lo, lo.rolling(int(p["spring"])).mean())
    upthrust = _xu(h, h.rolling(int(p["upthrust"])).mean())
    long_e = (acc & spring).astype(bool)
    short_e = (dist & upthrust).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()   # each exit equals the other side's entry (a reversal)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
