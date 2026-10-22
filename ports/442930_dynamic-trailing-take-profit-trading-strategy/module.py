"""SMA 14 / 28 crossings, 1-hour bars: the SMA 14 crossing over goes long, under goes short; the trailing take-profit (a limit re-set every bar at the previous high + 1.5 ATR, low - 1.5 ATR for shorts) is
described and kept pending; reversing.
Port of FMZ strategy #442930 "Dynamic Trailing Take Profit Trading Strategy" (TrailingTakeProfit example).

FMZ source id: 442930

Source
    https://www.fmz.com/strategy/442930 (PineScript v5, FMZ last modified 2024-02-27 14:43:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 210-241), SMA 14 / 28; ATR 7 x 1.5; margin 100, qty 1, capital 100
    crossover(sma14, sma28) -> entry Long;  crossunder -> entry Short
    long: exit(limit = high[1] + 1.5 atr(7));  short: exit(limit = low[1] - 1.5 atr(7)) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The take-profit limit is re-sent on every bar at the previous bar's high (low) plus (minus) 1.5
      ATR, a level that moves after entry: stops() cannot express a level re-set every bar, so it is
      described here and kept pending (as #438034, mark trailing_stop_pending). Positions end at the
      opposite entry until then. The margin, quantity and capital are sizing. strategy.entry reverses:
      REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving take-profit described (pending).
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: margin, quantity and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND438046 (2 members, best partner #438046, Jaccard 0.768); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_442930_sma14_28_cross_trailing_take_profit_pending"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [14, 9],
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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
