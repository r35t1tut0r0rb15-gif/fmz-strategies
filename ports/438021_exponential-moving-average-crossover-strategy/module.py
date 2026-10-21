"""Crossings of the 100-bar midpoint, 1-hour bars, at most one long and one short in all: the first close crossing over the 50 % level of the 100-bar range goes long with a target at the 10-bar high, the first
crossing under goes short with a target at the 10-bar low; the re-arming test can never pass, so no later entries are sent.
Port of FMZ strategy #438021 "Exponential Moving Average Crossover Strategy" (Fibonacci Strategy).

FMZ source id: 438021

Source
    https://www.fmz.com/strategy/438021 (PineScript v5, FMZ last modified 2024-01-08 11:30:21).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 123-158), Fibonacci level 0.5; range 100 bars; exit targets highest(high, 10) / lowest(low, 10)
    fib = lowest(low, 100) + (highest(high, 100) - lowest(low, 100)) x 0.5;  crossover(close, fib) -> if not inLong: entry Buy, inLong := true;  exit(Exit, Buy, limit = highest(high, 10))
    crossunder(close, fib) -> if not inShort: entry Sell, inShort := true;  exit(Exit, Sell, limit = lowest(low, 10));  crossover(close, highest(high, 10)) or crossunder(close, lowest(low, 10)) -> both flags false

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 10-bar high includes the current bar, so the close can never cross over it (nor under the
      10-bar low): the flags are never reset and the script sends one Buy and one Sell entry in its whole
      history, as written (owed: the intended re-arming). The target is the 10-bar extreme of the signal
      bar: tp_stop = highest(high, 10) / close - 1 for a long (1 - lowest(low, 10) / close for a short) of
      the signal bar, shifted one bar inside stops() and re-based on the fill (a zero distance places no
      target). A later crossing bar inside the trade re-sends the exit and moves the target: described,
      not emitted (mark trailing_stop_pending). The Sell entry reverses an open long: REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed at entry (re-sent targets marked).
    2 generic: PASS, range midpoint and rolling extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_438021_range_midpoint_cross_once"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fib_level": [0.5, 0.618],
    "range_len": [100, 50],
}
DEFAULT_PARAMS = {"fib_level": 0.5, "range_len": 100, "exit_len": 10}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, k = int(p["range_len"]), int(p["exit_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    fib = ll + (hh - ll) * float(p["fib_level"])
    lc = ((c > fib) & (c.shift(1) <= fib.shift(1))).to_numpy()
    sc = ((c < fib) & (c.shift(1) >= fib.shift(1))).to_numpy()
    hx, lx = h.rolling(k).max(), lo.rolling(k).min()
    reset = (((c > hx) & (c.shift(1) <= hx.shift(1))) | ((c < lx) & (c.shift(1) >= lx.shift(1)))).to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    in_l = in_s = False
    for i in range(m):
        if lc[i] and not in_l:
            le[i], in_l = True, True
        if sc[i] and not in_s:
            se[i], in_s = True, True
        if reset[i]:
            in_l = in_s = False
    return pd.Series(le, index=bars_df.index), pd.Series(se, index=bars_df.index), hx, lx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, hx, lx = _signals(bars_df, p)
    c = bars_df["close"]
    tp = pd.Series(np.where(le.to_numpy(), (hx / c - 1.0).to_numpy(), (1.0 - lx / c).to_numpy()), index=c.index)
    return {"tp_stop": tp.where(tp > 0).shift(1)}


def portfolio_kwargs(**params):
    return {}
