"""SMA Ichimoku crosses, long only, 1-hour bars: the SMA 9 crossing above the SMA 26 with the close above both spans of 26
bars ago (span A = their average, span B = the SMA 52) goes long; the SMA 9 crossing under the SMA 26, or the close
under both spans of 26 bars ago, closes it.
Port of FMZ strategy #432305 "Momentum Ichimoku Cloud Trading Strategy" (Ichimoku Cloud Strategy).

FMZ source id: 432305

Source
    https://www.fmz.com/strategy/432305 (PineScript v5, FMZ last modified 2023-11-16 10:56:22).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 176-202), SMA 9 / 26 / 52, displacement 26
    tenkan = sma(close, 9); kijun = sma(close, 26); spanA = (tenkan + kijun) / 2; spanB = sma(close, 52)
    crossover(tenkan, kijun) and close > spanA[26] and close > spanB[26] -> entry long
    crossunder(tenkan, kijun) or close < spanA[26] and close < spanB[26] -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lines are SMAs of the close, as written (not mid-ranges). The spans are read 26 bars back
      (spanA[26], spanB[26]), i.e. the cloud drawn under the current bar. Pine's "and" binds before
      "or". Long only; Opposite entries cannot occur. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crosses and lagged spans.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432305_sma_ichimoku_cross_long"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conv": [9, 7],
    "disp": [26, 13],
}
DEFAULT_PARAMS = {"conv": 9, "base": 26, "span_b": 52, "disp": 26}


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
    tk = c.rolling(int(p["conv"])).mean()
    kj = c.rolling(int(p["base"])).mean()
    d = int(p["disp"])
    sa = ((tk + kj) / 2).shift(d)
    sb = c.rolling(int(p["span_b"])).mean().shift(d)
    up = (tk > kj) & (tk.shift(1) <= kj.shift(1))
    dn = (tk < kj) & (tk.shift(1) >= kj.shift(1))
    le = (up & (c > sa) & (c > sb)).astype(bool)
    lx = (dn | ((c < sa) & (c < sb))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
