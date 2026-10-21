"""Three moving averages, 5-minute bars: the SMA 5 crossing over the SMA 20 with the SMA 20 above the SMA 100 goes long, the cross under with the SMA 20 below the SMA 100 goes short; reversing (the percent
stop and target are off).
Port of FMZ strategy #438978 "Triangular Moving Average Crossover Trading Strategy" (kozlod_3ma).

FMZ source id: 438978

Source
    https://www.fmz.com/strategy/438978 (PineScript v3, FMZ last modified 2024-01-16 18:18:02).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 180-298), MA type SMA; lengths 5 / 20 / 100 on close; SL 0 %, PT 0 % (off); 5 % of equity
    long = crossover(short, medium) and medium > long ma -> entry long;  short = crossunder and medium < long ma -> entry short;  SL / PT closes only when their percent is above 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * SL and PT are 0 (off), so the close-tested exits never fire. The MA type is swept over SMA and EMA
      (the other types are not swept). strategy.entry reverses: REVERSAL INTENDED. The 5 % of equity size
      is sizing. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crossings with a trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and the off SL / PT inputs stored.
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

NAME = "fmz_438978_kozlod_three_ma_cross"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_type": ["SMA", "EMA"],
    "short_len": [5, 10],
}
DEFAULT_PARAMS = {"ma_type": "SMA", "short_len": 5, "medium_len": 20, "long_len": 100}


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

    def _ma(n):
        return c.ewm(span=n, adjust=False).mean() if p["ma_type"] == "EMA" else c.rolling(n).mean()

    s, md, lg = _ma(int(p["short_len"])), _ma(int(p["medium_len"])), _ma(int(p["long_len"]))
    up = (s > md) & (s.shift(1) <= md.shift(1)) & (md > lg)
    dn = (s < md) & (s.shift(1) >= md.shift(1)) & (md < lg)
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
