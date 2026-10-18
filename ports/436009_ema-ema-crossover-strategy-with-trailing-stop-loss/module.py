"""EMA 9 / 21 crossings, 1-minute bars: the EMA 9 crossing over the EMA 21 goes long, crossing under goes short (reversing). The 2 % "trailing stop" is never
set (its highest-high variable stays missing), so there is no exit (as written).
Port of FMZ strategy #436009 "基于EMA均线交叉的移动止损策略EMA-Crossover-Strategy-with-Trailing-Stop-Loss" (EMA Crossover with Trailing Stop-Loss).

FMZ source id: 436009

Source
    https://www.fmz.com/strategy/436009 (PineScript v4, FMZ last modified 2023-12-20 17:39:30).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 117-143), EMA 9 / 21; trail 2 % of the highest high
    longCondition = crossover(ema9, ema21);  shortCondition = crossunder;  entry long / short;  highestHigh := na at a long signal and the update needs high > highestHigh (false against na);  exit(loss = trailingStop) with trailingStop = na

Interpretation choices (Pine rules in SURVEY_README.md)
    * highestHigh is reset to na at each long signal and the next test high > highestHigh is false
      against a missing value, so highestHigh and the stop stay missing and strategy.exit does nothing:
      the strategy only reverses on crossings, as written (the intended 2 % trail is owed). strategy.entry
      reverses: REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, the trailing stop never exists: no exit as written.
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

NAME = "fmz_436009_ema_9_21_cross_no_exit"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 34],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = ((f > s) & (f.shift(1) <= s.shift(1))).fillna(False).astype(bool)
    se = ((f < s) & (f.shift(1) >= s.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
