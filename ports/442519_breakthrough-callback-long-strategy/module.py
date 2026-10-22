"""Bearish outside bars, 1-hour bars, long only: a bar with a lower low, a higher high and a close under its open goes long; the stop is that bar's low (the take-profit input only plots).
Port of FMZ strategy #442519 "Breakthrough Callback Long Strategy" (Outside (OB)).

FMZ source id: 442519

Source
    https://www.fmz.com/strategy/442519 (PineScript v3, FMZ last modified 2024-02-22 15:41:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-149), outside bar: low < low[1], high > high[1], close < open; stop valuewhen(signal, low, 0); take profit 2 % (plotted only)
    allConditions = low < low[1] and high > high[1] and close < open -> entry Long
    strategy.exit(from_entry = Long, stop = valuewhen(allConditions, low, 0))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is the low of the signal bar: sl_stop = (close - low) / close of the signal bar, shifted
      one bar inside stops() and re-based on the fill (a low equal to the close places no stop); a new
      signal while long moves the script's stop, which the port does not follow (as #439608). The
      take-profit value is only plotted. Long only. Stop module: portfolio_kwargs {} (driver D4). No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry from signal-bar data.
    2 generic: PASS, outside-bar pattern.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442519_bearish_outside_bar_low_stop_long"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {}
DEFAULT_PARAMS = {}


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


def _fraction(bars_df):
    c, lo = bars_df["close"], bars_df["low"]
    return (c - lo) / c


def simulate(bars_df, **params):
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    sig = ((lo < lo.shift(1)) & (h > h.shift(1)) & (c < o)).to_numpy()
    sl = _fraction(bars_df).to_numpy()
    ov, lv = o.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, entry_i, s_ = 0, -1, 0.0
    for i in range(m):
        if pos == 1 and i >= entry_i and s_ > 0 and lv[i] <= ov[entry_i] * (1 - s_):
            pos = 0
        if pos == 0 and sig[i] and i + 1 < m:
            le[i], pos, entry_i, s_ = True, 1, i + 1, sl[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    return {"sl_stop": _fraction(bars_df).shift(1)}


def portfolio_kwargs(**params):
    return {}
