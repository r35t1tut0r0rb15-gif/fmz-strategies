"""Z-score turn, long only, 4-hour bars: the z-score of WMA 3 of ohlc4 against its EMA 17 (in 17-bar standard
deviations) below -1 and rising goes long; above +1 and falling closes the long.
Port of FMZ strategy #429954 "Trend Breakout Strategy Based on Moving Average Deviation" (Escaping of Rate from Avarage By Mustafa OZVER).

FMZ source id: 429954

Source
    https://www.fmz.com/strategy/429954 (PineScript v4, FMZ last modified 2023-10-23 15:38:37).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 189-220), WMA 3 of ohlc4, length 17
    F = wma(ohlc4, 3); z = (F - ema(F,17)) / stdev(F,17)
    z < -1 and change(z) > 0 -> strategy.order long; z > 1 and change(z) < 0 -> strategy.close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.order adds on every signal (sizing, the adds are not ported); the close shuts the whole
      long. stdev is the population deviation. The short lines are commented out. Long only.
      FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a z-score only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the repeated adds stored.
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

NAME = "fmz_429954_wma_zscore_turn_long"
FAMILY = "zscore_reversion"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [17, 34],
    "band": [1.0, 1.5],
}
DEFAULT_PARAMS = {"length": 17, "band": 1.0}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (o + h + lo + c) / 4
    w = np.array([1.0, 2.0, 3.0])
    f = src.rolling(3).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)
    n = int(p["length"])
    z = (f - f.ewm(span=n, adjust=False).mean()) / f.rolling(n).std(ddof=0).replace(0.0, np.nan)
    b = float(p["band"])
    long_e = ((z < -b) & (z.diff() > 0)).astype(bool)
    long_x = ((z > b) & (z.diff() < 0)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
