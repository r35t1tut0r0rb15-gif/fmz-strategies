"""EMA 20 / 55 ribbon crossings, 1-hour bars: the EMA 20 crossing over the EMA 55 goes long, crossing under goes short; reversing.
Port of FMZ strategy #439622 "EMA Ribbon Strategy" (EMA Ribbon [Krypt] with Buy/Sell Signals).

FMZ source id: 439622

Source
    https://www.fmz.com/strategy/439622 (PineScript v4, FMZ last modified 2024-01-22 12:21:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 158-204), EMAs 20 / 25 / 30 / 35 / 40 / 45 / 50 / 55 of close (dropn 1); signals on MA-1 / MA-8
    price = dropn(close, 1) (na on the first bar);  buySignal = crossover(ema20, ema55) -> entry long;  else sellSignal = crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * dropn leaves the first bar undefined, so the EMAs start on the second bar; the inner ribbon lines
      only feed the plots. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings.
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

NAME = "fmz_439622_ema_ribbon_20_55_cross"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length1": [20, 10],
    "length8": [55, 100],
}
DEFAULT_PARAMS = {"length1": 20, "length8": 55}


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
    price = c.where(c.shift(1).notna())                 # dropn(close, 1)
    a = price.ewm(span=int(p["length1"]), adjust=False).mean()
    b = price.ewm(span=int(p["length8"]), adjust=False).mean()
    up = (a > b) & (a.shift(1) <= b.shift(1))
    dn = (a < b) & (a.shift(1) >= b.shift(1)) & ~up
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
