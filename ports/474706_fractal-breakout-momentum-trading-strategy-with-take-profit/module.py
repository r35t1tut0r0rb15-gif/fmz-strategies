"""Fractal-distance entries, daily bars: a close at or under the last bottom fractal plus 107 pips goes long with a target 107 pips over that trigger; a close at or over the last top fractal minus 107 pips goes short with the mirror target (the short wins a bar with both); reversing. The pips are fractions of 42000 of the signal close.
Port of FMZ strategy #474706 "Fractal Breakout Momentum Trading Strategy with Take Profit Optimization" (Fractal Buy/Sell Strategy with 107 Pips Target).

FMZ source id: 474706

Source
    https://www.fmz.com/strategy/474706 (PineScript v5, FMZ last modified 2024-12-11 17:20:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-134), trigger 107 pips; target 107 pips; pip = mintick x 10 = 1.0
    bottom fractal: low[1] < low[2] and low[1] < low -> lastBottom := low[1];  top mirror;  close <= lastBottom + 107 -> entry Buy, exit(limit = lastBottom + 214);  close >= lastTop - 107 -> entry Sell, exit(limit = lastTop - 214)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pip is mintick x 10 = 1.0 in price, so 107 / 214 pips are price amounts, ported as fractions
      of 42000 of the signal close (0.002548 each). The fractal levels are kept from the last fractal
      (a loop). Both entries can be sent on one bar; the later call, the short, wins (#437773). The
      target is sent on each signal bar: the opening signal's target is ported, as a fraction of the
      fill open (a level at or through it is marketable and closed one bar late, as #458256); the
      re-sends of repeat signals are not followed (as #434428, mark trailing_stop_pending). There is no
      stop. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark
      coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the pip target as a fraction of the fill.
    2 generic: PASS, fractal-distance entries with a target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_474706_fractal_distance_107pip_target_reversal"
FAMILY = "pivot_levels"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trig_frac": [0.002548, 0.01],
    "tp_frac": [0.002548, 0.01],
}
DEFAULT_PARAMS = {"trig_frac": 0.002548, "tp_frac": 0.002548}


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


def _kept(level, hit):
    """The level of the last bar where `hit` held (na before the first), as a var."""
    v, k = level.to_numpy(dtype=float), hit.to_numpy()
    out = np.full(len(v), np.nan)
    cur = np.nan
    for i in range(len(v)):
        if k[i]:
            cur = v[i]
        out[i] = cur
    return pd.Series(out, index=level.index)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    lb = _kept(lo.shift(1), (lo.shift(1) < lo.shift(2)) & (lo.shift(1) < lo))
    lt = _kept(h.shift(1), (h.shift(1) > h.shift(2)) & (h.shift(1) > h))
    tf, pf = float(p["trig_frac"]) * c, float(p["tp_frac"]) * c
    bt, tt = lb + tf, lt - tf
    se = c >= tt
    le = (c <= bt) & ~se                         # the later short entry wins a bar with both
    lvl = {"l_tp": bt + pf, "s_tp": tt - pf}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    lx = lf & (lvl["l_tp"].shift(1) <= o) & ~se & ~le    # marketable at the fill
    sx = sf & (lvl["s_tp"].shift(1) >= o) & ~le & ~se
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
