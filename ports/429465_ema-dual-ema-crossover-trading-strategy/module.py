"""EMA 25 crossing EMA 75 of the close, hourly bars: crossing over goes long, crossing under goes short; reversing.
Port of FMZ strategy #429465 "双EMA金叉死叉交易策略Dual-EMA-Crossover-Trading-Strategy" (Double EMA CROSS).

FMZ source id: 429465

Source
    https://www.fmz.com/strategy/429465 (PineScript v4, FMZ last modified 2023-10-17 13:56:54).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 219-263), EMA 25 / 75; start date 2020-01-01; volume only colours the bars
    crossover(ema(close, 25), ema(close, 75)) -> entry Long;  crossunder -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The volume tests only colour the bars, so volume does not reach the orders: ported as not using
      volume (check 8). The author's 2020-01-01 start is dropped. REVERSAL INTENDED. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossover.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the author's 2020 start dropped).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429465_ema25_75_cross_reversal"
FAMILY = "ma_crossover"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [25, 12],
    "slow": [75, 50],
}
DEFAULT_PARAMS = {"fast": 25, "slow": 75}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
