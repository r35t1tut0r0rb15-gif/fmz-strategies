"""SMA 13 / SMA 5 crosses, always in, broker days: SMA 13 crossing above SMA 5 goes long, crossing below goes short (the
source's bracket exits never attach, so the trades only reverse).
Port of FMZ strategy #489285 "智能交易动量均线混合策略-Smart-Trading-Momentum-and-Moving-Average-Hybrid-Strategy" (Smart Trade By Amit Roy).

FMZ source id: 489285

Source
    https://www.fmz.com/strategy/489285 (PineScript v5, FMZ last modified 2025-04-03 10:42:22).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 160-228), "fast" SMA 13, "slow" SMA 5
    long = crossover(sma13, sma5) -> entry long (id in Hindi);  short = crossunder(sma13, sma5) -> entry short
    exit("Take Profit", from_entry = "Long" / "Short", ...) with a 1.5 ATR stop and a 3 R target

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits name from_entry "Long" / "Short", but the entries are named in Hindi, so the exits bind to no
      position and never fire: inert, as written (not emitted). The trades only reverse (REVERSAL INTENDED).
    * The candle patterns and the SMA 22 marks are drawn only. The risk-based quantity is sizing.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 3 %-risk quantity and the inert bracket quoted in original_sizing.txt.
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

NAME = "fmz_489285_sma_13_5_cross_always_in"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [13, 20],
    "slow": [5, 8],
}
DEFAULT_PARAMS = {"fast": 13, "slow": 5}


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
    up = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
