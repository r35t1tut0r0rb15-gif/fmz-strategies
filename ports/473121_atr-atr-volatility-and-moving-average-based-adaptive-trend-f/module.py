"""Close crossings of the SMA 50, 1-hour bars, long only: the close crossing over the SMA buys, and the long is never closed (the exit bands are built around the same close they are compared with).
Port of FMZ strategy #473121 "基于ATR波动率和均线的自适应趋势跟踪退出策略-ATR-Volatility-and-Moving-Average-Based-Adaptive-Trend-Following-Exit-Strategy" (ATR Band Exit Strategy).

FMZ source id: 473121

Source
    https://www.fmz.com/strategy/473121 (PineScript v5, FMZ last modified 2024-11-27 14:07:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 123-157), SMA 50; ATR 14 x 2 bands around the current close
    crossover(close, sma50) -> entry Long;  close >= close + 2 atr -> close Long;  close <= close - 2 atr -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bands are the current close plus / minus 2 ATR, so the exit tests compare the close with
      itself plus or minus a positive distance and can never hold: the first cross-up opens a long held
      to the end of the data, as written (as #451391). Long only. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA cross-ups (the exits never hold, as written).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473121_close_cross_sma50_bands_never_hit_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_len": [50, 20],
}
DEFAULT_PARAMS = {"ma_len": 50}


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
    ma = c.rolling(int(p["ma_len"])).mean()
    le = (c > ma) & (c.shift(1) <= ma.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
