"""SMA 50 / 200 golden and death crosses, 15-minute bars: a golden cross goes long, a death cross goes short; reversing.
Port of FMZ strategy #439621 "Precise Trend Reversal Moving Average Crossover Strategy" ([S_R__9] - Death and Golden Cross).

FMZ source id: 439621

Source
    https://www.fmz.com/strategy/439621 (PineScript v5, FMZ last modified 2024-01-22 12:14:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-176), SMA 50 / 200; specific date range off
    deathCross = crossunder(sma50, sma200) -> entry "Death Cross long" (short);  goldenCross = crossover -> entry "Golden Cross short" (long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry ids are swapped in name only; the directions are the usual ones. The date filter is off.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "15min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings.
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

NAME = "fmz_439621_sma50_200_golden_death_cross"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
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
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
