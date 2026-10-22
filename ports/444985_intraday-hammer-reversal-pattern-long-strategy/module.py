"""A red hammer followed by a green bar with a higher low, daily bars, long only: goes long with a stop at the hammer's low and a target at 1.5 times the signal close.
Port of FMZ strategy #444985 "Intraday Hammer Reversal Pattern Long Strategy" (Hammer Pattern and Follow-Up Green Candle Strategy).

FMZ source id: 444985

Source
    https://www.fmz.com/strategy/444985 (PineScript v5, FMZ last modified 2024-03-15 17:13:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-124), hammer: red, body <= 30 % of the range, open - low >= 2 bodies, high <= open x 1.01; stop low[1]; target close x 1.5; qty 50000 / close
    isHammer (on bar [1]) and close > open and low > low[1] -> entry Hammer Buy (qty 50000 / close), exit(stop = low[1], limit = close x 1.5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lower wick is measured from the open, as written (for a red candle the body's bottom is the
      close). The stop and target are fixed on the signal bar: sl_stop = (close - low[1]) / close and
      tp_stop = 0.5, shifted one bar inside stops() and re-based on the fill. A repeated signal inside a
      trade re-sends the exit with new levels; that move is not followed: mark trailing_stop_pending
      (as #440292). A repeated entry while long is ignored (one position). Daily stop module: mark
      coarse_bar_stop. Stop module: portfolio_kwargs {} (driver D4). Long only. The 50000 / close
      quantity is sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop and target fixed on the signal bar.
    2 generic: PASS, hammer and follow-up candle pattern.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 50000 / close quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_444985_red_hammer_green_follow_long_stop_low"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "body_frac": [0.3, 0.5],
    "target_mult": [1.5, 1.1],
}
DEFAULT_PARAMS = {"body_frac": 0.3, "target_mult": 1.5, "wick_mult": 2.0, "upper_tol": 1.01}


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


def _signal(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    o1, h1, l1, c1 = o.shift(1), h.shift(1), lo.shift(1), c.shift(1)
    body = (c1 - o1).abs()
    hammer = ((c1 < o1) & (body <= (h1 - l1) * float(p["body_frac"]))
              & ((o1 - l1) >= body * float(p["wick_mult"]))
              & (((h1 - o1) == 0) | (h1 <= o1 * float(p["upper_tol"]))))
    return hammer & (c > o) & (lo > l1)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    false = pd.Series(False, index=bars_df.index)
    return _signal(bars_df, p), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sl = (c - bars_df["low"].shift(1)) / c
    tp = pd.Series(float(p["target_mult"]) - 1.0, index=c.index)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
