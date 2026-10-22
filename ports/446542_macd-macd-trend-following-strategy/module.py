"""MACD (3, 9, 5) above its signal and above zero goes long, below both goes short, daily bars; a long closes when the MACD falls under its signal, a short when it rises over it; reversing.
Port of FMZ strategy #446542 "MACD趋势跟踪策略-MACD-Trend-Following-Strategy" (MACD TF (MACD trendfollow)).

FMZ source id: 446542

Source
    https://www.fmz.com/strategy/446542 (PineScript v4, FMZ last modified 2024-03-29 15:14:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 121-200), MACD 3 / 9 / 5; dates 2002-2029 (window() always true)
    macd > signal and macd > 0 -> entry long;  macd < signal -> close long;  macd < signal and macd < 0 -> entry short;  macd > signal -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are levels, so a repeated entry while already on that side is ignored. A close after
      the opposite entry on the same bar leaves the reversal (the long close comes before the short
      entry: together they are one reversal). REVERSAL INTENDED. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD signal and zero-line state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_446542_macd3_9_5_signal_zero_state_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [3, 12],
    "slow": [9, 26],
}
DEFAULT_PARAMS = {"fast": 3, "slow": 9, "signal": 5}


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
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    le = (macd > sig) & (macd > 0)
    se = (macd < sig) & (macd < 0)
    lx = (macd < sig) & ~se
    sx = (macd > sig) & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
