"""Pullback "reactions" to a composite EMA 25, always in the market, daily (broker-day) bars: above the EMA, a bar
whose low dips 0.5 % below it and closes back above goes long; below the EMA, a bar whose high pokes 0.5 % above it and
closes back below goes short.
Port of FMZ strategy #482906 "复合趋势均线反转交易策略-Composite-Trend-Moving-Average-Reversal-Trading-Strategy" (Ultrajante MA Reaction Strategy).

FMZ source id: 482906

Source
    https://www.fmz.com/strategy/482906 (PineScript v5, FMZ last modified 2025-02-27 17:23:21).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 94-157), MA type EMA, periods 20 / 30 averaged (25), reaction 0.5 %
    up = close > ma and low <= ma x 0.995: close short, entry long; down = close < ma and high >= ma x 1.005: mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The composite period is round((20 + 30) / 2) = 25 ("Average"); the MA type EMA (default). close + entry is a
      reversal: only the entries are emitted (REVERSAL INTENDED); no exits, no stops.
    * Daily bars are broker days (17:00 America/New_York) stamped with their first minute (as #430984). FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a moving average and a percentage band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_482906_composite_ema_reaction_reversal_1d"
FAMILY = "ma_pullback"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "comp_period": [25, 50],
    "reaction_pct": [0.5, 1.0],
}
DEFAULT_PARAMS = {"comp_period": 25, "reaction_pct": 0.5}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ma = c.ewm(span=int(p["comp_period"]), adjust=False).mean()
    k = p["reaction_pct"] / 100
    long_e = ((c > ma) & (lo <= ma * (1 - k))).astype(bool)
    short_e = ((c < ma) & (h >= ma * (1 + k))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
