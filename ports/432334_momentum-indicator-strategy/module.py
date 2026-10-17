"""MACD 12 / 26 / 9 signal crosses, broker days: the MACD crossing above its signal goes long, crossing below goes short;
always in once started.
Port of FMZ strategy #432334 "Momentum Indicator Strategy" (MACD Backtesting).

FMZ source id: 432334

Source
    https://www.fmz.com/strategy/432334 (PineScript v3, FMZ last modified 2023-11-16 15:47:13).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 152-180), MACD 12 / 26 / 9 (EMA)
    crossover(macd, signal) -> entry long;  crossunder(macd, signal) -> entry short
    exit("Close Long Trigger" / "Close Short Trigger") with no levels on the same crosses

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit calls carry no price or tick levels, so they place no order (as #429564); the
      positions change by the opposite entry. pyramiding 3 is sizing (crosses alternate, so no add
      occurs). strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, pyramiding 3 and the commission stored in original_sizing.txt.
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

NAME = "fmz_432334_macd_signal_cross"
FAMILY = "macd_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 17],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


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
    le = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).astype(bool)
    se = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
