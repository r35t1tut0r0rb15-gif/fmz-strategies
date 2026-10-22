"""SMA 11 / 31 trend with an SMA 5 filter, 3-hour bars, long only: the SMA 11 over the SMA 31 with the close over the SMA 5 buys; the SMA 11 under the SMA 31 sells.
Port of FMZ strategy #473157 "Advanced Dual Moving Average Momentum Trend Following Trading System" (Nifty 30m SMA Crossover Long).

FMZ source id: 473157

Source
    https://www.fmz.com/strategy/473157 (PineScript v5, FMZ last modified 2024-11-27 16:54:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-122), SMA 31 / 11 / 5 (constants); date window 2020-2024; qty 1
    in window: entry Long when sma11 > sma31 and close > sma5;  close Long when sma11 < sma31

Interpretation choices (Pine rules in SURVEY_README.md)
    * The date window is dropped like other date windows. The entry test is a state: repeated entries
      while held do nothing; the entry and exit tests cannot hold together. The title names Nifty and 30
      minutes; the header's 3-hour bars are followed. The fixed 1-unit quantity is not ported. Long only.
      FREQ = "3h" from the backtest header (UTC-aligned 3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA trend with a short filter.
    3 crypto-exchange-only: no (exchange pair in the header only (Nifty named in the title)).
    4 signals only: fixed quantity stored, not ported.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473157_sma11_31_trend_sma5_filter_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [11, 5],
    "slow": [31, 50],
    "filt": [5, 10],
}
DEFAULT_PARAMS = {"fast": 11, "slow": 31, "filt": 5}


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
    f, s, ft = (c.rolling(int(p[k])).mean() for k in ("fast", "slow", "filt"))
    le = (f > s) & (c > ft)
    lx = f < s
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
