"""Momentum crash warning, short only, 2-hour bars: a 50-bar momentum under -5 (re-expressed as a fraction of the close) holds a short; the momentum crossing over the VIX-fix value (read on the same price
scale) closes it.
Port of FMZ strategy #439741 "Momentum and Fear Index Crossover Strategy" (S&P Bear Warning).

FMZ source id: 439741

Source
    https://www.fmz.com/strategy/439741 (PineScript v4, FMZ last modified 2024-01-23 14:27:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 139-187), momentum 50 of close; bands 5 / -5; VIX fix 22; ATR 14 (plot only)
    mom = close - close[50];  VIXFix = (highest(close, 22) - low) / highest(close, 22) x 100;  entry SELL when mom < -5;  close SELL when crossover(mom, VIXFix)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the momentum is in price units and is compared with -5 and with the VIX fix (a
      percent); both become fractions of the close: mom / close < -5 / 42000 and mom / close crossing over
      VIXFix / 42000 (the BTC reading near 42000). The entry is sent on every bar of the state and the
      two tests cannot share a bar. Short only. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit momentum tests -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only: Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439741_momentum_crash_warning_short"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [50, 20],
    "scale": [42000.0, 4200.0],
}
DEFAULT_PARAMS = {"len": 50, "scale": 42000.0, "band_lower": -5.0, "vix_len": 22}


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
    lo, c = bars_df["low"], bars_df["close"]
    s = float(p["scale"])
    mom = (c - c.shift(int(p["len"]))) / c
    hc = c.rolling(int(p["vix_len"])).max()
    vix = (hc - lo) / hc * 100 / s
    se = mom < float(p["band_lower"]) / s
    sx = (mom > vix) & (mom.shift(1) <= vix.shift(1))
    false = pd.Series(False, index=c.index)
    return false, false.copy(), se, sx


def portfolio_kwargs(**params):
    return {}
