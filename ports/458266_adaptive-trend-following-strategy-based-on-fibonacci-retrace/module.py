"""Close crossings of the 20-bar closing range's 61.8 % and 38.2 % retracement lines, 1-hour bars: the close crossing over the 61.8 % line goes long, crossing under the 38.2 % line goes short, each with a 100-point target and 50-point stop from the fill; reversing.
Port of FMZ strategy #458266 "Adaptive Trend Following Strategy Based on Fibonacci Retracement" (Fibonacci Retracement Strategy).

FMZ source id: 458266

Source
    https://www.fmz.com/strategy/458266 (PineScript v5, FMZ last modified 2024-07-31 14:14:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 217-258), highest / lowest close over 20 bars (the input n unused); fib 0.618 / 0.382 from the high; target 100, stop 50 points from the average price
    crossover(close, high - range x 0.618) -> entry Long;  crossunder(close, high - range x 0.382) -> entry Short
    every bar: exit(Long, limit = avg + 100, stop = avg - 50);  exit(Short, limit = avg - 100, stop = avg + 50)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket comes from the average (fill) price and is sent every bar: ported active from the
      fill bar (#440797). The 100 / 50 points are price amounts, ported as fractions of 42000 (0.00238 /
      0.00119 of the fill). The "number of candles" input is never used (20 is written in). REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the point bracket as fractions of the fill.
    2 generic: PASS, retracement-line crossings with a point bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458266_close_range_fib_line_cross_point_bracket_reversal"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 50],
    "tp_frac": [0.00238, 0.01],
    "sl_frac": [0.00119, 0.005],
}
DEFAULT_PARAMS = {"length": 20, "tp_frac": 0.00238, "sl_frac": 0.00119}


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
    n = int(p["length"])
    hi, lw = c.rolling(n).max(), c.rolling(n).min()
    f618, f382 = hi - (hi - lw) * 0.618, hi - (hi - lw) * 0.382
    le = (c > f618) & (c.shift(1) <= f618.shift(1))
    se = (c < f382) & (c.shift(1) >= f382.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_frac"]), "tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
