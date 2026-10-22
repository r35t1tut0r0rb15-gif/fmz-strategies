"""Close crossing its EMA 20, 4-hour bars: a crossing on an up close goes long, a crossing on a down close goes short; reversing.
Port of FMZ strategy #442961 "Mayan Treasure Hunting Guide" (Megalodon).

FMZ source id: 442961

Source
    https://www.fmz.com/strategy/442961 (PineScript v5, FMZ last modified 2024-02-27 16:33:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 131-160), EMA 20 on the close; highest / lowest close 8 (plots only)
    cross(close, ema) and close[1] < close -> entry Buy;  cross(close, ema) and close[1] > close -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.cross fires on a crossing in either direction; the bar's close direction picks the side. The
      8-bar highs and lows only plot. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ =
      "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with the close direction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442961_ema20_cross_close_direction_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
}
DEFAULT_PARAMS = {"length": 20}


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
    e = c.ewm(span=int(p["length"]), adjust=False).mean()
    d, d1 = c - e, (c - e).shift(1)
    cross = ((d > 0) & (d1 <= 0)) | ((d < 0) & (d1 >= 0))
    le = cross & (c.shift(1) < c)
    se = cross & (c.shift(1) > c)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
