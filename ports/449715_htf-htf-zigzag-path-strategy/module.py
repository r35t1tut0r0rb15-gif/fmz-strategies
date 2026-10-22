"""The colour of the day's last 15-minute bar, daily bars: a red last 15-minute bar goes long, a green one goes short; reversing.
Port of FMZ strategy #449715 "HTF-锯齿形路径策略HTF-Zigzag-Path-Strategy" (HTF Zigzag Path Strategy).

FMZ source id: 449715

Source
    https://www.fmz.com/strategy/449715 (PineScript v5, FMZ last modified 2024-04-28 14:00:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 116-168), "higher" time frame 15 (lower than the daily chart)
    [o, h, l, c] = security("15", ohlc);  c < o -> entry Alım (long);  c > o -> entry Satım (short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 15-minute request is a LOWER time frame than the daily chart, so it returns the day's LAST
      15-minute bar (as #436765), built left-labelled from the minutes and grouped by broker day. The
      zigzag lines and boxes are commented out. Both conditions are levels; a repeated entry on the
      held side is ignored. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the 15-minute bar ends with the daily bar.
    2 generic: PASS, contrarian colour of the day's last 15-minute bar.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449715_last_15m_bar_colour_contrarian_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tf_minutes": [15, 60],
}
DEFAULT_PARAMS = {"tf_minutes": 15}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    ltf = df.resample("%dmin" % int(p["tf_minutes"]), label="left", closed="left").agg(
        {"open": "first", "close": "last"}).dropna(how="all")
    last = ltf.groupby(broker_day(ltf.index)).last()                 # the day's last lower-time-frame bar
    bars["ltf_open"] = last["open"]
    bars["ltf_close"] = last["close"]
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    o, c = bars_df["ltf_open"], bars_df["ltf_close"]
    le = c < o
    se = c > o
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
