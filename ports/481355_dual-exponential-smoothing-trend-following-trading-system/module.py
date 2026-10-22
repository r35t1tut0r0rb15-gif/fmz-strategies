"""Crossings of two exponentially weighted averages (9 and 30 bars, normalized weights) of (high + low + 2 close) / 4, broker days: the short crossing over the long goes long, under goes short, each with a 30-point stop and target from the signal close; reversing.
Port of FMZ strategy #481355 "Dual Exponential Smoothing Trend Following Trading System" (Dynamic Trend Navigator AI [CodingView]).

FMZ source id: 481355

Source
    https://www.fmz.com/strategy/481355 (PineScript v5, FMZ last modified 2025-02-10 14:46:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-185), windows 9 / 30; weights (1 - 2 / (n + 1))^i over the last n bars; target / stop 30 points; 200 % of equity
    avg(n) = sum(src[i] w^i) / sum(w^i), i = 0..n-1, w = 1 - 2 / (n + 1);  s9 crosses over s30 -> close Short, entry Long, levels close +/- 30;  crosses under -> close Long, entry Short, levels close -/+ 30;  every bar: exit(Long / Short, limit, stop) from the stored levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are stored on the signal bar and re-sent unchanged every bar, so the bracket is the
      signal bar's: the 30 points are price amounts, ported as fractions of 42000 of the signal close
      (7.14e-04), sent as fractions of the fill open (a level at or through it is marketable and closed
      one bar late, as #458256); the crossings alternate, so no repeat moves them. REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. The 200 % of
      equity size and capital are sizing. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; point bracket as fractions of the fill.
    2 generic: PASS, weighted-average crossings with a point bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_481355_weighted_avg9_30_cross_point_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "primary": [9, 5],
    "secondary": [30, 60],
}
DEFAULT_PARAMS = {"primary": 9, "secondary": 30, "tp_frac": 7.14286e-04, "sl_frac": 7.14286e-04}


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


def _wavg(x, n):
    """sum(x[i] w^i) / sum(w^i) over i = 0..n-1 (i = 0 the current bar), w = 1 - 2 / (n + 1)."""
    w = (1 - 2 / (n + 1)) ** np.arange(n, dtype=float)
    rev = w[::-1]                                     # rolling windows run oldest to newest
    return x.rolling(n).apply(lambda v: np.dot(v, rev) / rev.sum(), raw=True)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    src = (h + lo + 2 * c) / 4
    a, b = _wavg(src, int(p["primary"])), _wavg(src, int(p["secondary"]))
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    tp, sl = float(p["tp_frac"]) * c, float(p["sl_frac"]) * c
    lvl = {"l_sl": c - sl, "l_tp": c + tp, "s_sl": c + sl, "s_tp": c - tp}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se, se, sf & s_thr & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
