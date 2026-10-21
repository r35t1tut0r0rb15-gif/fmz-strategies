"""SMA 14 / 28 crossings on the side of the EMA 200, 1-hour bars: the cross up above the EMA 200 goes long, the cross down below it goes short; reversing. The trailing take-profit (previous high + 1.5 ATR 7,
re-sent every bar) is not ported (pending).
Port of FMZ strategy #438046 "基于EMA200的移动止盈移动止损策略EMA-200-Based-Trailing-Take-Profit-and-Trailing-Stop-Loss-Strategy" (EMA 200 Based Trailing Take Profit).

FMZ source id: 438046

Source
    https://www.fmz.com/strategy/438046 (PineScript v5, FMZ last modified 2024-01-08 15:50:52).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 135-161), SMA 14 / 28, EMA 200; ATR 7 x 1.5; quantity 1, capital 100
    long = crossover(sma 14, sma 28) and close > ema 200 -> entry Long;  short = crossunder and close < ema 200 -> entry Short;  every bar: exit(from Long, limit = high[1] + 1.5 atr(7)), exit(from Short, limit = low[1] - 1.5 atr(7))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The take-profit limits are re-sent on every bar from the previous high (low) and the current ATR,
      so they move after entry: stops() cannot express a level re-set every bar, so it is described here
      and kept pending (as #437036, mark trailing_stop_pending). Positions end at the opposite entry until
      then. REVERSAL INTENDED. The quantity and capital are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings and EMA side; per-bar target described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity, capital and margins stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND438046 (2 members, best partner #442930, Jaccard 0.768); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_438046_sma14_28_cross_ema200_side"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [14, 7],
    "slow": [28, 56],
}
DEFAULT_PARAMS = {"fast": 14, "slow": 28, "trend": 200}


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
    t = c.ewm(span=int(p["trend"]), adjust=False).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1)) & (c > t)
    dn = (f < s) & (f.shift(1) >= s.shift(1)) & (c < t)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
