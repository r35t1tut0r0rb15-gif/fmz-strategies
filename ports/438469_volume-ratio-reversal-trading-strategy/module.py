"""Hourly volume ratio: a bar whose volume is more than 3 times its 20-bar average goes long when the close is above the previous close and short otherwise; reversing.
Port of FMZ strategy #438469 "Volume Ratio Reversal Trading Strategy" (Volume Ratio_30min).

FMZ source id: 438469

Source
    https://www.fmz.com/strategy/438469 (PineScript v4, FMZ last modified 2024-01-12 12:08:05).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 149-189), length 20; threshold 3; direction over 1 bar
    vrs = volume / sma(volume, 20);  dir = close / close[1] > 1 ? 1 : -1
    vrs > 3 and dir == 1 -> entry Long;  vrs > 3 and dir == -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A flat close counts as down (dir -1), as written. The date inputs feed nothing (_testPeriod is
      always true). The title says 30 minutes but the backtest header runs 1-hour bars. REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume spikes in the bar's direction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the ratio volume / sma(volume, 20); exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438469_volume_ratio_spike_direction_1h_reversal"
FAMILY = "volume_filter"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "threshold": [3.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "threshold": 3.0, "dir_bars": 1}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    avg = v.rolling(int(p["length"])).mean()
    vrs = v / avg.where(avg != 0)
    spike = vrs > float(p["threshold"])
    up = (c / c.shift(int(p["dir_bars"]))) > 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (spike & up).astype(bool), false, (spike & ~up).astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
