"""Three-bar pullbacks on the SMA 100 side, 1-minute bars: above the SMA 100, three lower closes in a row go long; below it, three higher closes go short; reversing; the ratcheting ATR stop is not ported.
Port of FMZ strategy #439260 "基于SMA和ATR的趋势追踪策略SMA-and-ATR-Based-Trend-Tracking-Strategy" (SMA with ATR).

FMZ source id: 439260

Source
    https://www.fmz.com/strategy/439260 (PineScript v5, FMZ last modified 2024-01-18 16:04:51).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 148-219), SMA 100; ATR 10, stop offset 4
    enterLong = close > sma 100 and close < close[1] < close[2] < close[3];  enterShort = close < sma 100 and three higher closes;  entry EL / ES
    longStop = enterLong and not long ? close - 4 atr : max(close - 4 atr, longStop[1]);  exit(SL Long, stop = longStop) while long;  shortStop mirror;  cancel() of unused ids

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop ratchets the close minus 4 ATR(10) bar by bar (it never retreats), re-sent every bar: a
      level the house trail cannot express (its volatility trail takes the best price minus the current
      ATR and may retreat). Not ported: mark trailing_stop_pending; the port keeps the entries. The
      cancel() calls name orders that do not exist and do nothing. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the ratchet stop pending.
    2 generic: PASS, SMA side and close sequences.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_439260_sma100_three_bar_pullback"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [100, 200],
    "run": [3, 2],
}
DEFAULT_PARAMS = {"sma_len": 100, "run": 3}


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
    sma = c.rolling(int(p["sma_len"])).mean()
    lower = pd.Series(True, index=c.index)
    higher = pd.Series(True, index=c.index)
    for k in range(int(p["run"])):
        lower &= c.shift(k) < c.shift(k + 1)
        higher &= c.shift(k) > c.shift(k + 1)
    up = (c > sma) & lower
    dn = (c < sma) & higher
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
