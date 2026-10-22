"""EMA 9 / 21 crossings with the close on the same side of the EMA 21, 1-hour bars: the cross up with the close above goes long, the cross down with the close below goes short; reversing. The ATR bracket
from the 2-bar extremes is re-sent every bar and is not ported (pending).
Port of FMZ strategy #439190 "黄金快速突破EMA交易策略Gold-Fast-Breakthrough-EMA-Trading-Strategy" (XAUUSD Strategy).

FMZ source id: 439190

Source
    https://www.fmz.com/strategy/439190 (PineScript v4, FMZ last modified 2024-01-18 11:37:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 128-157), EMA 9 / 21; ATR 2 x 2; profit target and commission inputs unused
    long = crossover(ema 9, ema 21) and close > ema 21 -> entry Long;  short mirror -> entry Short;  every bar: exit(Long, stop = lowest(2) - 2 atr(2), limit = highest(2) + 2 atr(2)), shorts mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent on every bar from the latest 2-bar extremes and ATR, so its levels move after
      entry: stops() cannot express a level re-set every bar, so it is described and kept pending (as
      #437036, mark trailing_stop_pending). Positions end at the opposite entry until then. The profit
      target and commission inputs feed nothing. strategy.entry reverses: REVERSAL INTENDED. No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; unused profit / commission inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_439190_ema9_21_cross_atr_bracket_pending"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
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
    up = (f > s) & (f.shift(1) <= s.shift(1)) & (c > s)
    dn = (f < s) & (f.shift(1) >= s.shift(1)) & (c < s)
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
