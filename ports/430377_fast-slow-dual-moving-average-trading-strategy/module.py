"""SMA 3 / 9 cross, broker days, long only (the default direction): the fast SMA crossing above the slow goes long,
crossing below closes it.
Port of FMZ strategy #430377 "Fast Slow Dual Moving Average Trading Strategy" (SMA Strategy).

FMZ source id: 430377

Source
    https://www.fmz.com/strategy/430377 (PineScript v4, FMZ last modified 2023-10-27 16:41:24).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 183-250), SMA 3 / 9, long only on, short only / swap / stops off
    crossover(sma(close, 3), sma(close, 9)) -> entry long;  crossunder -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Defaults: "Long only" on; "Short only", order swapping, the initial stop and the trailing stop
      are options (off), not ported. The 2021 start / finish inputs are unused (time_cond = true).
    * Long only; Opposite entries cannot occur. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity per entry stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND429389 (2 members, best partner #429389, Jaccard 0.667); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430377_sma3_9_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [3, 5],
    "slow": [9, 20],
}
DEFAULT_PARAMS = {"fast": 3, "slow": 9}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    xo = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    xu = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return xo, xu, false, false.copy()


def portfolio_kwargs(**params):
    return {}
