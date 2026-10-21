"""SMA 50 / 200 golden and death crosses, 30-minute bars: the fast SMA crossing over the slow one goes long, crossing under goes short; reversing.
Port of FMZ strategy #437499 "Golden Cross Uptrend Tracking Strategy" (TFs Golden Cross 1.2).

FMZ source id: 437499

Source
    https://www.fmz.com/strategy/437499 (PineScript v4, FMZ last modified 2024-01-03 11:46:44).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 178-207), fast SMA 50, slow SMA 200; backtest period 2019-2099 (isTestPeriod() = true)
    bullishCross = crossover(sma 50, sma 200) -> entry long;  bearishCross = crossunder(...) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The comment says the strategy does not short, but the code sends a short entry on the death cross:
      ported as coded (an intended long-only version is owed). isTestPeriod() is true: the window is
      dropped. REVERSAL INTENDED. No sizing code. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossing.
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

NAME = "fmz_437499_golden_death_cross"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [50, 20],
    "slow": [200, 100],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200}


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
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
