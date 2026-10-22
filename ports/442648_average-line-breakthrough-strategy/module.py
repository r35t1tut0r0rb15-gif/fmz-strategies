"""Bollinger-style band re-entries, daily bars: the close crossing back over the lower band (SMA 50 +- 2 deviations) goes long, crossing under the upper band goes short; the stops set at the latest SMA
crossing are described and kept pending; reversing.
Port of FMZ strategy #442648 "Average Line Breakthrough Strategy" (Standard Deviation Bands with Buy/Sell Signals).

FMZ source id: 442648

Source
    https://www.fmz.com/strategy/442648 (PineScript v5, FMZ last modified 2024-02-23 14:46:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 138-197), SMA 50; deviation x 2; stop 12 %
    crossover(close, lower) -> entry Buy;  crossunder(close, upper) -> entry Sell
    crossover(close, sma) -> stopLossBuy = close (1 - 12 %);  crossunder(close, sma) -> stopLossSell = close (1 + 12 %);  exit(Buy, stop = stopLossBuy);  exit(Sell, stop = stopLossSell)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stops are price levels re-set whenever the close crosses the SMA, usually after the entry and
      again during a trade, not at entry: a level moving with later events, which the house stops cannot
      express, so they are described here and kept pending (mark trailing_stop_pending, as #438034).
      Positions end at the opposite entry until then. Pine's stdev is the population deviation.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the event-set stops described (pending).
    2 generic: PASS, band re-entries.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_442648_sd_band_reentry_reversal_pending_stops"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 20],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 50, "mult": 2.0}


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
    n = int(p["length"])
    sma = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, dn = sma + dev, sma - dev
    le = (c > dn) & (c.shift(1) <= dn.shift(1))
    se = (c < up) & (c.shift(1) >= up.shift(1))
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
