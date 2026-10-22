"""Crossings of the last 2-bar pivot levels, broker days: the close crossing over the last pivot-low support within 0.4 % of it goes long, crossing under the last pivot-high resistance within 0.4 % goes short, each with a 10 % stop and 26 % target from the entry price; reversing.
Port of FMZ strategy #477944 "Dynamic Support and Resistance Adaptive Pivot Trading Strategy" (Dynamic Support and Resistance Pivot Strategy).

FMZ source id: 477944

Source
    https://www.fmz.com/strategy/477944 (PineScript v6, FMZ last modified 2025-01-10 15:08:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 83-169), pivot length 2; distance 0.4 %; stop 10 %, target 26 % of strategy.position_avg_price
    pivothigh(2, 2) -> resistance := high[2];  pivotlow(2, 2) -> support := low[2];  crossover(close, support) and |close / support - 1| <= 0.4 % -> entry Long;  crossunder(close, resistance) and near it -> entry Short
    in a position: exit(stop = avg x (1 -/+ 10 %), limit = avg x (1 +/- 26 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * A pivot is confirmed 2 bars after its centre bar (strict, as Pine's pivothigh / pivotlow) and its
      level is kept until the next one. The bracket is sent from the position's average price while it is
      held: scalar fractions of the entry fill, active from the fill (as #440797). REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; avg-price bracket as fractions of the fill.
    2 generic: PASS, pivot support / resistance crossings with a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored.
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

NAME = "fmz_477944_pivot2_sr_cross_near_pct_bracket_reversal"
FAMILY = "support_resistance"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "pivot_length": [2, 5],
    "distance_pct": [0.4, 1.0],
}
DEFAULT_PARAMS = {"pivot_length": 2, "distance_pct": 0.4, "sl_pct": 0.10, "tp_pct": 0.26}


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
    """Strict pivot of x at t - span, confirmed at t (Pine ta.pivothigh / pivotlow on the chart bars)."""
    v = np.asarray(x, dtype=float)
    m = len(v)
    out = np.zeros(m, dtype=bool)
    for t in range(2 * span, m):
        c = v[t - span]
        rest = np.concatenate([v[t - 2 * span:t - span], v[t - span + 1:t + 1]])
        if np.isnan(c) or np.isnan(rest).any():
            continue
        out[t] = (c > rest).all() if side > 0 else (c < rest).all()
    return out


def _kept(flag, value):
    """var level := value on flag bars, kept between them (na before the first)."""
    v = np.where(flag, value, np.nan)
    idx = np.where(flag, np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    out = v[idx]
    out[~np.maximum.accumulate(flag)] = np.nan
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k = int(p["pivot_length"])
    res = pd.Series(_kept(_pivot(h, 1, k), h.shift(k).to_numpy()), index=c.index)
    sup = pd.Series(_kept(_pivot(lo, -1, k), lo.shift(k).to_numpy()), index=c.index)
    d = float(p["distance_pct"]) / 100
    near_s = (c >= sup * (1 - d)) & (c <= sup * (1 + d))
    near_r = (c >= res * (1 - d)) & (c <= res * (1 + d))
    le = near_s & (c > sup) & (c.shift(1) <= sup.shift(1))
    se = near_r & (c < res) & (c.shift(1) >= res.shift(1))
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
