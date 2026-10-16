"""Mid-band cross, 4-hour bars: the close crossing above the average of the SMA 20 and the 20-bar high/low
midpoint goes long, crossing below it goes short.
Port of FMZ strategy #428966 "Trend Tracking Maximized Profit Strategy" (Lawyers Trend Pro Strategy).

FMZ source id: 428966

Source
    https://www.fmz.com/strategy/428966 (PineScript v4, FMZ last modified 2023-10-11 14:38:40).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 121-181), length 20
    MB = (sma(close,20) + (highest(20) + lowest(20)) / 2) / 2
    crossover(close, MB) and not long -> entry long (close short); crossover(MB, close) and not short -> entry short (close long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest(20) / lowest(20) are the high / low over 20 bars, current included. The Bollinger
      deviation is computed but never used in MB.
    * strategy.entry reverses: REVERSAL INTENDED (the isLong / isShort flags let every alternate cross
      through). FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price vs a band mid-line only.
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

NAME = "fmz_428966_mid_band_cross"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    mb = (c.rolling(n).mean() + (h.rolling(n).max() + lo.rolling(n).min()) / 2) / 2
    up = ((c > mb) & (c.shift(1) <= mb.shift(1))).to_numpy()
    dn = ((mb > c) & (mb.shift(1) <= c.shift(1))).to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    is_long = is_short = False
    for i in range(m):
        b = (not is_long) and up[i]
        s = (not is_short) and dn[i]
        if b:
            is_long, is_short = True, False
        if s:
            is_long, is_short = False, True
        le[i], se[i] = b, s
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
