"""Bollinger 10 / 2 band re-entries, broker days: the close crossing back over the lower band goes long, back under the upper band goes short; a long whose high touches the upper band closes, a short whose low touches the lower band closes; reversing.
Port of FMZ strategy #483048 "基于Bollinger带策略应用的动态出场交易系统-Dynamic-Exit-Trading-System-Based-on-Bollinger-Bands-Application" (Bollinger Strategy: Close at Band Touch v6).

FMZ source id: 483048

Source
    https://www.fmz.com/strategy/483048 (PineScript v6, FMZ last modified 2025-02-27 17:13:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-133), Bollinger 10 x 2.0; capital 1000, 1000 % of equity
    crossover(close, lower) -> entry Long;  crossunder(close, upper) -> entry Short
    long and high >= upper -> close Long;  short and low <= lower -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The touch exits are read on the bar's close (an exit signal filled at the next open), as the
      strategy.close calls are. A close on the bar of an entry is masked by the entry; an entry on the
      other side reverses (REVERSAL INTENDED). The 1000 % of equity size and the capital are sizing.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger band re-entries with band-touch exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1000 % of equity and capital stored, not ported.
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

NAME = "fmz_483048_bb10_2_reentry_opposite_band_touch_exit_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 10, "mult": 2.0}


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
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    upper, lower = basis + float(p["mult"]) * sd, basis - float(p["mult"]) * sd
    le = (c > lower) & (c.shift(1) <= lower.shift(1))
    se = (c < upper) & (c.shift(1) >= upper.shift(1))
    lx = h >= upper
    sx = lo <= lower
    return le & ~se, lx & ~le & ~se, se, sx & ~se & ~le


def portfolio_kwargs(**params):
    return {}
