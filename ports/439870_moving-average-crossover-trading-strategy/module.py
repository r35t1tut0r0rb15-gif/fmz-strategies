"""EMA 4 / 8 side with the EMA 20 slope, 1-hour bars: the EMA 4 above the EMA 8 with a rising EMA 20 holds a long, the mirror holds a short; reversing; the entry is sent on every bar of the state.
Port of FMZ strategy #439870 "Moving Average Crossover Trading Strategy" (stub).

FMZ source id: 439870

Source
    https://www.fmz.com/strategy/439870 (PineScript v3, FMZ last modified 2024-01-24 14:59:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 163-206), EMA 4 / 8 / 20; test period true
    go_long = ema4 > ema8 and ema20 > ema20[1];  go_short = ema4 < ema8 and ema20 < ema20[1];  entry simpleBuy / simpleSell;  exit("simpleBuy", "simpleSell", when = exit_long)  -- no price levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two strategy.exit calls carry no profit / loss / stop / limit / trail, so they place no order;
      positions change only by reversal. A same-side entry while in the position is ignored.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA side and slope.
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

NAME = "fmz_439870_ema4_8_side_ema20_slope_state"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "e2": [8, 13],
    "e3": [20, 50],
}
DEFAULT_PARAMS = {"e2": 8, "e3": 20, "e1": 4}


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
    a, b, t = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("e1", "e2", "e3"))
    le = (a > b) & (t > t.shift(1))
    se = (a < b) & (t < t.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
