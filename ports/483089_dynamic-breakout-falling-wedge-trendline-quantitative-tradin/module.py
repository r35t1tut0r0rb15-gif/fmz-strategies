"""Falling-wedge breakouts from the last two 5 / 5 pivot highs and lows, broker days, long only: with both lines falling and the upper falling faster, the close crossing over the upper line goes long with a 2 % stop and a 20 % target from the signal close.
Port of FMZ strategy #483089 "Dynamic Breakout Falling Wedge Trendline Quantitative Trading Strategy" (Falling Wedge Strategy by Nitin).

FMZ source id: 483089

Source
    https://www.fmz.com/strategy/483089 (PineScript v6, FMZ last modified 2025-02-27 17:02:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 107-174), pivots 5 / 5; take profit 20 %; stop 2 %; MPL 2.0 notice
    last two pivot highs (h1 newest, h2) and lows (l1, l2) with their bars;  upper = h2 + slope_h x (bar - i2);  lower = l2 + slope_l x (bar - j2)
    h1 < h2 and l1 < l2 and slope_h < slope_l < 0 ... and crossover(close, upper) -> entry Buy + exit(stop = close x 0.98, limit = close x 1.20)

Interpretation choices (Pine rules in SURVEY_README.md)
    * A pivot is confirmed 5 bars after its bar (Pine's pivothigh / pivotlow, the centre strictly beyond
      every bar of the 5 on each side). The upper line exists only on bars where the wedge test holds (as
      the local variable inside the if block); its crossover needs the line on the bar before too. The
      levels are fixed at the signal close and sent as fractions of the fill open (a level at or through
      it is marketable and closed one bar late, as #458256). A repeat breakout while held re-sends the
      bracket; stops() keeps the first, so the repeat case is marked trailing_stop_pending (as #434428).
      Long only; Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). Stops on
      daily bars: mark coarse_bar_stop. No sizing code (margin 100 / 100). The MPL 2.0 notice is kept with
      the verbatim copy (ported, stated). Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: PASS, falling-wedge trendline breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483089_falling_wedge_pivot5_upper_line_break_2_20pct_bracket_long"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "pivot_bars": [5, 3],
    "take_profit_percent": [20.0, 10.0],
}
DEFAULT_PARAMS = {"pivot_bars": 5, "take_profit_percent": 20.0, "stop_loss_percent": 2.0}


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


def _pivot(x, side, span=5):
    """Strict pivot of x at t - span, confirmed at t (Pine ta.pivothigh / pivotlow), on rolling
    windows: the centre beats every bar of the span on each side."""
    s = x if side > 0 else -x
    centre = s.shift(span)
    left = s.shift(span + 1).rolling(span).max()
    right = s.rolling(span).max()
    return ((centre > left) & (centre > right)).to_numpy()


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k = int(p["pivot_bars"])
    ph, pl = _pivot(h, 1, k), _pivot(lo, -1, k)
    hv, lv, cv = (x.to_numpy(dtype=float) for x in (h, lo, c))
    m = len(cv)
    upper = np.full(m, np.nan)
    highs, lows = [], []
    for i in range(m):
        if ph[i]:
            highs = [(hv[i - k], i - k)] + highs[:1]
        if pl[i]:
            lows = [(lv[i - k], i - k)] + lows[:1]
        if len(highs) >= 2 and len(lows) >= 2:
            (h1, i1), (h2, i2) = highs
            (l1, j1), (l2, j2) = lows
            mu, ml = (h1 - h2) / (i1 - i2), (l1 - l2) / (j1 - j2)
            if h1 < h2 and l1 < l2 and mu < ml and mu < 0 and ml < 0:
                upper[i] = h2 + mu * (i - i2)
    up = pd.Series(upper, index=c.index)
    le = (c > up) & (c.shift(1) <= up.shift(1))
    a, b = float(p["stop_loss_percent"]) / 100, float(p["take_profit_percent"]) / 100
    return le, {"l_sl": c * (1 - a), "l_tp": c * (1 + b)}


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    false = pd.Series(False, index=o.index)
    return le, lf & l_thr & ~le, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    sl_f = 1 - lvl["l_sl"].shift(1) / o
    tp_f = lvl["l_tp"].shift(1) / o - 1
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
