"""One-bar dips above the SMA 100, 1-hour bars, long only: a close more than 3 % under the previous close while above the SMA 100 buys; a close more than 1 % over the previous close closes.
Port of FMZ strategy #438063 "买入低点-MA200优化策略Buying-Dips-MA200-Optimized-Strategy" (Buy The Dips - MA200 Optimised).

FMZ source id: 438063

Source
    https://www.fmz.com/strategy/438063 (PineScript v4, FMZ last modified 2024-01-08 16:54:21).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 108-136), MA 100; lookback 1; date window true
    overall = (close - close[1]) / close[1] x 100;  overall < -3 and close > sma 100 -> entry long;  overall > 1 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * window() is true. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, percent change and SMA side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_438063_one_bar_dip_above_sma100"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "drop": [-3.0, -2.0],
    "ma_len": [100, 200],
}
DEFAULT_PARAMS = {"drop": -3.0, "ma_len": 100, "lookback": 1, "rise": 1.0}


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
    k = int(p["lookback"])
    chg = (c - c.shift(k)) / c.shift(k) * 100
    ma = c.rolling(int(p["ma_len"])).mean()
    le = (chg < float(p["drop"])) & (c > ma)
    lx = chg > float(p["rise"])
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
