"""Aroon oscillator (19) crossings of -25, 1-hour bars: crossing up through -25 goes long, crossing down goes short; reversing; a long is also closed when the oscillator falls back through 75, a short when it
rises back through -85.
Port of FMZ strategy #438795 "Aroon Oscillator Based Stock Trading Strategy" (Aroon Oscillator strategy by Saucius).

FMZ source id: 438795

Source
    https://www.fmz.com/strategy/438795 (PineScript v2, FMZ last modified 2024-01-15 14:08:33).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 149-176), length 19; middle -25, high 75, low -85
    up = 100 (highestbars(high, 20) + 19) / 19;  down = 100 (lowestbars(low, 20) + 19) / 19;  osc = up - down
    osc crosses up -25 -> entry Long, close Short;  crosses down -25 -> entry Short, close Long;  osc crosses down 75 -> close Long;  osc crosses up -85 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * highestbars / lowestbars give the offset of the extreme in the last 20 bars (current included; on a
      tie the most recent bar). The closes of the opposite side on an entry bar act on a trade the
      reversing entry already closed, so the reversal stands. strategy.entry reverses: REVERSAL INTENDED.
      No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Aroon oscillator levels.
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

NAME = "fmz_438795_aroon_oscillator_middle_cross"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [19, 25],
    "level_middle": [-25, 0],
}
DEFAULT_PARAMS = {"length": 19, "level_middle": -25.0, "level_high": 75.0, "level_low": -85.0}


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


def _xo(a, lvl):
    return (a > lvl) & (a.shift(1) < lvl)


def _xu(a, lvl):
    return (a < lvl) & (a.shift(1) > lvl)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo = bars_df["high"], bars_df["low"]
    n = int(p["length"])
    hb = h.rolling(n + 1).apply(lambda a: -int(np.argmax(a[::-1])), raw=True)
    lb = lo.rolling(n + 1).apply(lambda a: -int(np.argmin(a[::-1])), raw=True)
    osc = 100 * (hb + n) / n - 100 * (lb + n) / n
    mid = float(p["level_middle"])
    el = _xo(osc, mid)
    es = (osc < mid) & (osc.shift(1) >= mid)             # crossunder(oscillator, level_middle)
    xl = _xu(osc, float(p["level_high"])) & ~es
    xs = _xo(osc, float(p["level_low"])) & ~el
    return el, xl, es, xs


def portfolio_kwargs(**params):
    return {}
