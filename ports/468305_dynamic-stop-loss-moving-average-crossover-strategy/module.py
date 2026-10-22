"""EMA 9 / 21 crossings with swing stops and 1:3 targets, daily bars: the cross up goes long with a stop at the 5-bar low and a target three times that distance over the close, the cross down goes short with the mirror levels; reversing.
Port of FMZ strategy #468305 "Dynamic Stop Loss Moving Average Crossover Strategy" (RAMZY CRYPTO-KING).

FMZ source id: 468305

Source
    https://www.fmz.com/strategy/468305 (PineScript v5, FMZ last modified 2024-09-26 14:47:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 263-308), EMA 9 / 21; stop lowest(low, 5) / highest(high, 5) (current bar included); target close +- 3 x the stop distance; trail_offset 0 (no trail points)
    crossover(ema9, ema21) -> close Short, entry Long + exit(limit = close + 3 x (close - swingLow), stop = swingLow, trail_offset = 0)
    crossunder -> close Long, entry Short + exit(limit = close - 3 x (swingHigh - close), stop = swingHigh, trail_offset = 0)

Interpretation choices (Pine rules in SURVEY_README.md)
    * trail_offset without trail_price / trail_points places no trailing stop (#441084). The levels are
      prices fixed on the signal bar, sent as fractions of the fill open (the signal bar's levels shifted
      into the fill bar); a level already at or through the fill open is marketable and is sent as a
      bar-close exit on the fill bar (one bar late). Cross-ups and cross-downs alternate, so each entry
      opens a new position. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on
      daily bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar levels as fractions of the fill.
    2 generic: PASS, EMA crossings with swing stops and 1:3 targets.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_468305_ema9_21_cross_swing_stop_3r_target_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_len": [9, 5],
    "long_len": [21, 50],
    "rr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"short_len": 9, "long_len": 21, "rr": 3.0, "swing": 5}


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


def _parts(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    a = c.ewm(span=int(p["short_len"]), adjust=False).mean()
    b = c.ewm(span=int(p["long_len"]), adjust=False).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    n, rr = int(p["swing"]), float(p["rr"])
    sw_l, sw_h = lo.rolling(n).min(), h.rolling(n).max()
    sl = sw_l.where(le, sw_h.where(se))                       # stop level on each signal bar
    tp = (c + rr * (c - sw_l)).where(le, (c - rr * (sw_h - c)).where(se))
    return le, se, sl, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, sl, tp = _parts(bars_df, p)
    o = bars_df["open"]
    was_l, was_s = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    s1, t1 = sl.shift(1), tp.shift(1)
    lx = was_l & ((s1 >= o) | (t1 <= o)) & ~se   # a level through the fill: closed at the next open
    sx = was_s & ((s1 <= o) | (t1 >= o)) & ~le
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, sl, tp = _parts(bars_df, p)
    o = bars_df["open"]
    was_l = le.shift(1, fill_value=False)
    s1, t1 = sl.shift(1), tp.shift(1)                         # the signal bar's levels, read at the fill
    sl_f = (1 - s1 / o).where(was_l, s1 / o - 1)
    tp_f = (t1 / o - 1).where(was_l, 1 - t1 / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
