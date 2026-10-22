"""Close against the previous open, daily bars, long only: a close more than 1 % over the previous bar's open buys; a close more than 1 % under it sells. The 2 % / 1 % bracket is re-sent every bar from the latest close and is not ported (pending).
Port of FMZ strategy #471690 "Open Market Exposure Dynamic Position Adjustment Quantitative Trading Strategy" (Open Market Exposure (OME) Strategy).

FMZ source id: 471690

Source
    https://www.fmz.com/strategy/471690 (PineScript v5, FMZ last modified 2024-11-12 14:48:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-138), OME = (close - open[1]) / open[1], summed within the day (reset each new day); threshold 0.01; target 2 %, stop 1 % of the current close; Sharpe figures computed only
    cum_ome > 0.01 -> entry Long;  cum_ome < -0.01 -> close Long;  long: exit(limit = close x 1.02);  exit(stop = close x 0.99)  (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * dayofweek changes on every daily bar, so the cumulative OME is reset each bar and equals that
      bar's OME. The bracket is re-sent on every bar from that bar's close, so its levels move after
      entry: stops() cannot express a level re-set every bar, so it is described here and kept pending
      (as #438034, mark trailing_stop_pending). The Sharpe figures feed no order. Long only. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close vs previous open thresholds; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_471690_close_vs_prev_open_exposure_threshold_long"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "threshold": [0.01, 0.02],
}
DEFAULT_PARAMS = {"threshold": 0.01}


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
    o, c = bars_df["open"], bars_df["close"]
    ome = (c - o.shift(1)) / o.shift(1)
    t = float(p["threshold"])
    false = pd.Series(False, index=bars_df.index)
    return ome > t, ome < -t, false, false.copy()


def portfolio_kwargs(**params):
    return {}
