"""EMA scalper, 1-minute bars, short only: the EMA 9 crossing over the EMA 26 opens a SHORT (the entry id "long" is placed with
strategy.short); the position is closed when the EMA 100 crosses under the EMA 55.
Port of FMZ strategy #435477 "EMA黄金交叉短线交易策略EMA-Golden-Cross-Short-term-Trading-Strategy" (EMA SCALPEUR).

FMZ source id: 435477

Source
    https://www.fmz.com/strategy/435477 (PineScript v5, FMZ last modified 2023-12-15 11:16:18).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 134-154), EMA 9 / 26 for the entry, EMA 100 / 55 for the exit
    buy = crossover(ema(close, 9), ema(close, 26)) -> entry "long" with strategy.short ("ENTER-SHORT");  buyexit = crossunder(ema(close, 100), ema(close, 55)) -> close "long" ("EXIT-SHORT")

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry is named "long" but its direction is strategy.short, and its comment says
      ENTER-SHORT: the port follows the direction (short only) and says so. A second entry while short
      adds nothing. The exit is a crossing of the slow pair, as written (EMA 100 under EMA 55).
      FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the initial capital input stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG435477 (2 members, best partner #438484, Jaccard 0.843); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435477_ema_scalper_short"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_l": [9, 5],
    "ema_l2": [26, 21],
}
DEFAULT_PARAMS = {"ema_l": 9, "ema_l2": 26, "ema_s": 100, "ema_s2": 55}


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
    e1 = c.ewm(span=int(p["ema_l"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ema_l2"]), adjust=False).mean()
    e3 = c.ewm(span=int(p["ema_s"]), adjust=False).mean()
    e4 = c.ewm(span=int(p["ema_s2"]), adjust=False).mean()
    se = ((e1 > e2) & (e1.shift(1) <= e2.shift(1))).fillna(False).astype(bool)
    sx = ((e3 < e4) & (e3.shift(1) >= e4.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return false, false.copy(), se, sx


def portfolio_kwargs(**params):
    return {}
