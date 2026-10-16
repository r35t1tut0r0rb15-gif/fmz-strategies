"""MACD cross, long only, broker days: the MACD crossing above its signal goes long, crossing below closes the
long (the source's per-bar tick bracket is described, not emitted).
Port of FMZ strategy #429385 "MACD动量策略MACD-Momentum-Strategy" (MACD Momentum Strategy).

FMZ source id: 429385

Source
    https://www.fmz.com/strategy/429385 (PineScript v5, FMZ last modified 2023-10-16 15:57:34).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 119-138), MACD 12 / 26 / 9
    crossover(macd, signal) -> entry long; crossunder(macd, signal) -> close long
    every bar: exit(loss = lowest(low, 1), profit = highest(high, 3))   (price levels passed as tick counts)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy.exit passes price levels (the bar's low, the 3-bar high) as tick distances, so
      the stop and target sit about low x mintick / high x mintick away (roughly 10 % of the price for a
      0.1 tick at BTC prices), re-issued with new values on every bar: an instrument-specific, moving
      bracket that stops() cannot express (rules 2 and criterion 2). Not emitted; mark
      trailing_stop_pending, described in PORT_NOTES.
    * Long only. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving tick bracket is not emitted (rule 2).
    2 generic: PASS, MACD crosses only (the tick bracket is not ported).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket is quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_429385_macd_cross_long"
FAMILY = "macd_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 50],
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
    e = lambda x, n: x.ewm(span=int(n), adjust=False).mean()  # noqa: E731
    macd = e(c, p["fast"]) - e(c, p["slow"])
    sig = e(macd, p["signal"])
    long_e = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).astype(bool)
    long_x = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
