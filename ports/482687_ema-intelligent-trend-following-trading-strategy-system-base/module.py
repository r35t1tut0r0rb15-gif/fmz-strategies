"""EMA 10 / 20 crosses confirmed by the close beyond both EMAs, always in, inside a 2017-01-01 to 2029-01-30 window,
hourly bars.
Port of FMZ strategy #482687 "基于EMA双均线交叉的智能趋势跟踪交易策略系统-Intelligent-Trend-Following-Trading-Strategy-System-Based-on-EMA-Double-Moving-Average-Crossover" (BFX Buy and Sell).

FMZ source id: 482687

Source
    https://www.fmz.com/strategy/482687 (PineScript v5, FMZ last modified 2025-02-27 17:52:35).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 32-69), EMA 10 / 20, window 2017-01-01 00:00 to 2029-01-30 23:59
    crossover(ema10, ema20) and close > both and in window -> entry long; crossunder mirrored -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Clock rule (check 9 / C6): timestamp() without a zone uses the exchange zone; read as UTC (the author's
      Binance pair). Signals outside the window are dropped; a position held at the window's end stays open, as
      written. The window matters only for data before 2017.
    * Entries reverse (REVERSAL INTENDED). Signal module, no stops. FREQ = "1h" from the backtest header. The
      signals are #482764's (same batch) plus this window.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, two EMAs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used; trading window 2017-01-01 00:00 to 2029-01-30 23:59 UTC.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482687_ema10_20_cross_confirmed_window"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 5],
    "slow": [20, 50],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 20}
WINDOW = (pd.Timestamp("2017-01-01 00:00", tz="UTC"), pd.Timestamp("2029-01-30 23:59", tz="UTC"))


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    inside = pd.Series((bars_df.index >= WINDOW[0]) & (bars_df.index <= WINDOW[1]), index=bars_df.index)
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (c > f) & (c > s) & inside).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & (c < f) & (c < s) & inside).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
