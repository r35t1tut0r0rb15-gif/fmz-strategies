"""Open-price SMA crossings, 1-minute bars: the slow SMA of opens crossing over the fast one (the fast falling through the slow) goes long; the fast crossing over the slow goes short (reversing).
Port of FMZ strategy #436533 "SMA Crossover Trading Strategy" (SMA Cross Entry & Exit Strategy).

FMZ source id: 436533

Source
    https://www.fmz.com/strategy/436533 (PineScript v3, FMZ last modified 2023-12-25 16:03:48).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 117-163), fast SMA 36, slow SMA 46, both of the open
    maFast = sma(open, 36);  maSlow = sma(open, 46);  enterLong = crossover(maSlow, maFast);  exitLong = crossover(maFast, maSlow)
    entry "Long Entry" when window and enterLong;  entry "Short Entry" (short) when window and exitLong

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long is entered when the SLOW average crosses over the FAST one, as written (a counter-trend
      reading of the names). The date window starts 2018-09-01 and never ends; it is treated as always
      true. REVERSAL INTENDED. The default quantity is sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crossings.
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

NAME = "fmz_436533_open_sma_cross_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [36, 20],
    "slow": [46, 60],
}
DEFAULT_PARAMS = {"fast": 36, "slow": 46}


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
    o = bars_df["open"]
    fast, slow = o.rolling(int(p["fast"])).mean(), o.rolling(int(p["slow"])).mean()
    slow_over = ((slow > fast) & (slow.shift(1) <= fast.shift(1))).fillna(False).astype(bool)
    fast_over = ((fast > slow) & (fast.shift(1) <= slow.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return slow_over, false, fast_over, false.copy()


def portfolio_kwargs(**params):
    return {}
