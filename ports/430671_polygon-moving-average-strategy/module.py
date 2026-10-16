"""EMA 3 / 7 / 13 stack with a trailing stop, 1-hour bars: the close above a rising stack goes long, below a falling stack
goes short; each position trails 2 % behind its best price once 5 % in profit.
Port of FMZ strategy #430671 "Polygon Moving Average Strategy" (BLANK Strategy + TSL).

FMZ source id: 430671

Source
    https://www.fmz.com/strategy/430671 (PineScript v4, FMZ last modified 2023-10-31 14:53:50).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 120-175), EMA 3 / 7 / 13, trail points 5 % of the close, trail offset 2 % of the close
    close > ema3 > ema7 > ema13 -> entry long;  close < ema3 < ema7 < ema13 -> entry short
    exit(trail_points = close x 0.05 / mintick, trail_offset = close x 0.02 / mintick) for each side, every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail activates after a profit of 5 % of the price and then trails 2 % behind the best
      high (low for shorts): ported natively (mark trailing_stop) as {"type": "percent", "pct": 0.02,
      "anchor": "high_low", "activate_after": 0.05}. Stated approximation: the source sizes both
      distances from each bar's close in ticks (re-issued every bar), the house from the fill price.
    * The 2019-2020 date inputs are unused (time_cond = true). strategy.entry reverses: REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is a house trail (approximation stated).
    2 generic: PASS, moving averages and percentage trail distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430671_ema_stack_pct_trail"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_pct": [0.02, 0.04],
    "activate": [0.05, 0.02],
}
DEFAULT_PARAMS = {"e1": 3, "e2": 7, "e3": 13, "trail_pct": 0.02, "activate": 0.05}


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
    a, b, d = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("e1", "e2", "e3"))
    long_e = ((c > a) & (a > b) & (b > d)).astype(bool)
    short_e = ((c < a) & (a < b) & (b < d)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low",
                      "activate_after": float(p["activate"])}}


def portfolio_kwargs(**params):
    return {}
