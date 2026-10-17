"""The close and the SMA 2 crossing the SMA 4 together, always in, daily bars: both crossing above goes long, both
below goes short.
Port of FMZ strategy #482800 "多重移动平均线交叉趋势捕捉策略-Multiple-Moving-Average-Crossover-Trend-Capture-Strategy" (1/2/4 Moving Average STR 1.0.0).

FMZ source id: 482800

Source
    https://www.fmz.com/strategy/482800 (PineScript v6, FMZ last modified 2025-02-20 11:31:18).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 93-130), SMA 1 / 2 / 4
    buy = crossover(sma1, sma4) and crossover(sma2, sma4) -> entry long, close short
    sell = crossunder(sma1, sma4) and crossunder(sma2, sma4) -> close long, entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * SMA 1 is the close. The closes repeat the reversal the entries make (the long close runs before the short
      entry and acts on the held long, the same result); always in (REVERSAL INTENDED).
    * Signal module, no stops. Daily bars are broker days (17:00 America/New_York), stamped with their first minute;
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, short SMAs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482800_sma1_2_cross_sma4_always_in"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "t_len": [2, 3],
    "f_len": [4, 8],
}
DEFAULT_PARAMS = {"o_len": 1, "t_len": 2, "f_len": 4}


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
    o, t, f = (c.rolling(int(p[k])).mean() for k in ("o_len", "t_len", "f_len"))

    def xover(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    long_e = (xover(o, f) & xover(t, f)).astype(bool)
    short_e = (xover(f, o) & xover(f, t)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
