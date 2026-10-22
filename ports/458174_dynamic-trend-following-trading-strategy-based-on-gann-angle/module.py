"""Close crossings of the last confirmed 14-bar swing levels, 1-hour bars: the close crossing over the last swing low goes long, crossing under the last swing high goes short; reversing. The 1 % / 2 % bracket is re-sent every bar from the latest close and is not ported (pending).
Port of FMZ strategy #458174 "Dynamic Trend Following Trading Strategy Based on Gann Angles" (Gann Strategy).

FMZ source id: 458174

Source
    https://www.fmz.com/strategy/458174 (PineScript v5, FMZ last modified 2024-07-30 15:53:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-210), swing high / low = high[14] / low[14] equal to the 29-bar extreme; Gann angles 45 degrees; stop 1 %, target 2 % of the current close
    gann_up = swingLow + tan(45) x (bar_index - valuewhen(not na(swingLow), bar_index, 0));  gann_down likewise from swingHigh
    crossover(close, gann_up) -> entry Long;  crossunder(close, gann_down) -> entry Short;  while held: exit(limit / stop = close x (1 +- 0.02 / 0.01))

Interpretation choices (Pine rules in SURVEY_README.md)
    * swingLow and swingHigh are kept (var) once set, so valuewhen(not na(...), bar_index, 0) is the
      current bar_index on every later bar and the angle term is always 0: the Gann lines are the last
      confirmed swing low and high themselves, as written. A swing is confirmed 14 bars after it (the
      extreme of the 29 bars ending now, ties included). The bracket is re-sent on every bar while a
      trade is open from that bar's close, so its levels move after entry: stops() cannot express a
      level re-set every bar, so it is described here and kept pending (as #438034, mark
      trailing_stop_pending). Positions end at the opposite entry until then. REVERSAL INTENDED. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, swing-level crossings; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_458174_confirmed_swing_level_cross_reversal"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
}
DEFAULT_PARAMS = {"length": 14}


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


def _kept(x):
    """A Pine var set only on some bars: the last value set, na before the first."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    last = np.nan
    for i in range(len(v)):
        if not np.isnan(v[i]):
            last = v[i]
        out[i] = last
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    w = 2 * n + 1
    hn, ln = h.shift(n), lo.shift(n)
    sh = _kept(hn.where(hn == h.rolling(w).max()))   # the last confirmed swing high
    sl = _kept(ln.where(ln == lo.rolling(w).min()))
    le = (c > sl) & (c.shift(1) <= sl.shift(1))
    se = (c < sh) & (c.shift(1) >= sh.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
