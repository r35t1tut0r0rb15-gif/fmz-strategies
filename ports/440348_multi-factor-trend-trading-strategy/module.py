"""SMA 9 / 21 crossings with fixed breakout levels, 1-hour bars: as written for BTC the close is always above the 1600 resistance, so a long is entered on every bar; the SMA 9 crossing under the SMA 21 goes
short for that bar; the written exits place nothing; reversing.
Port of FMZ strategy #440348 "Multi factor Trend Trading Strategy" (Combined Strategy).

FMZ source id: 440348

Source
    https://www.fmz.com/strategy/440348 (PineScript v4, FMZ last modified 2024-01-29 15:17:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 157-191), SMA 9 / 21; support 1500, resistance 1600 (price constants, "replace with your level"); BB 20 / 2 plotted only
    longCondition = crossover(sma9, sma21) or close > 1600 -> entry Long;  shortCondition = crossunder(sma9, sma21) or close < 1500 -> entry Short
    strategy.exit("ExitLong", from_entry = "Long", when = crossunder(close, sma21)) and the short mirror, with no levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the support and resistance are fixed prices; the port uses fractions of the close at
      the BTC reading near 42000 (1600 / 42000 = 0.0381, 1500 / 42000 = 0.0357), which keeps the reading:
      the resistance test is always true and the support test never. The exit calls have no profit,
      loss, stop, limit or trail, so they place nothing (as #439111). The short entry is written after
      the long one and wins on a cross-down bar (as #437773); the next bar's long entry reverses back.
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, fixed price levels -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440348_sma_cross_fixed_breakout_levels"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "res_frac": 0.0381, "sup_frac": 0.0357}


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
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    long_ = up | (c > float(p["res_frac"]) * c)
    short_ = dn | (c < float(p["sup_frac"]) * c)
    false = pd.Series(False, index=c.index)
    return long_ & ~short_, false, short_, false.copy()


def portfolio_kwargs(**params):
    return {}
