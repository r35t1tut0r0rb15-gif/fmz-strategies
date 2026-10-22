"""SMA 5 / 11 crossings beyond the Bollinger 22 / 1.5 band on the SMA 55 side, 5-minute bars: an up-cross with the close over the SMA 55 and under the lower band goes long, the mirror goes short; the close crossing back through the SMA 5 or the SMA 55 side closes; reversing.
Port of FMZ strategy #482820 "Multi Moving Average and Bollinger Bands Crossover Options Quantitative Trading Strategy" (MA5 MA11 Bollinger Bands 22 Strategy).

FMZ source id: 482820

Source
    https://www.fmz.com/strategy/482820 (PineScript v5, FMZ last modified 2025-02-20 14:53:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 114-160), SMA 5 / 11 / 55; Bollinger 22 x 1.5; ATR 14 bracket 1.5 / 3
    crossover(ma5, ma11) and close > ma55 and close < lowerBB -> entry Long;  crossunder(ma5, ma11) and close < ma55 and close > upperBB -> entry Short
    crossunder(close, ma5) or close < ma55 -> close Long;  crossover(close, ma5) or close > ma55 -> close Short
    every bar: exit Long (stop = close - 1.5 atr, limit = close + 3 atr), exit Short (stop = close + 1.5 atr, limit = close - 3 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ATR bracket is re-sent on every bar from that bar's close, so its levels follow the price: not
      ported, mark trailing_stop_pending (as the C170-C175 readings); the close conditions are the exits.
      A close of the side being entered on the same bar is masked by the entry. An entry on the other
      side reverses (REVERSAL INTENDED). No sizing code. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent ATR bracket pending.
    2 generic: PASS, SMA crossings beyond the Bollinger bands.
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

NAME = "fmz_482820_sma5_11_cross_bb22_1_5_beyond_sma55_side_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 3],
    "dev": [1.5, 2.0],
}
DEFAULT_PARAMS = {"fast": 5, "dev": 1.5, "slow": 11, "trend": 55, "bb_length": 22}


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
    s = c.rolling(int(p["slow"])).mean()
    t = c.rolling(int(p["trend"])).mean()
    n = int(p["bb_length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    upper, lower = basis + float(p["dev"]) * sd, basis - float(p["dev"]) * sd
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (c > t) & (c < lower)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (c < t) & (c > upper)
    lx = ((c < f) & (c.shift(1) >= f.shift(1))) | (c < t)
    sx = ((c > f) & (c.shift(1) <= f.shift(1))) | (c > t)
    return le, lx & ~le & ~se, se, sx & ~se & ~le


def portfolio_kwargs(**params):
    return {}
