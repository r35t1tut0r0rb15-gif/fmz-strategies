"""SMA 7 / 30 crossings, 3-hour bars, long only: the SMA 7 crossing over the SMA 30 goes long, crossing under closes.
Port of FMZ strategy #441067 "Dynamic SMA Cross Trend Strategy" (Onchain Edge Trend SMA Strategy).

FMZ source id: 441067

Source
    https://www.fmz.com/strategy/441067 (PineScript v4, FMZ last modified 2024-02-05 12:14:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-205), source close; incomplete bars on (offset 0); forecast "flat"; SMA 7 / 30 / 50 (50 plotted only); capital 100000, risk 1 %; 10 % of equity
    enterLong = crossover(fastMA, mediumMA) -> entry Enter Long (qty = 1 % of 100000 / (2 atr(14)));  exitLong = crossunder(fastMA, mediumMA) -> close Enter Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * With incomplete bars on the source offset is 0, and the "flat" forecast returns the source (the
      forecast function is never called). The quantity from the capital, risk and ATR, and the 10 % of
      equity default, are sizing. Long only. FREQ = "3h" from the backtest header (bars on UTC multiples of
      3 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the ATR risk quantity and percent-of-equity default stored.
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

NAME = "fmz_441067_sma7_30_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [7, 14],
    "medium": [30, 60],
}
DEFAULT_PARAMS = {"fast": 7, "medium": 30}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["medium"])).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return up, dn, false, false.copy()


def portfolio_kwargs(**params):
    return {}
