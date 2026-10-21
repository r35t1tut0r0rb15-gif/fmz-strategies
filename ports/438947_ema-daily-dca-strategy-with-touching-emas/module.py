"""First-bar-of-the-day EMA cross buys held one bar, 3-minute bars, long only: on the first bar of a UTC day, a close crossing above any of the EMAs 5 / 10 / 20 / 50 / 100 / 200 buys; the always-true sell
closes the position at the next bar's close.
Port of FMZ strategy #438947 "每日均成本策略结合EMA触碰信号Daily-DCA-Strategy-with-Touching-EMAs" (Daily DCA Strategy with Touching EMAs).

FMZ source id: 438947

Source
    https://www.fmz.com/strategy/438947 (PineScript v4, FMZ last modified 2024-01-16 15:30:17).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 262-297), daily investment 50000; start 2022-01-01; pyramiding limit 10000; enable sell on (sell condition true)
    isNewDay = dayofmonth != dayofmonth[1] and time >= start;  isNewDay and close crosses over any EMA (5 / 10 / 20 / 50 / 100 / 200) -> entry Buy;  enable_sell and true -> close_all on every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The sell condition is the constant true, so close_all runs on every bar: it acts on the position
      held at the bar close, so each buy is closed at the close of the bar after its fill (one-bar
      trades), as written (owed: a real sell rule). dayofmonth is read on the bar's UTC open time (as
      #435514). The start date (2022-01-01) never ends; it is treated as always true (as #436533).
      pyramiding never stacks (one buy per day, closed the next bar). Long only. The investment quantity
      is sizing. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, day-start EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the daily investment quantity and pyramiding stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: UTC day start of the bar.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438947_day_start_ema_cross_one_bar"
FAMILY = "calendar_seasonal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fastest": [5, 3],
    "slowest": [200, 100],
}
DEFAULT_PARAMS = {"fastest": 5, "slowest": 200}


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
    any_x = pd.Series(False, index=c.index)
    for n in (int(p["fastest"]), 10, 20, 50, 100, int(p["slowest"])):
        e = c.ewm(span=n, adjust=False).mean()
        any_x = any_x | ((c > e) & (c.shift(1) <= e.shift(1)))
    dom = pd.Series(bars_df.index.tz_convert("UTC").day, index=c.index)
    new_day = (dom != dom.shift(1)).to_numpy()
    buy = (any_x.to_numpy() & new_day)
    buy[0] = False
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend_e, pend_x = 0, False, False
    for i in range(m):
        if pend_x:                                       # orders of the last bar fill at this open
            pos, pend_x = 0, False
        if pend_e:
            pos, pend_e = 1, False
        if buy[i] and pos == 0 and i + 1 < m:
            le[i], pend_e = True, True
        if pos == 1:                                     # close_all on every bar with a position
            lx[i], pend_x = True, True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
