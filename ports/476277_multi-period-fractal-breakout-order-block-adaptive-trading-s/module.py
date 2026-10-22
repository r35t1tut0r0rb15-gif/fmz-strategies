"""Breaks of the last 2-bar fractal high or low, broker days: the high crossing over the last up-fractal level goes long, the low crossing under the last down-fractal level goes short, once per fractal; reversing.
Port of FMZ strategy #476277 "Multi Period Fractal Breakout Order Block Adaptive Trading Strategy" (Supply and Demand - Order Block Strategy).

FMZ source id: 476277

Source
    https://www.fmz.com/strategy/476277 (PineScript v5, FMZ last modified 2024-12-27 15:49:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 79-222), fractal periods 2; break type Wick+Body (high / low); boxes and table drawn only (commented out)
    upFractal = high[2] == highest(high, 5) -> topValue := high[2], topBreakBlock := false;  downFractal = low[2] == lowest(low, 5) -> bottomValue := low[2], bottomBreakBlock := false
    crossover(high, topValue) and not topBreakBlock -> block, position <= 0: entry Long;  crossunder(low, bottomValue) and not bottomBreakBlock -> block, position >= 0: entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The break tests run before the fractal updates on each bar, so a break is measured against the
      level known at the previous bar's close; a fractal is the centre bar equal to the 5-bar high (low),
      ties included, as written. Each level breaks once until the next fractal. The position tests only
      skip a same-side entry, which the engine ignores anyway; on a bar with both breaks from flat the
      later short call wins (#437773). REVERSAL INTENDED. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, fractal level breaks.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_476277_fractal2_level_break_once_reversal"
FAMILY = "channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [2, 3, 5],
}
DEFAULT_PARAMS = {"n": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo = bars_df["high"], bars_df["low"]
    n = int(p["n"])
    w = 2 * n + 1
    upf = (h.shift(n) == h.rolling(w).max()).to_numpy()
    dnf = (lo.shift(n) == lo.rolling(w).min()).to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(hv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    top = bot = np.nan
    top_blk = bot_blk = False
    for i in range(1, m):
        if hv[i] > top and hv[i - 1] <= top and not top_blk:
            top_blk, le[i] = True, True
        if lv[i] < bot and lv[i - 1] >= bot and not bot_blk:
            bot_blk, se[i] = True, True
        if upf[i]:
            top_blk, top = False, hv[i - n]
        if dnf[i]:
            bot_blk, bot = False, lv[i - n]
    ix = bars_df.index
    le_s, se_s = pd.Series(le, index=ix), pd.Series(se, index=ix)
    false = pd.Series(False, index=ix)
    return le_s & ~se_s, false, se_s, false.copy()


def portfolio_kwargs(**params):
    return {}
