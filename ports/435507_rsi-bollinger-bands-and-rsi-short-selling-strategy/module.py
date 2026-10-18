"""Bollinger band shorts, 1-minute bars, short only: the close crossing over the upper band (20, 2 sd) with the RSI 14 under 70 goes
short; the close crossing back under the upper band with the RSI over 70 closes it. The exit order's levels are swapped
(stop below, limit above), so it fills at the next open, as written.
Port of FMZ strategy #435507 "布林带和RSI短线策略Bollinger-Bands-and-RSI-Short-Selling-Strategy" (Bollinger Bands and RSI Short Selling).

FMZ source id: 435507

Source
    https://www.fmz.com/strategy/435507 (PineScript v5, FMZ last modified 2023-12-15 15:54:05).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 215-246), Bollinger 20 / 2 sd; RSI 14 at 70; stop 1 %, take profit 7 %
    entry short when crossover(close, upper) and RSI < 70 and not long (position_size <= 0);  if crossover(upper, close) and RSI > 70: exit(stop = avg (1 - 7 %), limit = avg (1 + 1 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit order is sent for a short with the stop BELOW the average price (take-profit level
      as stop) and the limit ABOVE it (stop-loss level as limit): both are already reached when
      placed, so the order fills at the next open. The port is an exit signal on that
      condition, and the intended 1 % stop / 7 % target bracket is owed. The start-date window
      (1 December 2021) is the author's backtest window: dropped. The entry is allowed when flat
      or already short (position_size <= 0); a second short adds nothing. The 30 % of equity size
      and commission are sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, exit levels swapped: exit signal as written.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, commission and the percent bracket inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435507_bollinger_rsi_short"
FAMILY = "bollinger_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "rsi_len": 14, "level": 70}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    upper = basis + float(p["mult"]) * c.rolling(n).std(ddof=0)
    r = int(p["rsi_len"])
    ch = c.diff()
    up_ = ch.clip(lower=0).ewm(alpha=1 / r, adjust=False).mean()
    dn_ = (-ch.clip(upper=0)).ewm(alpha=1 / r, adjust=False).mean()
    rsi = (100 - 100 / (1 + up_ / dn_)).where(dn_ != 0, 100.0).where(up_.notna())
    lvl = float(p["level"])
    se = ((c > upper) & (c.shift(1) <= upper.shift(1)) & (rsi < lvl)).fillna(False).astype(bool)
    sx = ((upper > c) & (upper.shift(1) <= c.shift(1)) & (rsi > lvl)).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return false, false.copy(), se, sx


def portfolio_kwargs(**params):
    return {}
