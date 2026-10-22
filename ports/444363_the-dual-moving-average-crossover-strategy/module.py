"""SMA 14 / 28 crossings, 1-hour bars: the fast SMA crossing over the slow goes long, crossing under goes short (shorting allowed by default); reversing.
Port of FMZ strategy #444363 "The Dual Moving Average Crossover Strategy" (#2idagos (dual moving average crossover)).

FMZ source id: 444363

Source
    https://www.fmz.com/strategy/444363 (PineScript v5, FMZ last modified 2024-03-11 12:06:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 146-186), fast SMA 14, slow SMA 28 (type inputs Simple); allow shorting true; margins 100 / 100
    crossover(fast, slow) -> entry Long;  crossunder(fast, slow) and allowShorting -> entry Short;  crossunder and not allowShorting -> close Long (never: shorting allowed)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both type inputs default to Simple, so the averages are SMAs. With shorting allowed the close
      branch never acts. strategy.entry reverses: REVERSAL INTENDED. The margin settings are sizing. FREQ
      = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the margin settings stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG444363 (2 members, best partner #458025, Jaccard 0.914); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_444363_sma14_28_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [14, 10],
    "slow": [28, 50],
}
DEFAULT_PARAMS = {"fast": 14, "slow": 28}


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
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
